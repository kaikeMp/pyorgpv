import pandas as pd
import numpy as np
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt
from scipy import stats

def read_and_process_data(
    filename,
    voltage_col_name,
    current_col_name,
    voltage_unit='V',
    current_unit='mA',
    area=None,
    delimiter=',',
    decimal='.',
):
    """
    Reads and processes IV data from a file.

    Parameters:
    - filename: str, path to the data file
    - voltage_col_name: str, name of the voltage column in the file
    - current_col_name: str, name of the current column in the file
    - voltage_unit: str, unit of the voltage data ('V' or 'mV')
    - current_unit: str, unit of the current data ('A', 'mA', 'A/cm2', 'mA/cm2')
    - area: float, area in cm^2 (required if current is per unit area)
    - delimiter: str, delimiter used in the file (default is ',')
    - decimal: str, decimal separator used in the file (default is '.')

    Returns:
    - voltage: pandas Series, voltage data in volts
    - current_mA: pandas Series, current data in mA
    - current_density_mA_cm2: pandas Series, current density data in mA/cm^2 (if area is provided)
    """
    # Read the data
    df = pd.read_csv(filename, delimiter=delimiter, decimal=decimal)

    # Extract voltage and current columns
    voltage = df[voltage_col_name]
    current = df[current_col_name]

    # Convert voltage to volts if necessary
    if voltage_unit == 'mV':
        voltage = voltage / 1000  # Convert millivolts to volts
    elif voltage_unit != 'V':
        raise ValueError("Unsupported voltage unit. Use 'V' or 'mV'.")

    # Process current units
    if current_unit == 'A':
        current_mA = current * 1000  # Convert amperes to milliamperes
    elif current_unit == 'mA':
        current_mA = current
    elif current_unit == 'A/cm2':
        if area is None:
            raise ValueError("Area must be specified when using current density units.")
        current_mA = current * area * 1000  # Convert A/cm² to mA
    elif current_unit == 'mA/cm2':
        if area is None:
            raise ValueError("Area must be specified when using current density units.")
        current_mA = current * area  # Convert mA/cm² to mA
    else:
        raise ValueError("Unsupported current unit. Use 'A', 'mA', 'A/cm2', or 'mA/cm2'.")

    # Calculate current density if area is provided
    if area is not None:
        current_density_mA_cm2 = current_mA / area  # mA/cm²
    else:
        current_density_mA_cm2 = None

    return voltage, current_mA, current_density_mA_cm2


def interpolate_iv_curve(voltage, current, num_points=1500, kind='cubic', plot=False, label='Current (mA)'):
    """
    Interpolate the IV curve using the specified interpolation method.

    Parameters:
    - voltage: array-like, voltage data in volts
    - current: array-like, current data (current or current density)
    - num_points: int, number of points to interpolate (default is 1500)
    - kind: str, type of interpolation (default is 'cubic')
    - plot: bool, if True, plot the raw and interpolated data
    - label: str, label for the current data (e.g., 'Current (mA)', 'Current Density (mA/cm²)')

    Returns:
    - interpolated_df: pandas DataFrame, containing interpolated voltage and current data
    """
    # Ensure numpy arrays
    voltage = np.array(voltage)
    current = np.array(current)

    # Sort the data by voltage
    sorted_indices = np.argsort(voltage)
    voltage_sorted = voltage[sorted_indices]
    current_sorted = current[sorted_indices]

    # Remove duplicate voltage values
    voltage_unique, indices = np.unique(voltage_sorted, return_index=True)
    current_unique = current_sorted[indices]

    # Create interpolation function
    interpolation_function = interp1d(voltage_unique, current_unique, kind=kind)

    # Generate interpolated data
    V = np.linspace(voltage_unique.min(), voltage_unique.max(), num_points)
    I = interpolation_function(V)

    # Create DataFrame with interpolated data
    interpolated_df = pd.DataFrame({'Voltage (V)': V, label: I})

    if plot:
        plt.plot(V, I, label='Interpolated Data')
        plt.plot(voltage, current, 'o', label='Raw Data')
        plt.xlabel('Voltage (V)')
        plt.ylabel(label)
        plt.title('IV Curve and Interpolation')
        plt.legend()
        plt.show()

    return interpolated_df

def _interpolate_at_x(df, x_col, y_col, x_target, kind='linear'):
    x = df[x_col]
    y = df[y_col]
    interpolation_function = interp1d(x, y, kind=kind, fill_value="extrapolate")
    return interpolation_function(x_target)

def get_jsc(df, voltage_col='Voltage (V)', current_density_col='Current Density (mA/cm²)'):
    return _interpolate_at_x(df, voltage_col, current_density_col, 0)

def get_voc(df, voltage_col='Voltage (V)', current_density_col='Current Density (mA/cm²)'):
    return _interpolate_at_x(df, current_density_col, voltage_col, 0)

def calculate_ff(df, jsc, voc, voltage_col='Voltage (V)', current_density_col='Current Density (mA/cm²)'):
    """
    Calcula o Fill Factor (FF) de uma célula solar.

    Parâmetros:
    - df: pandas DataFrame contendo os dados interpolados da curva IV.
    - jsc: float, densidade de corrente de curto-circuito (mA/cm²).
    - voc: float, tensão de circuito aberto (V).
    - voltage_col: str, nome da coluna de tensão.
    - current_density_col: str, nome da coluna de densidade de corrente.

    Retorna:
    - ff: float, fator de preenchimento (unitário, entre 0 e 1).
    """
    # Calcula a densidade de potência (P = V * J)
    df['Power Density (mW/cm²)'] = df[voltage_col] * df[current_density_col]
    
    # Filtra o DataFrame para incluir apenas pontos onde V >= 0 e V <= Voc
    filtered_df = df[(df[voltage_col] >= 0) & (df[voltage_col] <= voc)]
    
    # Verifica se o DataFrame filtrado está vazio
    if filtered_df.empty:
        raise ValueError("Nenhum ponto de dados encontrado no intervalo V >= 0 e V <= Voc.")
    
    # Encontra o ponto de máxima potência (MPP) dentro do intervalo especificado
    mpp_row = filtered_df.loc[filtered_df['Power Density (mW/cm²)'].idxmin()]
    v_mp = mpp_row[voltage_col]            # Tensão no MPP
    j_mp = mpp_row[current_density_col]    # Densidade de corrente no MPP

    # Calcula o Fill Factor
    ff = (v_mp * j_mp) / (voc * jsc)
    ff = abs(ff)  # Garante que o FF seja positivo
    return ff


def calculate_pce(ff, voc, jsc, incident_power=100):
    """
    Calculate the Power Conversion Efficiency (PCE) of a solar cell.

    Parameters:
    - ff: float, fill factor (unitless, between 0 and 1)
    - voc: float, open-circuit voltage (V)
    - jsc: float, short-circuit current density (mA/cm²)
    - incident_power: float, the incident light power in mW/cm² (default is 100 mW/cm²)

    Returns:
    - pce: float, power conversion efficiency (percentage)
    """
    # Output power density
    p_out = voc * jsc * ff  # mW/cm²
    # PCE calculation
    pce = abs(p_out / incident_power) * 100  # Percentage
    return pce

def calculate_resistances_from_iv(df, voltage_col='Voltage (V)', current_col='Current (mA)', low_voltage_limit=0.1, high_voltage_limit=0.9):
    """
    Calculate series resistance (Rs) and shunt resistance (Rsh) from IV data using linear regression.

    Parameters:
    - df: pandas DataFrame, containing IV data
    - voltage_col: str, column name for voltage (default is 'Voltage (V)')
    - current_col: str, column name for current (default is 'Current (mA)')
    - low_voltage_limit: float, voltage threshold for low-voltage region for Rsh calculation (default is 0.1 V)
    - high_voltage_limit: float, voltage threshold for high-voltage region for Rs calculation (default is 0.9 V)

    Returns:
    - Rsh: float, shunt resistance (ohms)
    - Rs: float, series resistance (ohms)
    """
    # Extract voltage and current data
    voltage = df[voltage_col]
    current_mA = df[current_col]

    # Convert current from mA to A
    current_A = current_mA / 1000  # Convert mA to A

    # Shunt Resistance (Rsh) Calculation
    low_voltage_mask = voltage < low_voltage_limit
    if not any(low_voltage_mask):
        raise ValueError("No data points found for shunt resistance calculation in the specified voltage range.")
    low_voltage_range = voltage[low_voltage_mask]
    low_current_range_A = current_A[low_voltage_mask]

    # Linear regression for Rsh
    slope_shunt, _, _, _, _ = stats.linregress(low_voltage_range, low_current_range_A)
    Rsh = 1 / slope_shunt  # Shunt resistance

    # Series Resistance (Rs) Calculation
    high_voltage_mask = voltage > high_voltage_limit
    if not any(high_voltage_mask):
        raise ValueError("No data points found for series resistance calculation in the specified voltage range.")
    high_voltage_range = voltage[high_voltage_mask]
    high_current_range_A = current_A[high_voltage_mask]

    # Linear regression for Rs
    slope_series, _, _, _, _ = stats.linregress(high_voltage_range, high_current_range_A)
    Rs = 1 / slope_series  # Series resistance

    return Rs, Rsh

