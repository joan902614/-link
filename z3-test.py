from z3 import Real, Solver, And, sat

# 定義變數
p = Real('p')
i = Real('i')
v = Real('v')
r = Real('r')

# 建立求解器
s = Solver()

# 加入約束條件
s.add(p == i * v)
s.add(v == i * r)
s.add(p >= 0, p <= 2)
s.add(i >= -0.0001, i <= 0.0001)
s.add(r >= 4, r <= 5)
s.add(v >= 1.62, v <= 3.6)

# 檢查是否有解
if s.check() == sat:
    model = s.model()
    print("✅ 有可行解")
    for var in [p, i, v, r]:
        print(f"{var} = {model[var]}")
else:
    print("❌ 無解，條件矛盾")
