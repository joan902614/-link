import sympy

# DAC constraint
"DAC_voltage <= 3.6"
"DAC_voltage >= 1.62"
"DAC_current <= 1 * 1 / 1000"
"DAC_current >= -1 * 1 / 1000"
# Speaker constraint
"Speaker.power <= 2"
"Speaker.impedense = 4"
or (2W <= Speaker.power <= 4W and Speaker.time == Peak)


# 定義 DAC 相關變數
DAC_voltage, DAC_current, DAC_power, DAC_impedense = symbols('DAC_voltage, DAC_current, DAC_power, DAC_impedense')

# DAC constraint
DAC_voltage_constraints = Interval(1.62, 3.6)
DAC_current_constraints = Interval(-1 * 1 / 1000, 1 * 1 / 1000)
 
# DAC add eq
eq1 = Eq(DAC_voltage, DAC_current * DAC_impedense)
eq2 = Eq(DAC_power, DAC_current * DAC_voltage)

# 定義 Speaker 相關變數
Speaker_voltage, Speaker_current, Speaker_power, Speaker_impedense = symbols('Speaker_voltage Speaker_current Speaker_power Speaker_impedense')

# Speaker constraint
Speaker_power_constraint = Interval(0, 2) # Speaker_impedense_value = 4 * ohm
eq3 = Eq(Speaker_impedense, 4)

# 喇叭 add eq
eq4 = Eq(Speaker_voltage, Speaker_current * Speaker_impedense)
eq5 = Eq(Speaker_power, Speaker_current * Speaker_voltage)

# each other
eq6 = Eq(DAC_impedense, Speaker_impedense)
eq7 = Eq(Speaker_voltage, DAC_voltage)
eq8 = Eq(DAC_voltage, 2)