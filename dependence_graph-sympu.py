# 公式存放都先用 string
from sympy import symbols, Eq, solve, Interval, And, Symbol, solveset, sympify
from itertools import product

# === Parameter Node Class ===
class ParameterNode:
    def __init__(self, parameter):
        self.parameter = parameter  # str
        self.relations = []         # list of Equation
        self.constraints = []       # list of Inequation
        self.can_self_config = None # bool
        self.configs = []           # list of Ineqution

    def setPortTypeNotConnected(self, constraint):
        self.can_self_config = True
        self.configs.append(constraint)

    def setInnerTypeCanConfig(self, configs):
        self.can_self_config = True
        self.configs.extend(configs)

    def add_relation(self, relation):
        self.relations.append(relation)

    def add_constraint(self, constraint):
        self.constraints.append(constraint)
    
    def get_relations(self):
        return self.relations
    
    def get_constraints(self):
        return self.constraints

    def get_can_self_config(self):
        return self.can_self_config

# === Single Math Formula Class ===
class Math:
    def __init__(self, expression_strs=None):
        self._expression_strs = expression_strs or []  # list of str
    
    def getExpr(self):
        return self._expression_strs

class Inequation(Math):
    def __init__(self, name, expression_strs, ineq_type=None):
        self.name = name        # str
        self.type = ineq_type   # str: "Assumption", "Provide", "None" (inner type config)
        super().__init__(expression_strs)
    
    def get_type(self):
        return self.type

class Equation(Math):
    def __init__(self, output, inputs, expression_str):
        self.output = output    # str
        self.inputs = inputs    # list of str
        super().__init__([expression_str])

# === Parameter Dependence Graph ===
class ParameterGraph:
    def __init__(self):
        self.nodes = {}  # dict -> key: str(parameter name), value: ParameterNode

    def add_equation(self, eq: Equation):
        # rhs
        if eq.output not in self.nodes:
            self.nodes[eq.output] = ParameterNode(eq.output)
        self.nodes[eq.output].add_relation(eq)
        # lhs
        for i in eq.inputs:
            if i not in self.nodes:
                self.nodes[i] = ParameterNode(i)

    def add_port_type(self, ineq: Inequation):
        if ineq.name not in self.nodes:
            self.nodes[ineq.name] = ParameterNode(ineq.name)
        self.nodes[ineq.name].setPortTypeNotConnected(ineq)

    def add_self_config(self, configs: Inequation):
        if configs[0].name not in self.nodes:
            self.nodes[configs[0].name] = ParameterNode(configs[0].name)
        self.nodes[configs[0].name].setInnerTypeCanConfig(configs)

    def get_para_equations(self, param):
        if param not in self.nodes:
            return []
        return self.nodes[param].get_relations()
    
    def get_para_inequations(self, param):
        if param not in self.nodes:
            return []
        return self.nodes[param].get_constraints()

    def get_all_nodes(self):
        return self.nodes

def generate_equations_from_sympy(base_eq):
    """
    base_eq: sympy Eq

    use sympy to generate every parameter direction equation 
    
    return: list of equations
    """
    all_vars = list(base_eq.free_symbols)
    results = []
    for target in all_vars:
        transfer = solve(base_eq, target)
        if transfer:
            rhs = transfer[0]
            inputs = [str(v) for v in rhs.free_symbols]
            results.append(Equation(str(target), inputs, f"{str(target)} = {str(rhs)}"))
    return results

# === 依賴探索器 ===
class DependencyExplorer:
    def __init__(self, graph: ParameterGraph):
        self.graph = graph      # ParameterGraph
        self.used_math = []     # list of Equation
        self.used_config = []   # list of str(parameter name)
        self.used_para = set()  # set of str(parameter name)
        self.can_config = True  # bool(this path can do config)

    def explore(self, start_param):
        self.used_math = []
        self.used_para = set()
        self.can_config = True
        self._dfs(start_param)

    def _dfs(self, param):
        if param in self.used_para:
            return
        
        print(f"🔍 Visiting: {param}")
        self.used_para.add(param)
        
        if self.graph.nodes[param].get_can_self_config():
            if param not in self.used_config:
                self.used_config.append(param)
       
        equations = self.graph.get_para_equations(param)
        for eq in equations:
            if eq not in self.used_math:
                self.used_math.append(eq)
                print(eq.getExpr())
                for i in eq.inputs:
                    self._dfs(i)

# === 新增部分：用 Sympy 處理 config 範圍 ===
# def parse_inequation(ineq: Inequation):
#     sym = Symbol(ineq.name)
#     exprs = []
#     for expr in ineq.getExpr():
#         try:
#             exprs.append(sympify(expr, locals={ineq.name: sym}))
#         except Exception as e:
#             print(f"解析不等式錯誤: {expr} -> {e}")
#     return And(*exprs)

# def parse_equation(eq: Equation):
#     expr_str = eq.getExpr()[0]  # 只取第一個表達式，因為 Equation 預設一條式子
#     lhs_str, rhs_str = expr_str.split("=")
#     lhs_str = lhs_str.strip()
#     rhs_str = rhs_str.strip()
    
#     symbols = {name: Symbol(name) for name in [eq.output] + eq.inputs}

#     try:
#         # 轉成 sympy 表達式
#         lhs = sympify(lhs_str, locals=symbols)
#         rhs = sympify(rhs_str, locals=symbols)

#         return Eq(lhs, rhs)
    
#     except Exception as e:
#         print(f"解析等式錯誤: {expr_str} -> {e}")
#         return None

# def select_config(source_var: str, guarantee: Inequation, used_math, used_config: dict):
#     from sympy import Rel,satisfiable

#     def is_strictly_true(expr):
#         # 如果是 sympy 的邏輯判斷式，試著化簡判斷
#         if isinstance(expr, Rel):
#             return expr.simplify() == True
#         # 如果是 bool 值 True 就回傳
#         if expr == True:
#             return True
#         return False  # 其他都當作不確定（不是 true）
#     '''
#     guarantee: assumption require provide
#     used_math: list of Equtions
#     used_config: dict(key: parameter str, value: list of Ineqitions)
#     '''
#     # transfer all eqution from string to sympy
#     sympy_eqs = []
#     for eq in used_math:
#         sympy_eqs.append(parse_equation(eq))

#     # transfer all eqution from string to sympy
#     sympy_all_configs = []
#     for configs in config_candidates.values():
#         sympy_all_configs.append([parse_inequation(ineq) for ineq in configs])
    
#     # tansfer guarantee
#     sympy_guarantee = parse_inequation(guarantee)

#     # solve
#     solutions = solve(sympy_eqs, dict=True)
#     print(solutions)
#     # match
#     for sympy_configs in product(*sympy_all_configs):
#         # sympy_configs sympy_guarantee
#         # 1. 將 config 條件 + guarantee 條件合併
#         all_constraints = list(sympy_configs) + [sympy_guarantee]

#         # 2. 嘗試解聯立等式，給定這些條件
#         # 使用 sympy 的解法器
        

#         # 3. 篩選符合 config 限制與 guarantee 的解
#         valid_solutions = []
#         for sol in solutions:
#             # if all(constraint.subs(sol) for constraint in all_constraints):
#             #     valid_solutions.append(list(sympy_configs))
#             if all(is_strictly_true(constraint.subs(sol)) for constraint in all_constraints):
#                 valid_solutions.append(list(sympy_configs))

#         if valid_solutions:
#             print("找到符合條件的解：", valid_solutions)
#         else:
#             print("這組 config 沒有符合條件的解")
#     return valid_solutions
from z3 import Real, Optimize, sat

def select_config(target_var: str, guarantee: Inequation, used_math, used_config: dict):
    """
    依照 target 條件反推，檢查每個 config 的實際需求範圍是否落在定義範圍中。
    """

    # 工具函數：解析定義的上下界
    def extract_defined_range(expr_list: list[str], param_name: str):
        min_val = None
        max_val = None
        for expr in expr_list:
            expr = expr.replace(" ", "")
            if "<=" in expr:
                parts = expr.split("<=")
                if len(parts) == 2:
                    if parts[1] == param_name:
                        min_val = float(parts[0])
                    elif parts[0] == param_name:
                        max_val = float(parts[1])
                elif len(parts) == 3:
                    # 例如 "1.62<=vin_dac<=3.3"
                    min_val = float(parts[0])
                    max_val = float(parts[2])
        return min_val, max_val

    # === 1. 收集所有變數
    all_vars = set()
    for eq in used_math:
        all_vars.add(eq.output)
        all_vars.update(eq.inputs)
    all_vars.add(guarantee.name)
    for config_list in used_config.values():
        for ineq in config_list:
            all_vars.add(ineq.name)

    z3_vars = {var: Real(var) for var in all_vars}

    # === 2. 組 base constraints（等式 + config 限制 + target 限制）
    base_constraints = []

    for eq in used_math:
        expr_str = eq.getExpr()[0]
        lhs_str, rhs_str = expr_str.split("=")
        lhs = sympify(lhs_str.strip(), locals=z3_vars)
        rhs = sympify(rhs_str.strip(), locals=z3_vars)
        base_constraints.append(lhs == rhs)

    for config_list in used_config.values():
        for ineq in config_list:
            for expr in ineq.getExpr():
                base_constraints.append(sympify(expr, locals=z3_vars))

    for expr in guarantee.getExpr():
        base_constraints.append(sympify(expr, locals=z3_vars))

    # === 3. 開始反推每個 config 的範圍
    result = {}

    for config_param in used_config.keys():
        var = z3_vars[config_param]

        # 找最小值
        opt = Optimize()
        opt.set("timeout", 5000)  # 5000 毫秒，即 5 秒
        opt.add(*base_constraints)
        h_min = opt.minimize(var)
        min_val = None
        check_result = opt.check()
        print(f"🧪 {config_param} 最小化 check 結果: {check_result}")
        if check_result == sat:
            model = opt.model()
            min_val = float(model.eval(var).as_decimal(10))

        # 找最大值
        opt = Optimize()
        opt.set("timeout", 5000)  # 5000 毫秒，即 5 秒
        opt.add(*base_constraints)
        h_max = opt.maximize(var)
        max_val = None
        check_result = opt.check()
        print(f"🧪 {config_param} 最大化 check 結果: {check_result}")
        if check_result == sat:
            model = opt.model()
            max_val = float(model.eval(var).as_decimal(10))


        # 抓原本 config 限制範圍（用字串分析）
        all_exprs = [expr for ineq in used_config[config_param] for expr in ineq.getExpr()]
        defined_min, defined_max = extract_defined_range(all_exprs, config_param)

        # 判斷是否合法
        valid = True
        if min_val is not None and defined_min is not None and min_val < defined_min - 1e-8:
            valid = False
        if max_val is not None and defined_max is not None and max_val > defined_max + 1e-8:
            valid = False

        result[config_param] = {
            "required_range": (min_val, max_val),
            "defined_range": (defined_min, defined_max),
            "valid": valid
        }

    # === 4. 輸出報告
    print("\n📊 [推導回來的 config 範圍 VS 原始定義]")
    for param, info in result.items():
        r_min, r_max = info['required_range']
        d_min, d_max = info['defined_range']
        print(f"🔧 {param}:")
        print(f"  - 推導需求: ({r_min}, {r_max})")
        print(f"  - 原始定義: ({d_min}, {d_max})")
        print(f"  - ✅ 合法？→ {'✅ YES' if info['valid'] else '❌ NO'}")
    return result


# === DOT graph ===
def print_dot_graph_parameter_graph(graph: ParameterGraph, highlight_math=[]):
    highlight_eq_keys = set()
    highlight_ineq_keys = set()
    highlight_nodes = set()

    for math in highlight_math:
        if isinstance(math, Equation):
            expr = math.getExpr()[0]
            highlight_eq_keys.add(expr)
            highlight_nodes.add(math.output)
            highlight_nodes.update(math.inputs)
        elif isinstance(math, Inequation):
            for expr in math.getExpr():
                highlight_ineq_keys.add(expr)
            highlight_nodes.add(math.name)

    print("\n📊 DOT Graph with Highlighted Paths (No Duplicates):")
    print("digraph G {")
    print("  rankdir=LR;")
    print('  node [shape=box, style=filled, fillcolor="#f0f0f0"];')

    # === 節點
    for pname, node in graph.get_all_nodes().items():
        color = "#ffeaaf" if pname in highlight_nodes else "#f0f0f0"
        print(f'  "{pname}" [label="{pname}", fillcolor="{color}"];')

    # === Equation 邊（去重）
    seen_edges = set()
    for node in graph.get_all_nodes().values():
        for eq in node.get_relations():
            expr = eq.getExpr()[0]
            for inp in eq.inputs:
                edge_key = (inp, eq.output, expr)
                if edge_key in seen_edges:
                    continue
                seen_edges.add(edge_key)
                color = "red" if expr in highlight_eq_keys else "black"
                style = "bold" if expr in highlight_eq_keys else "solid"
                print(f'  "{inp}" -> "{eq.output}" [label="{expr}", color="{color}", style="{style}"];')

    # === Constraint（Inequation）節點與邊（去重）
    seen_ineqs = set()
    seen_ineq_edges = set()
    for node in graph.get_all_nodes().values():
        for ineq in node.get_constraints() + node.configs:
            ineq_id = id(ineq)
            if ineq_id in seen_ineqs:
                continue
            seen_ineqs.add(ineq_id)

            # 只顯示一條代表性不等式
            ineq_type = ineq.get_type() or "None"
            example_expr = ineq.getExpr()[0]
            constraint_label = f"{ineq_type}: {example_expr}"

            # 根據類型決定顏色
            if ineq_type == "Provide":
                fillcolor = "#c8facc"  # 淡綠
            elif ineq_type == "Assumption":
                fillcolor = "#cce5ff"  # 淡藍
            else:
                fillcolor = "#dddddd"  # 灰

            constraint_node_name = f"constraint_{ineq_id}"
            print(f'  "{constraint_node_name}" [label="{constraint_label}", shape=note, fillcolor="{fillcolor}", style="filled", fontcolor="black"];')

            # 只連一次邊：constraint → variable
            edge_key = (constraint_node_name, ineq.name)
            if edge_key not in seen_ineq_edges:
                seen_ineq_edges.add(edge_key)
                print(f'  "{constraint_node_name}" -> "{ineq.name}" [color="gray", style="dashed"];')

    print("}")
    print("--- End ---\n")



# === 主流程：DAC → Speaker 範例 ===
graph = ParameterGraph()

# test: 加入簡單等式 a = b 與 a 的約束 (白色節點)
a, b = symbols("a b")
for eq in generate_equations_from_sympy(Eq(a, b)):
    graph.add_equation(eq)
graph.nodes["a"].add_constraint(Inequation("a", ["1.62 <= a", "a <= 3.3"], "Assumption"))

# DAC 部分:
vin_dac, vout_dac, iout_dac, pout_dac, rout_dac = symbols("vin_dac vout_dac iout_dac pout_dac rout_dac")
for eq in generate_equations_from_sympy(Eq(vout_dac, vin_dac - 0.7)):
    graph.add_equation(eq)
graph.add_port_type(Inequation("vin_dac", ["2.0<= vin_dac", "vin_dac <= 3.3"], "Assumption"))
graph.add_port_type(Inequation("vout_dac", ["1.2 <= vout_dac", "vout_dac <= 3.0"], "Provide"))
graph.add_port_type(Inequation("iout_dac", ["0.01 <= iout_dac", "iout_dac <= 0.02"], "Assumption"))

# Speaker 部分:
pin_speaker, rin_speaker, iin_speaker, vin_speaker = symbols("pin_speaker rin_speaker iin_speaker vin_speaker")
# graph.add_port_type(Inequation("pin_speaker", ["0 <= pin_speaker", "pin_speaker <= 2"], ineq_type="Assumption"))
graph.add_port_type(Inequation("rin_speaker", ["125 <= rin_speaker", "rin_speaker <= 125"], "Provide"))

# DAC → Speaker 連接:
for eq in generate_equations_from_sympy(Eq(vout_dac, vin_speaker)):
    graph.add_equation(eq)
for eq in generate_equations_from_sympy(Eq(rout_dac, rin_speaker)):
    graph.add_equation(eq)
for eq in generate_equations_from_sympy(Eq(iout_dac, iin_speaker)):
    graph.add_equation(eq)
for eq in generate_equations_from_sympy(Eq(pout_dac, pin_speaker)):
    graph.add_equation(eq)
for eq in generate_equations_from_sympy(Eq(pout_dac, vout_dac * iout_dac)):
    graph.add_equation(eq)
for eq in generate_equations_from_sympy(Eq(vout_dac, rout_dac * iout_dac)):
    graph.add_equation(eq)
for eq in generate_equations_from_sympy(Eq(pin_speaker, vin_speaker * iin_speaker)):
    graph.add_equation(eq)
for eq in generate_equations_from_sympy(Eq(vin_speaker, rin_speaker * iin_speaker)):
    graph.add_equation(eq)

# 探索 (使用 DFS 收集所有公式與約束)
explorer = DependencyExplorer(graph)
explorer.explore("pin_speaker")
used_math = explorer.used_math

print("\n✅ 使用到的公式 / 約束：")
for math in used_math:
    if isinstance(math, Equation):
        print(f" - 【公式】{math.getExpr()}")
    elif isinstance(math, Inequation):
        for expr in math.getExpr():
            print(f" - 【約束】{expr}")

# 印出 DOT 圖
print_dot_graph_parameter_graph(graph, used_math)

# === 新增部分：根據所有公式和可 config 節點候選範圍，找出能讓 vin_dac 落在目標區間 (3.5, 4.1) 的組合 ===
target_range = Inequation("pin_speaker", ["0.0125 <= pin_speaker", "pin_speaker <= 0.05"])
config_candidates = { p: graph.nodes[p].configs for p in explorer.used_config } # key: used_config parameter str, value: config Ineqition
valid_configs = select_config("vout_dac", target_range, used_math, config_candidates)

