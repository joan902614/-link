def findRequire(object, tag):
    """
    
    """
def symbolConvertTag(object, symbol):
    """
    convert object's symbol to object's tag
    """

def findRequireConstraint(object, Require):

def propagateComp(constraint, object1, object2):
    object.constraint = constraint
    object = object1 + object2




def design_interface(object1, object2, link_library):
    """
    object1: 例如 DAC
    object2: 例如 Speaker
    link_library: 候選的中間元件列表 (例如不同型號的放大器)
    """
    
    # Step 1: 嘗試直接連接
    penalty_direct = penalty_direct_connection(object1, object2)
    if penalty_direct == 0:
        return propagateComp(constraint, object1, object2)
    
    # Step 2: 對候選中間元件進行搜尋
    feasible_designs = []
    for linkcomp in link_library:
        # 假設我們有一個函數 build_circuit() 依據拓撲建立電路模型
        circuit_design = build_circuit(object1, linkcomp, object2)
        
        # 評估設計：計算整個電路中的關鍵參數，例如：DAC端電流、load端電壓等
        penalty_total = evaluate_circuit(circuit_design)
        
        # 如果滿足所有硬性限制，則視為一個可行解
        if penalty_total < threshold:  
            feasible_designs.append((circuit_design, penalty_total))
    
    # Step 3: 選擇一個可行解（這裡可以是第一個符合條件的，或依懲罰值排序）
    if feasible_designs:
        feasible_designs.sort(key=lambda x: x[1])  # 按照懲罰值排序
        best_design = feasible_designs[0][0]
        return {
            "configuration": "with_buffer",
            "buffer": best_design.buffer.name,
            "details": best_design  # 包含電路拓撲、各元件參數等
        }
    
    # 如果所有候選解都不符合，返回不可行訊息
    return {"error": "No feasible design found"}


# solution
class Component:
    """一般元件定義"""
    def __init__(self, name):
        self.name = name
        self.params = {}      # 例如輸出電壓、輸出電流
        self.constraints = {} # 例如電壓門檻、電流限制

class LinkComponent:
    """連接元件，具有兩個端口，內部包含模擬與評分邏輯"""
    def __init__(self, comp_type, **kwargs):
        self.type = comp_type  # 'resistor' 或 'amplifier' 等
        self.params = kwargs

    def simulate(self, unified_input):
        """
        模擬連接元件的行為：
        - 使用左側輸入 (unified_input['V_source'], 'I_source') 來作為輸入訊號
        - 產生一個輸出訊號，滿足右側要求（V_in_required, I_in_limit）
        """
        V_source = unified_input.get('V_source')
        R_load = unified_input.get('R_load')
        
        if self.type == 'resistor':
            R_link = self.params.get('R_link')
            # 假設連接元件只是增加阻抗，輸出訊號與輸入相同，但電流變小
            I_out = V_source / (R_link + R_load)
            V_out = I_out * R_load
            return {'V_out': V_out, 'I_out': I_out}
        elif self.type == 'amplifier':
            gain = self.params.get('gain')
            offset = self.params.get('offset', 0.0)
            # 放大器改變電壓，但電流依然由負載決定
            V_out = gain * V_source + offset
            I_out = V_out / R_load
            return {'V_out': V_out, 'I_out': I_out}
        else:
            return {'V_out': V_source, 'I_out': V_source / R_load}

    def evaluate_cost(self, unified_input):
        """依據模擬結果與右側要求評分，成本越低代表匹配越好"""
        result = self.simulate(unified_input)
        V_out = result['V_out']
        I_out = result['I_out']
        
        cost = 0.0
        # 右側需求
        V_required = unified_input.get('V_in_required')
        I_limit = unified_input.get('I_in_limit')
        
        # 如果輸出電壓低於需求，則懲罰
        if V_required is not None and V_out < V_required:
            cost += 1e6 * (V_required - V_out)**2
        # 如果輸出電流超過限制，則懲罰
        if I_limit is not None and I_out > I_limit:
            cost += 1e6 * (I_out - I_limit)**2
        
        # 元件本身成本：例如希望 resistor 的 R_link 不宜過高；放大器的 gain 希望接近某個理想值
        if self.type == 'resistor':
            cost += self.params.get('R_link', 0)
        elif self.type == 'amplifier':
            cost += abs(self.params.get('gain') - 1) * 100 + abs(self.params.get('offset', 0))
        return cost

def generate_unified_input(left_component, right_component):
    """
    生成統一需求：
    - 左側：輸出電壓、輸出電流（作為參考）
    - 右側：負載電阻與其需求的輸入電壓、電流限制
    """
    unified = {}
    unified['V_source'] = left_component.params.get('V_out')
    unified['I_source'] = left_component.params.get('I_out')
    unified['R_load'] = right_component.params.get('R_load')
    unified['V_in_required'] = right_component.constraints.get('voltage_threshold')
    unified['I_in_limit'] = right_component.constraints.get('current_max')
    return unified

def select_best_link_component(link_library, left_component, right_component):
    unified_input = generate_unified_input(left_component, right_component)
    best_component = None
    best_cost = float('inf')
    for link in link_library:
        cost = link.evaluate_cost(unified_input)
        print(f"候選 {link.type} 成本: {cost:.2f}")
        if cost < best_cost:
            best_cost = cost
            best_component = link
    return best_component, best_cost

# -------------------------
# 例子：假設左側元件輸出 12V，右側負載需要至少 11V 並限制電流 1A
left = Component("Left_Source")
left.params = {'V_out': 12.0, 'I_out': 2.0}  # 假設電流參考值
left.constraints = {}  # 此處重點在供給電壓

right = Component("Right_Load")
right.params = {'R_load': 10.0}
right.constraints = {'voltage_threshold': 11.0, 'current_max': 1.0}

# 建立連接元件候選庫
link_library = [
    LinkComponent('resistor', R_link=10.0),
    LinkComponent('resistor', R_link=20.0),
    LinkComponent('amplifier', gain=1.2, offset=0.0),
    LinkComponent('amplifier', gain=1.5, offset=0.5)
]

best_link, best_cost = select_best_link_component(link_library, left, right)
print("\n最佳連接元件:", best_link.type, best_link.params, "評分成本:", best_cost)


Amp_impedence = 40 * 1000
2.5 <= Amp_voltage <= 5.5
0.5 <= Amp_voltage_in <= Amp_voltage - 0.8
Amp_Gain = 40 * 1000 / (40 * 1000 + Amp_impedense_in)
Amp_voltage_out = Amp_Gain * Amp_voltage_in
    Amp_voltage = Amp_current * Amp_impedense
    Amp_power = Amp_current * Amp_voltage 

DAC_impedence = 0
1.62 <= DAC_voltage <= 3.6
-1 * 1 / 1000 <= DAC_current <= 1 * 1 / 1000
    DAC_voltage = DAC_current * DAC_impedense
    DAC_power = DAC_current * DAC_voltage

Speaker_impedense = 4
0 <= Speaker_power <= 2
    Speaker_voltage = Speaker_current * Speaker_impedense
    Speaker_power = Speaker_current * Speaker_voltage


DAC_voltage = Amp_voltage_in
Amp_impedense_in = DAC_impedence
Amp_voltage_out = Speaker_voltage

EX:
空接: 電流太大
接AMP: 