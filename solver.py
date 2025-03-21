# examle
# value in example is str
# assumptions and provides in is str
class Port:
    def __init__(self, name, value_domain, assumptions=list(), provides=list()):
        self.name = name
        self._value_domain = value_domain
        self._assumptions = assumptions
        self._provides = provides

    def getValueDomain(self):
        return self._value_domain

    def getAssumptions(self):
        return self._assumptions

    def getProvides(self):
        return self._provides

    def __repr__(self):
        return self.name

# class NoLinkError(Exception):
#     pass
# def checkNoCandidate(candidates):
#     if (not candidates):
#         raise NoLinkError("No matching link")
#     else:
#         pass


# solver

def classifyPortValueDomain(left_ports: list, right_ports: list) -> dict:
    '''
    left_ports, right_ports: list of ports
    Classify all value domain in left's port and right's port
    return
    {
        value domain1:
        {
            left_ports: [...]
            right_ports: [...]
        }
        ...
    }
    '''
    value_domain_groups = {}
    for p_l in left_ports:
        p_l_value_domain = p_l.getValueDomain()
        if p_l_value_domain not in value_domain_groups:
            value_domain_groups[p_l_value_domain] = {'left_ports': [], 'right_ports': []}
        value_domain_groups[p_l_value_domain]['left_ports'].append(p_l)
    for p_r in right_ports:
        p_r_value_domain = p_r.getValueDomain()
        if p_r_value_domain not in value_domain_groups:
            value_domain_groups[p_r_value_domain] = {'left_ports': [], 'right_ports': []}
        value_domain_groups[p_r_value_domain]['right_ports'].append(p_r)
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



def is_bidirectional_APmatch(value_domain, left_port: Port, right_port: Port) -> bool:
    '''
    check if left port Assumption has Provide and right port Assumption has Provide
    '''
    left_As = left_port.getAssumptions()
    left_Ps = left_port.getProvides()
    right_As = right_port.getAssumptions()
    right_Ps = right_port.getProvides()
    solver = ValueDomainSolver[value_domain]

    # check all left assumptions has provides in right 
    if not solver(left_As, right_Ps):
        return False

    # check all right assumptions has provides in left 
    if not solver(right_As, left_Ps):
        return False

    return True
def APMatch(value_domain, left_ports: list, right_ports: list):
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
            if is_bidirectional_APmatch(value_domain, p_l, p_r):
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

def valueDomainAPMatch(value_domain_groups: dict):
    '''
    each value call itself's Assumption Provide 
    1. 
    '''
    # for v in value_domain_groups.keys():
    #     APMatch(v, value_domain_groups[v][left_ports], value_domain_groups[v][right_ports])
    results = {}
    for v in value_domain_groups.keys():
        matches = APMatch(v, value_domain_groups[v]['left_ports'], value_domain_groups[v]['right_ports'])
        results[v] = matches
    return results

# example use
left_ports = [
    Port("L1", "Analog", [7], [1, 2]),
    Port("L2", "Analog", [2], [2]),
   
    Port("L3", "Digit", [0.5], [0.5, 1.0])
]
right_ports = [
    Port("R1", "Analog", [1], [1, 3]),
    Port("R2", "Analog", [2], [2, 4]),

    Port("R3", "Digit", [0.5], [0.5])
]

# step 1
groups = classifyPortValueDomain(left_ports, right_ports)
print("依照 Value Domain 分類結果:")
for domain, ports in groups.items():
    print(f"{domain}: Left = {ports['left_ports']}, Right = {ports['right_ports']}")

# step 2
match_results = valueDomainAPMatch(groups)
print("\n各 Value Domain 的 AP Match 結果:")
for domain, matches in match_results.items():
    print(f"Value Domain: {domain}")
    for pair in matches:
        print("  ", pair)
        print("  ", pair[0], "A: ", pair[0].getAssumptions() if pair[0] is not None else "", "P: ", pair[0].getProvides() if pair[0] is not None else "")
        print("  ", pair[1], "A: ", pair[1].getAssumptions() if pair[1] is not None else "", "P: ", pair[1].getProvides() if pair[1] is not None else "")
# class Flow():
#     """
#     1. 存入 source、destination
#     2. port 的 value domain 數量要和 slot 對得起來
#     3. port's constraint 和 slot's constraint 取交集，輸入成 link comp 資訊(maybe 也包含 config)?
#     4. 送到 output slot
#     5. output slot 再送到 destination
#     """
#     def __init__(self, func_feature_start, func_feature_end):
#         """
#         comp_start: source component
#         comp_end: destination component
#         link_comp: matching link components
#         """
#         # Step 1
#         self.comp_start = func_feature_start
#         self.comp_end = func_feature_end                                  
#         self.link_comp = []
#         self.findCandidateLink()
    
#     def findCandidateLink(self):
#         # Step 2
#         for candidate in LinkLibrary: 
#             if (matchPortSlot(self.comp_start.in_ports, candidate.out_slots) 
#                 and matchPortSlot(self.comp_end.out_ports, candidate.in_slots)):
#                 self.link_comp.append(candidate)
#         checkNoCandidate(self.link_comp)
#         # Step 3
#         for candidate in self.link_comp:
#             tmp = []
#             if (propagateAssumptionGuarantee(self.comp_start.in_ports, candidate.out_slots)):
#                 tmp.append(candidate)
#             self.link_comp = tmp
#         checkNoCandidate(self.link_comp)
#         # step 4
#         # step 5
#         for candidate in self.link_comp:
#             tmp = []
#             if (propagateAssumptionGuarantee(self.comp_start.in_ports, candidate.out_slots)):
#                 tmp.append(candidate)
#             self.link_comp = tmp
#         checkNoCandidate(self.link_comp)
 

# dac = DAC_core()
# speaker = Speaker_core()
# flow_dac_speaker = Flow(dac, speaker)


# not mine
# comp.getPorts() -> list
# comp.port.getValueDomain() -> isinstance
# comp.port.getAssumptions() -> list
# comp.port.getProvides() -> list
# comp.port.setConnectPort(list) 
