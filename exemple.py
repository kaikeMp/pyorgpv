import os
from PyPV.utils import (
    read_and_process_data,
    interpolate_iv_curve,
    get_jsc,
    get_voc,
    calculate_ff,
    calculate_pce,
    calculate_resistances_from_iv,
)

# Defina o caminho para o arquivo de dados
path = r'C:\Users\kaike3500709\OneDrive\Documenten\Academicos\novas-referencias\pce-calculation\Lib\tests'
file = 'curveData_03.txt'
file = 'B2C4_new (1).txt'
filename = os.path.join(path, file)

# Especifique os nomes das colunas e unidades conforme o seu arquivo
voltage_col_name = '[Volt (V)]'
current_col_name = '[Current (mA)]'
voltage_unit = 'V'        # ou 'mV'
current_unit = 'A'       # ou 'A', 'A/cm2', 'mA/cm2'
area = 0.01               # em cm², se necessário

# Leia e processe os dados
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

# Interpole os dados de corrente para Rs e Rsh
interpolated_current = interpolate_iv_curve(voltage, current_mA, label='Current (mA)', plot=False)

# Interpole os dados de densidade de corrente para Jsc, Voc, FF e PCE
interpolated_current_density = interpolate_iv_curve(voltage, current_density_mA_cm2, label='Current Density (mA/cm²)', plot=True)

# Calcule Jsc e Voc
jsc = get_jsc(interpolated_current_density)
voc = get_voc(interpolated_current_density)

# Calcule FF e PCE
ff = calculate_ff(interpolated_current_density, jsc, voc)
pce = calculate_pce(ff, voc, jsc)

# Calcule Rs e Rsh
Rs, Rsh = calculate_resistances_from_iv(interpolated_current, high_voltage_limit=voc*0.9)

print(f"Jsc: {abs(jsc):.2f} mA/cm²")
print(f"Voc: {voc:.2f} V")
print(f"FF: {ff*100:.2f} %")
print(f"PCE: {pce:.2f} %")
print(f"Rs: {Rs:.2f} Ω")
print(f"Rsh: {Rsh:.2f} Ω")
