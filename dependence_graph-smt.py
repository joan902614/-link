from sympy import symbols, Eq, solve
from z3 import Real, Solver

# === Parameter Node 定義 ===
class ParameterNode:
    def __init__(self, parameter):
        self.parameter = parameter  # str
        self.relations = []   # list of Equation
        self.constraints = []  # list of Ineqution
        self.can_self_config = None  # bool
        self.configs = []  # list of Ineqution

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

# === 單一公式類 ===
class Math:
    def __init__(self, expression_strs=None):
        self._expression_strs = expression_strs or [] # list of str
    
    def getExpr(self):
        return self._expression_strs

class Ineqution(Math):
    def __init__(self, name, expression_strs, ineq_type=None):
        self.name = name  # str
        self.type = ineq_type   # str: "Assumption", "Provide", "None"(inner type config)
        super().__init__(expression_strs)
    
    def get_type(self):
        return self.type
    
class Equation(Math):
    def __init__(self, output, inputs, expression_str):
        self.output = output      # str
        self.inputs = inputs      # list of str
        super().__init__([expression_str])


# === parameter dependence graph ===
class ParameterGraph:
    def __init__(self):
        self.nodes = {}  # key: parameter name, value: ParameterNode

    def add_equation(self, eq: Equation):
        # add rhs
        if eq.output not in self.nodes:
            self.nodes[eq.output] = ParameterNode(eq.output)
        self.nodes[eq.output].add_relation(eq)

        # add lhs
        for i in eq.inputs:
            if i not in self.nodes:
                self.nodes[i] = ParameterNode(i)

    def add_port_type(self, ineq: Ineqution):
        if ineq.name not in self.nodes:
            self.nodes[ineq.name] = ParameterNode(ineq.name)
        self.nodes[ineq.name].setPortTypeNotConnect(ineq)

    def add_self_config(self, configs: Ineqution):
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
    '''
    base_eq: sympy eqution

    use sympy to generate equtions of rhs with different parameter 
    
    return: list of Equtions
    '''
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
        self.graph = graph
        self.used_math = []
        self.used_config = []
        self.used_para = set()
        self.can_config = True

    def explore(self, start_param):
        self.used_math = []
        self.used_para = set()
        self.can_config = True
        self._dfs(start_param)

    def _dfs(self, param):
        if param in self.used_para:
            return
        
        print(f"🔍 Visiting: {param}")  # <== 加這行
        self.used_para.add(param)

        # can config?   
        if self.graph[param].get_can_self_config():
            for ineq in self.graph[param].configs:
                self.used_config.append(param)
                   
        # is port type and be assigned
        for con in self.graph[param].get_constraints():     
            if con.get_AP_type == "Provide":
                self.can_config = False
                return
        
        # # has dependence or assumption
        # inequtions = self.graph.get_para_inequations(param)
        # for ineq in inequtions:
        #     if ineq in self.used_math:
        #         continue
        #     self.used_math.append(ineq)
        #     print(ineq.getExpr())

        equations = self.graph.get_para_equations(param)
        for eq in equations:
            if eq in self.used_math:
                continue
            self.used_math.append(eq)
            print(eq.getExpr())
            for i in eq.inputs:
                self._dfs(i)
        
# === SMT 解算器 ===
def check_constraints_with_z3(graph: ParameterGraph, used_math: list):
    '''
    '''
    solver = Solver()
    z3_vars = {}

    def get_var(name):
        if name not in z3_vars:
            z3_vars[name] = Real(name)
        return z3_vars[name]

    for math in used_math:
        if isinstance(math, Ineqution):
            for ineq in math.getExpr():
                try:
                    z3_expr = eval(ineq, {}, {math.name: get_var(math.name)})
                    solver.add(z3_expr)
                except Exception as e:
                    print(f"⚠️ 解析公式錯誤: {ineq} -> {e}")
        elif isinstance(math, Equation):
            try:
                expr = math.getExpr()[0]
                lhs = get_var(math.output)
                rhs = eval(expr.split("=")[1], {}, {v: get_var(v) for v in math.inputs})
                solver.add(lhs == rhs)
            except Exception as e:
                print(f"⚠️ 解析公式錯誤: {expr} -> {e}")


    return solver.check(), solver

# === DOT 圖輸出 ===
def print_dot_graph_parameter_graph(graph: ParameterGraph, highlight_math=[]):
    highlight_math = highlight_math
    highlight_eq_set = set()
    highlight_ineq_set = set()
    highlight_nodes = set()

    for math in highlight_math:
        if isinstance(math, Equation):
            highlight_eq_set.add(math)
            highlight_nodes.add(math.output)
            highlight_nodes.update(math.inputs)
        elif isinstance(math, Ineqution):
            highlight_ineq_set.add(math)
            highlight_nodes.add(math.name)

    print("\n📊 DOT Graph with Highlighted Paths (No Duplicates):")
    print("digraph G {")
    print("  rankdir=LR;")
    print('  node [shape=box, style=filled, fillcolor="#f0f0f0"];')

    # === 參數節點 ===
    for pname, node in graph.get_all_nodes().items():
        color = "#ffeaaf" if pname in highlight_nodes else "#f0f0f0"
        print(f'  "{pname}" [label="{pname}", fillcolor="{color}"];')

    # === Equation 線條（去重）
    seen_edges = set()
    for node in graph.get_all_nodes().values():
        for eq in node.get_relations():
            for inp in eq.inputs:
                edge_key = (inp, eq.output, eq.getExpr()[0])
                if edge_key in seen_edges:
                    continue
                seen_edges.add(edge_key)
                color = "red" if eq in highlight_eq_set else "black"
                style = "bold" if eq in highlight_eq_set else "solid"
                print(f'  "{inp}" -> "{eq.output}" [label="{eq.getExpr()[0]}", color="{color}", style="{style}"];')


    # === Constraint 節點與線條
    seen_ineqs = set()
    for node in graph.get_all_nodes().values():
        for ineq in node.get_constraints():
            if id(ineq) in seen_ineqs:
                continue
            seen_ineqs.add(id(ineq))
            constraint_node_name = f"constraint_{id(ineq)}"
            constraint_label = "\\n".join(ineq.getExpr())

            highlight = ineq in highlight_ineq_set
            fillcolor = "#ffccee" if highlight else "#dddddd"
            fontcolor = "black"
            edge_color = "purple" if highlight else "gray"
            edge_style = "bold" if highlight else "dashed"

            print(f'  "{constraint_node_name}" [label="{constraint_label}", shape=note, fillcolor="{fillcolor}", style="filled", fontcolor="{fontcolor}"];')
            print(f'  "{constraint_node_name}" -> "{ineq.name}" [color="{edge_color}", style="{edge_style}"];')


    print("}")
    print("--- End ---\n")


# === 測試例子：DAC → Speaker ===
graph = ParameterGraph()

# test
a, b = symbols("a b")
for eq in generate_equations_from_sympy(Eq(a, b)):
    graph.add_equation(eq)
graph.add_ineqution(Ineqution("a", "Assumption", ["1.62 <= a", "a <= 3.3"]))

# DAC:
#   vin_dac:
#       1.62 <= vin_dac <= 3.3 (A)
#   vout_dac:
#       0.92 <= vout_dac <= 2.9 (P)
#       vout_dac = vin_dac - 0.7
#   iout_dac:
#       -0.0001 <= iout_dac <= 0.0001

vin_dac, vout_dac, iout_dac, pout_dac, rout_dac = symbols("vin_dac vout_dac iout_dac pout_dac rout_dac")
for eq in generate_equations_from_sympy(Eq(vout_dac, vin_dac - 0.7)):
    graph.add_equation(eq)

graph.add_port_type(Ineqution("vin_dac", ["1.62 <= vin_dac", "vin_dac <= 3.3"]), "Assumption")
graph.add_port_type(Ineqution("vout_dac", ["0.92 <= vout_dac", "vout_dac <= 2.9"]), "Provide")
graph.add_port_type(Ineqution("iout_dac", ["-0.0001 <= iout_dac", "iout_dac <= 0.0001"]), "Assumption")

# Speaker: 
#   pin_speaker:
#       0 <= pin_speaker <= 2
#   r_speaker:
#       4 <= rin_speaker <= 4
pin_speaker, rin_speaker, iin_speaker, vin_speaker = symbols("pin_speaker rin_speaker iin_speaker vin_speaker")
graph.add_port_type(Ineqution("pin_speaker", ["0 <= pin_speaker", "pin_speaker <= 2"]), "Assumption")
graph.add_port_type(Ineqution("rin_speaker", ["4 <= rin_speaker", "rin_speaker <= 4"]), "Provide")

# DAC → Speaker
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

# # === 測試例子：DAC → AMP → Speaker ===
# graph = ParameterGraph()

# # DAC: vout_dac = vin_dac - 0.7
# vin_dac, vout_dac = symbols("vin_dac vout_dac")
# for eq in generate_equations_from_sympy(Eq(vout_dac, vin_dac - 0.7)):
#     graph.add_equation(eq)

# # AMP: v_amp = gain * vout_dac
# gain, v_amp = symbols("gain v_amp")
# for eq in generate_equations_from_sympy(Eq(v_amp, gain * vout_dac)):
#     graph.add_equation(eq)

# # AMP: i_amp = v_amp / r_amp
# i_amp, r_amp = symbols("i_amp r_amp")
# for eq in generate_equations_from_sympy(Eq(i_amp, v_amp / r_amp)):
#     graph.add_equation(eq)

# # AMP: p_amp = v_amp * i_amp
# p_amp = symbols("p_amp")
# for eq in generate_equations_from_sympy(Eq(p_amp, v_amp * i_amp)):
#     graph.add_equation(eq)

# # Speaker: p_speaker = v_amp^2 / r_speaker
# p_speaker, r_speaker = symbols("p_speaker r_speaker")
# for eq in generate_equations_from_sympy(Eq(p_speaker, v_amp**2 / r_speaker)):
#     graph.add_equation(eq)

# # ➕ Constraints
# graph.add_constraint("i_amp", 0.01, 0.02)
# graph.add_constraint("r_amp", 1000, 1000)
# graph.add_constraint("vin_dac", 1.6, 3.3)
# graph.add_constraint("gain", 5, 20)

# 🧠 探索與求解
explorer = DependencyExplorer(graph)
explorer.explore("pin_speaker")
if not explorer.can_config:
    print("  ❌ 不可行，此 constraint 組合矛盾")
used_math = explorer.used_math
result, solver = check_constraints_with_z3(graph, used_math)

# 🧾 結果顯示
print("\n✅ 使用到的公式 / 約束：")
for math in used_math:
    if isinstance(math, Equation):
        print(f" - 【公式】{math.getExpr()}")
    elif isinstance(math, Ineqution):
        for expr in math.getExpr():
            print(f" - 【約束】{expr}")


print(f"\n📊 SMT 結果: {result}")
if str(result) == "sat":
    print("  ✅ 可行！模型如下：")
    model = solver.model()
    for d in model.decls():
        print(f"   - {d.name()} = {model[d]}")
else:
    print("  ❌ 不可行，此 constraint 組合矛盾")


print_dot_graph_parameter_graph(graph, highlight_math=used_math)