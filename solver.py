# examle
# value domain in example is str but actually class
import sympy as sp

class Port:
    def __init__(self, name, value_domain, parameter):
        self.name = name
        self._value_domain = value_domain
        self._parameter = parameter

    def getValueDomain(self):
        return self._value_domain

    def getParameter(self):
        return self._parameter.getParameter()

    def __repr__(self):
        return self.name

class Parameter:
    def __init__(self, name, min, max, type):
        self._name = name
        self._type = type
        self._min = min
        self._max = max
        self._constraint = self.setConstraint(min, max)
    
    def setConstraint(self, min, max):
        var = sp.symbols(self._name)
        return sp.And(min <= var, var <= max)
    
    def getMin(self):
        return self._min

    def getMax(self):
        return self._max
    
    def getType(self):
        return self._type
    
    def getConstraint(self):
        return self._constraint

class Analog:
    def __init__(self,
                 v={"name": "v", "min": float('-inf'), "max": float('inf'), "type": "None"}, 
                 i={"name": "i", "min": float('-inf'), "max": float('inf'), "type": "None"}, 
                 p={"name": "p", "min": float('-inf'), "max": float('inf'), "type": "None"}, 
                 r={"name": "r", "min": float('-inf'), "max": float('inf'), "type": "None"}):
        self._v = Parameter(v["name"], v["min"], v["max"], v["type"])
        self._i = Parameter(i["name"], i["min"], i["max"], i["type"])
        self._p = Parameter(p["name"], p["min"], p["max"], p["type"])
        self._r = Parameter(r["name"], r["min"], r["max"], r["type"])
    
    def getParameter(self):
        return {"v": self._v, "i": self._i, "p": self._p, "r": self._r}

# solver

def classifyPortValueDomain(left_ports: list, right_ports: list):
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

def APsolver(assumption: Parameter, provide: Parameter):
    '''
    assumption, provide: Parameter object

    assumption check and replace provide 

    return bool, constraint(sp.And)
    '''
    if provide.getMin() <= assumption.getMin() and assumption.getMax() <= provide.getMax():
        return True, assumption.getConstraint()
    else:
        return False, None

def analogSolver(left_port_parameter: dict, right_port_parameter: dict):
    '''
    left_port_parameter, right_port_parameter: dict parameter of left/right port

    check if left/right port Assumption has Provide, None can be defined
    
    return
    '''
    constraint_set = {}
    constraints = []
    
    for k, v in left_port_parameter.items():
        if v.getType() == "Assumption":
            if right_port_parameter[k].getType() == "Assumption":
                return False
            elif right_port_parameter[k].getType() == "Provide":
                res, constraint = APsolver(v, right_port_parameter[k])
                if not res:
                    return False
                else:
                    constraint_set[v] = constraint
                    constraints.append(constraint)
            elif right_port_parameter[k].getType() == "None":
                constraint_set[v] = v.getConstraint()
                constraints.append(v.getConstraint())
        elif v.getType() == "Provide":
            if right_port_parameter[k].getType() == "Assumption":
                res, constraint = APsolver(right_port_parameter[k], v)
                if not res:
                    return False
                else:
                    constraint_set[v] = constraint
                    constraints.append(constraint)
            elif right_port_parameter[k].getType() == "Provide":
                return False
            elif right_port_parameter[k].getType() == "None":
                constraint_set[v] = v.getConstraint()
                constraints.append(v.getConstraint())
        elif v.getType() == "None":
            if right_port_parameter[k].getType() == "Assumption":
                constraint_set[v] = right_port_parameter[k].getConstraint()
                constraints.append(right_port_parameter[k].getConstraint())
            elif right_port_parameter[k].getType() == "Provide":
                constraint_set[v] = right_port_parameter[k].getConstraint()
                constraints.append(right_port_parameter[k].getConstraint())
            elif right_port_parameter[k].getType() == "None":
                pass
    
    v, i, r, p = sp.symbols("v i r p")
    vars = [v, i, r, p]
    eqs = [sp.Eq(v, i * r), sp.Eq(p, i * v)]

    # solutions_eq = sp.solve(eqs, vars, dict=True)
    # subs_map = solutions_eq[0]
    # print(subs_map)
    # substituted_ineqs = []
    # for ineq in constraints:
    #     substituted_ineqs.append(ineq.subs(subs_map))
    # solution_range = sp.reduce_inequalities(substituted_ineqs)

    all_results = []

    for var in vars:
        sols = sp.solve(eqs, var, dict=True)
        # print(sols)

        for sol in sols:
            substituted_ineqs = [ineq.subs(sol) for ineq in constraints]
            print(substituted_ineqs)

            solution_range = sp.reduce_inequalities(substituted_ineqs)
            all_results.append(solution_range)

    # print(all_results)
    return all_results
    

def digitSolver(assumptions: list, provides: list) -> bool:
    # ex
    return any(a in provides for a in assumptions)
ValueDomainSolver = {
    "Digit": digitSolver,
    "Analog": analogSolver
}

def portMatch(value_domain, left_ports: list, right_ports: list):
    '''
    value_domain: value domain class
    left_ports, right_ports: value domain ports of left/right component 

    each port do Parameter match to find matched port

    return: [[L, R]]
    '''
    matched = []
    used_left = set()
    used_right = set()
    solver = ValueDomainSolver[value_domain]

    # each ports do match
    for idx_l, p_l in enumerate(left_ports):
        if idx_l in used_left:
            continue
        for idx_r, p_r in enumerate(right_ports):
            if idx_r in used_right:
                continue
            if solver(p_l.getParameter(), p_r.getParameter()):
                matched.append([p_l, p_r])
                used_left.add(idx_l)
                used_right.add(idx_r)
                break
    
    # if remain ports has assumption -> error 
    for idx_l, p_l in enumerate(left_ports):
        # if (idx_l not in used_left) and (not p_l.getAssumptions()):
        #     print("error")
        # elif (idx_l not in used_left):
        #     matched.append([p_l, None])
        if (idx_l not in used_left):
            matched.append([p_l, None])
    for idx_r, p_r in enumerate(right_ports):
        # if (idx_r not in used_right) and (not p_r.getAssumptions()):
        #     print("error")
        # elif (idx_r not in used_right):
        #     matched.append([None, p_r])
        if (idx_r not in used_right):
            matched.append([None, p_r])
    
    return matched

def valueDomainPortMatch(value_domain_groups: dict):
    '''
    value_domain_groups: classified value domain ports

    each value domain call port match
    
    return: 
    {
        "value domain1":
            [L, R]
            ...
        ...
    }
    '''
    results = {}

    for v in value_domain_groups.keys():
        matches = portMatch(v, value_domain_groups[v]["left_ports"], value_domain_groups[v]["right_ports"])
        results[v] = matches
    
    return results

# example use
L1 = Port("L1", "Analog", Analog({"name": "v", "min": 3, "max": 6, "type": "Provide"}))
L2 = Port("L2", "Analog", Analog(v={"name": "v", "min": 2, "max": 3, "type": "Assumption"}, r={"name": "r", "min": 50, "max": 50, "type": "Provide"}))
# L3 = Port("L3", "Digit", [0.5], [0.5, 1.0])
left_ports = [L1, L2]

R1 = Port("R1", "Analog", Analog({"name": "v", "min": 1, "max": 6, "type": "Provide"}))
# R2 = Port("R3", "Digit", [0.5], [0.5])
right_ports = [R1]

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
        # print("  ", pair[1], "Parameter: ", pair[1].getParameter() if pair[1] is not None else "")
        # print("  ", pair[0], "Parameter: ", pair[0].getParameter() if pair[0] is not None else "")

# not mine
# comp.getPorts() -> list
# comp.port.getValueDomain() -> isinstance
# comp.port.getAssumptions() -> list
# comp.port.getProvides() -> list
# comp.port.setConnectPort(list) 
