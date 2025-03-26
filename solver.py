# examle
# value domain in example is str but actually class
from sympy import symbols, Eq, Interval, solve, simplify, And

class Port:
    def __init__(self, name, value_domain, parameter):
        self.name = name
        self._value_domain = value_domain
        self._parameter = parameter

    def getValueDomain(self):
        return self._value_domain

    def getParameter(self):
        return self._parameter

    def __repr__(self):
        return self.name

class Parameter:
    def __init__(self, name, max, min, type):
        self._name = name
        self._type = type
        self._constraint = self.setConstraint(max, min)
    
    def setConstraint(self, max, min):
        var = symbols(self._name)
        return And(min <= var, var <= max)

class Analog:
    def __init__(self,
                 v={"name": "v", "max": float('inf'), "min": float('-inf'), "type": None}, 
                 i={"name": "i", "max": float('inf'), "min": float('-inf'), "type": None}, 
                 p={"name": "p", "max": float('inf'), "min": float('-inf'), "type": None}, 
                 r={"name": "r", "max": float('inf'), "min": float('-inf'), "type": None}):
        self._v = Parameter(v["name"], v["max"], v["min"], v["type"])
        self._i = Parameter(i["name"], i["max"], i["min"], i["type"])
        self._p = Parameter(p["name"], p["max"], p["min"], p["type"])
        self._r = Parameter(r["name"], r["max"], r["min"], r["type"])
    
    def getParameter(self):
        return [self._v, self._i, self._p, self._r]

L1 = Port("L1", "Analog", Analog({"name": "v", "max": 3, "min": 6, "type": "Provide"}))
L2 = Port("L2", "Analog", Analog({"name": "v", "max": 3, "min": 6, "type": "Provide"}))

R1 = Port("R1", "Analog", Analog({"name": "v", "max": 3, "min": 6, "type": "Provide"}))

# solver

def classifyPortValueDomain(left_ports: list, right_ports: list) -> dict:
    '''
    left_ports, right_ports: list of ports
    Classify all value domain in left's port and right's port
    return
    {
        "value domain1":
        {
            "left_ports": [...]
            "right_ports": [...]
        }
        ...
    }
    '''
    value_domain_groups = {}

    # classify left port
    for p_l in left_ports:
        p_l_value_domain = p_l.getValueDomain()
        if p_l_value_domain not in value_domain_groups:
            value_domain_groups[p_l_value_domain] = {"left_ports": [], "right_ports": []}
        value_domain_groups[p_l_value_domain]["left_ports"].append(p_l)
    
    # classify right port
    for p_r in right_ports:
        p_r_value_domain = p_r.getValueDomain()
        if p_r_value_domain not in value_domain_groups:
            value_domain_groups[p_r_value_domain] = {"left_ports": [], "right_ports": []}
        value_domain_groups[p_r_value_domain]["right_ports"].append(p_r)
    
    return value_domain_groups

def digitSolver(assumptions: list, provides: list) -> bool:
    # ex   
    return any(a in provides for a in assumptions)
def analogSolver(assumptions: list, provides: list) -> bool:
    # ex
    return any(a in provides for a in assumptions)
ValueDomainSolver = {
    "Digit": digitSolver,
    "Analog": analogSolver
}


# port match
def isAPMatch(value_domain, left_port_parameter: list, right_port_parameter: list) -> bool:
    '''
    value_domain: one of special value domain class
    left_port_parameter, right_port_parameter: left/right port's parameter

    check if left port Assumption has Provide and right port Assumption has Provide
    '''
    solver = ValueDomainSolver[value_domain] # maybe don't need? just all value domain use the same solver
    left_all_provide, right_all_provide = True, True

    # check all left assumptions has provides in right 
    for idx, p in enumerate(left_port_parameter):
        if p.getType() == "Assumption":
            if not solver(p, right_port_parameter[idx]):
                return False
            else:
                left_all_provide = False

    # check all right assumptions has provides in left 
    for idx, p in enumerate(right_port_parameter):
        if p.getType() == "Assumption":
            if not solver(p, left_port_parameter[idx]):
                return False
            else:
                right_all_provide = False
    
    # check left and right assumptions is empty
    if left_all_provide and right_all_provide:
        return False
    else:
        return True
    
def portMatch(value_domain, left_ports: list, right_ports: list):
    '''
    left_ports, right_ports: value domain ports of left/right component 
    
    1. for each left port 
        if used -> pass
        if not used -> match each right port
    2. if left/right can't match -> add in match with none
    '''
    matched = []
    used_left = set()
    used_right = set()
    
    for idx_l, p_l in enumerate(left_ports):
        if idx_l in used_left:
            continue
        found = False
        for idx_r, p_r in enumerate(right_ports):
            if idx_r in used_right:
                continue
            if isAPMatch(value_domain, p_l, p_r):
                matched.append([p_l, p_r])
                used_left.add(idx_l)
                used_right.add(idx_r)
                found = True
                break
        if not found:
            matched.append((p_l, None))  

    for idx_r, p_r in enumerate(right_ports):
        if idx_r not in used_right:
            matched.append((None, p_r))

    return matched

def valueDomainPortMatch(value_domain_groups: dict):
    '''
    each value call itself's Assumption Provide 
    '''
    results = {}

    for v in value_domain_groups.keys():
        matches = portMatch(v, value_domain_groups[v]['left_ports'], value_domain_groups[v]['right_ports'])
        results[v] = matches
    
    return results

# example use
left_ports = [
    Port("L1", "Analog", [7], [1, 2]),
    Port("L2", "Analog", [2], [2]),
   
    # Port("L3", "Digit", [0.5], [0.5, 1.0])
]
right_ports = [
    Port("R1", "Analog", [1], [1, 3]),
    Port("R2", "Analog", [2], [2, 4]),

    # Port("R3", "Digit", [0.5], [0.5])
]

# step 1
groups = classifyPortValueDomain(left_ports, right_ports)
print("依照 Value Domain 分類結果:")
for domain, ports in groups.items():
    print(f"{domain}: Left = {ports['left_ports']}, Right = {ports['right_ports']}")

# step 2
match_results = valueDomainPortMatch(groups)
print("\n各 Value Domain 的 AP Match 結果:")
for domain, matches in match_results.items():
    print(f"Value Domain: {domain}")
    for pair in matches:
        print("  ", pair)
        print("  ", pair[0], "A: ", pair[0].getAssumptions() if pair[0] is not None else "", "P: ", pair[0].getProvides() if pair[0] is not None else "")
        print("  ", pair[1], "A: ", pair[1].getAssumptions() if pair[1] is not None else "", "P: ", pair[1].getProvides() if pair[1] is not None else "")

# not mine
# comp.getPorts() -> list
# comp.port.getValueDomain() -> isinstance
# comp.port.getAssumptions() -> list
# comp.port.getProvides() -> list
# comp.port.setConnectPort(list) 
