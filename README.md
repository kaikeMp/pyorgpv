# PyPV

**PyPV** is a Python library for analyzing current-voltage (IV) curves of solar cells. It calculates key parameters from experimental IV data, including:

- **Short-circuit current density (\( J_{sc} \))**
- **Open-circuit voltage (\( V_{oc} \))**
- **Fill Factor (FF)**
- **Power Conversion Efficiency (PCE)**
- **Series resistance (\( R_s \))**
- **Shunt resistance (\( R_{sh} \))**

## Functions in the Library

The library provides the following functions:

### `read_and_process_data`

- **Purpose**: Reads the IV data from a file and processes the voltage and current data according to specified units and cell area.
- **Parameters**:
  - `filename`: Path to the data file.
  - `voltage_col_name`: Name of the voltage column in the file.
  - `current_col_name`: Name of the current column in the file.
  - `voltage_unit`: Unit of the voltage data ('V' or 'mV').
  - `current_unit`: Unit of the current data ('A', 'mA', 'A/cm2', 'mA/cm2').
  - `area`: Cell area in cm² (required if current is per unit area).
  - `delimiter`: Delimiter used in the file (default is ',').
  - `decimal`: Decimal separator used in the file (default is '.').
- **Returns**:
  - `voltage`: Voltage data in volts.
  - `current_mA`: Current data in milliamperes.
  - `current_density_mA_cm2`: Current density data in mA/cm².

### `interpolate_iv_curve`

- **Purpose**: Interpolates the IV curve using a specified interpolation method.
- **Parameters**:
  - `voltage`: Voltage data in volts.
  - `current`: Current data (current or current density).
  - `num_points`: Number of points to interpolate (default is 1500).
  - `kind`: Type of interpolation (default is 'cubic').
  - `plot`: If True, plots the raw and interpolated data.
  - `label`: Label for the current data (e.g., 'Current (mA)', 'Current Density (mA/cm²)').
- **Returns**:
  - `interpolated_df`: DataFrame containing interpolated voltage and current data.

### `get_jsc`

- **Purpose**: Calculates the short-circuit current density (\( J_{sc} \)) at \( V = 0 \).
- **Parameters**:
  - `df`: DataFrame containing interpolated data.
  - `voltage_col`: Name of the voltage column (default is 'Voltage (V)').
  - `current_density_col`: Name of the current density column (default is 'Current Density (mA/cm²)').
- **Returns**:
  - `jsc`: Short-circuit current density in mA/cm².

### `get_voc`

- **Purpose**: Calculates the open-circuit voltage (\( V_{oc} \)) at \( J = 0 \).
- **Parameters**:
  - Same as `get_jsc`.
- **Returns**:
  - `voc`: Open-circuit voltage in volts.

### `calculate_ff`

- **Purpose**: Calculates the Fill Factor (FF) of the solar cell.
- **Parameters**:
  - `df`: DataFrame containing interpolated data.
  - `jsc`: Short-circuit current density in mA/cm².
  - `voc`: Open-circuit voltage in volts.
  - `voltage_col`: Name of the voltage column.
  - `current_density_col`: Name of the current density column.
- **Returns**:
  - `ff`: Fill Factor (unitless, between 0 and 1).

### `calculate_pce`

- **Purpose**: Calculates the Power Conversion Efficiency (PCE) of the solar cell.
- **Parameters**:
  - `ff`: Fill Factor.
  - `voc`: Open-circuit voltage in volts.
  - `jsc`: Short-circuit current density in mA/cm².
  - `incident_power`: Incident light power in mW/cm² (default is 100 mW/cm²).
- **Returns**:
  - `pce`: Power Conversion Efficiency in percentage (%).

### `calculate_resistances_from_iv`

- **Purpose**: Calculates the series resistance (\( R_s \)) and shunt resistance (\( R_{sh} \)) from IV data using linear regression.
- **Parameters**:
  - `df`: DataFrame containing IV data.
  - `voltage_col`: Name of the voltage column (default is 'Voltage (V)').
  - `current_col`: Name of the current column (default is 'Current (mA)').
  - `low_voltage_limit`: Voltage threshold for low-voltage region for \( R_{sh} \) calculation (default is 0.1 V).
  - `high_voltage_limit`: Voltage threshold for high-voltage region for \( R_s \) calculation (default is 0.9 V).
- **Returns**:
  - `Rs`: Series resistance in ohms (Ω).
  - `Rsh`: Shunt resistance in ohms (Ω).

## Example Usage

An example of how to use the library is provided in the `example.py` file included in the folder. The example code demonstrates how to apply the library functions to process IV data and calculate the solar cell parameters.

Below is the code from `example.py`:

```python
import os
from pypv.utils import (
    read_and_process_data,
    interpolate_iv_curve,
    get_jsc,
    get_voc,
    calculate_ff,
    calculate_pce,
    calculate_resistances_from_iv,
)

# Define the path to the data file
path = r'C:\Users\your_username\Documents\SolarCellData'
file = 'curveData_03.txt'
# file = 'B2C4_new (1).txt'  # Alternative file
filename = os.path.join(path, file)

# Specify the column names and units as per your data file
voltage_col_name = '[Volt (V)]'
current_col_name = '[Current (mA)]'
voltage_unit = 'V'        # or 'mV'
current_unit = 'A'        # 'A', 'mA', 'A/cm2', 'mA/cm2'
area = 0.01               # in cm², if necessary

# Read and process the data
voltage, current_mA, current_density_mA_cm2 = read_and_process_data(
    filename,
    voltage_col_name,
    current_col_name,
    voltage_unit=voltage_unit,
    current_unit=current_unit,
    area=area,
    delimiter=',',
    decimal='.',
)

# Interpolate the current data for Rs and Rsh
interpolated_current = interpolate_iv_curve(
    voltage,
    current_mA,
    label='Current (mA)',
    plot=False
)

# Interpolate the current density data for Jsc, Voc, FF, and PCE
interpolated_current_density = interpolate_iv_curve(
    voltage,
    current_density_mA_cm2,
    label='Current Density (mA/cm²)',
    plot=True
)

# Calculate Jsc and Voc
jsc = get_jsc(interpolated_current_density)
voc = get_voc(interpolated_current_density)

# Calculate FF and PCE
ff = calculate_ff(interpolated_current_density, jsc, voc)
pce = calculate_pce(ff, voc, jsc)

# Calculate Rs and Rsh
Rs, Rsh = calculate_resistances_from_iv(
    interpolated_current,
    high_voltage_limit=voc * 0.9
)

# Print the results
print(f"Jsc: {abs(jsc):.2f} mA/cm²")
print(f"Voc: {voc:.2f} V")
print(f"FF: {ff*100:.2f} %")
print(f"PCE: {pce:.2f} %")
print(f"Rs: {Rs:.2f} Ω")
print(f"Rsh: {Rsh:.2f} Ω")
```

**Note**: Replace the `path` variable with the actual path to your data files.

## Test Data Files

There is a `tests` folder containing three IV curve data files you can use to test the library:

- `curveData_01.txt`
- `curveData_02.txt`
- `curveData_03.txt`

Additionally, there is a file called `Parameters.xlsx` that contains the expected parameters for comparison with the outputs from the code. These files can be used for testing and validation.

## License

This project is licensed under the terms of the [MIT License](LICENSE).
---
Author: 
Kaike Rosivan Maia Pacheco
Phisics Ph.D.
e-mail: fisikaike@live.com