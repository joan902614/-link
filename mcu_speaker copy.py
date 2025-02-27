# # class dac:
# #     def __init__(self):
# #         self.voltage = 0
# #         self.current = 0
# #         self.impedense = 0
# #         self.power = 0
# # class speaker:
# #     def __init__(self):
# #         self.voltage = 0
# #         self.current = 0
# #         self.impedense = 0
# #         self.power = 0


# milliampere = Unit("milliampere", ampere / 1000)

# DAC_voltage, DAC_current,  DAC_power, DAC_impedense = symbols('DAC_voltage, DAC_current, DAC_power, DAC_impedense')


# -1 * milliampere <= DAC_voltage
# DAC_voltage <= 1 * milliampere 

# DAC_voltage = DAC_current * DAC_impedense
# DAC_power = DAC_current * DAC_voltage

# Speaker_voltage, Speaker_current,  Speaker_power, Speaker_impedense = symbols('Speaker_voltage, Speaker_current, Speaker_power, Speaker_impedense')

# Speaker_impedense = 4 * ohm
# Speaker_power <= 2 * watt

# Speaker_voltage = Speaker_current * Speaker_impedense
# Speaker_power = Speaker_current * Speaker_voltage

# # 找出的 input、output
# DAC_impedense = DAC_input_impedense
# DAC_input_impedense = Speaker_output_impedense 
# Speaker_voltage = Speaker_input_voltage
# Speaker_input_voltage = DAC_output_voltage

from sympy.physics.units import ampere, ohm, volt, watt
from sympy.physics.units.prefixes import milli
from sympy import symbols, Eq, Interval, solve


# 定義 DAC 相關變數
DAC_voltage, DAC_current, DAC_power, DAC_impedense = symbols('DAC_voltage, DAC_current, DAC_power, DAC_impedense')

# DAC constraint
DAC_voltage_constraints = Interval(1.62 * volt, 3.6 * volt)
DAC_current_constraints = Interval(-1 * milli * ampere, 1 * milli * ampere)

# DAC add eq
eq1 = Eq(DAC_voltage, DAC_current * DAC_impedense)
eq2 = Eq(DAC_power, DAC_current * DAC_voltage)

# 定義 Speaker 相關變數
Speaker_voltage, Speaker_current, Speaker_power, Speaker_impedense = symbols('Speaker_voltage Speaker_current Speaker_power Speaker_impedense')

# Speaker constraint
Speaker_power_constraint = Interval(0, 2 * watt) # Speaker_impedense_value = 4 * ohm
eq3 = Eq(Speaker_impedense, 4 * ohm)

# 喇叭 add eq
eq4 = Eq(Speaker_voltage, Speaker_current * Speaker_impedense)
eq5 = Eq(Speaker_power, Speaker_current * Speaker_voltage)

# 解方程組
solution_DAC = solve([eq1, eq2], (DAC_voltage, DAC_power))
solution_Speaker = solve([eq3, eq4, eq5], (Speaker_voltage, Speaker_power))


print("DAC Solution:", solution_DAC)
print("Speaker Solution:", solution_Speaker)