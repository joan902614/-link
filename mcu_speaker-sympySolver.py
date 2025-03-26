import sympy
from sympy.physics.units.prefixes import milli
from sympy import symbols, Eq, Interval, solve, simplify

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
eq8 = Eq(DAC_voltage, 3.6)
# 解方程組
# solution = solve([eq1, eq2, eq3, eq4, eq5])
solution = solve([eq1, eq2, eq3, eq4, eq5, eq6, eq7, eq8])
solution = solution[0]
print("Solution: ", solution)

constraints = [
    DAC_voltage <= 3.6,
    DAC_voltage >= 1.62,
    DAC_current <= 1 * 1 / 1000,
    DAC_current >= -1 * 1 / 1000,
    Speaker_power <= 2,
    Speaker_power >= 0, 
]

# DAC - link - Speaker => DAC_current <= 0.001 → False
# DAC {voltage, impedense}

def simplify_constraints(solution, constraints):
    """
    不斷將 constraints 代入 solution 並嘗試化簡，直到無法進一步簡化
    """
    prev_constraints = constraints  # 初始不等式
    iteration = 1

    while True:
        # print(f"\n🔄 簡化第 {iteration} 輪")
        new_constraints = []

        for ineq in prev_constraints:
            simplified_ineq = simplify(ineq.subs(solution))  # 代入 solution 並化簡

            if isinstance(simplified_ineq, sympy.logic.boolalg.BooleanTrue):
                # print(f"✅ {ineq} → 簡化為 True")
                new_constraints.append(simplified_ineq)
            elif isinstance(simplified_ineq, sympy.logic.boolalg.BooleanFalse):
                # print(f"❌ {ineq} → 簡化為 False")
                new_constraints.append(simplified_ineq)
                # return False  # 如果發現 False，代表這組解不符合
            else:
                # print(f"🔸 {ineq} → {simplified_ineq}（仍為符號）")
                new_constraints.append(simplified_ineq)

        # 如果新約束條件沒有變化，代表化簡完成，停止迴圈
        if new_constraints == prev_constraints:
            break
        
        prev_constraints = new_constraints  # 更新約束條件
        iteration += 1

    return new_constraints  # 返回最簡的不等式組

# 遍歷所有解，進行化簡
simplified_constraints = simplify_constraints(solution, constraints)
print(f"\n🔹 測試 Solution: {solution}")
print("簡化後的約束條件：")
combined_constraints = list(zip(constraints, simplified_constraints))  # 將 constraints 和化簡結果合併
for original, simplified in combined_constraints:
    print(f"🔹 {original} → {simplified}")