# class NoLinkError(Exception):
#     pass
# def checkNoCandidate(candidates):
#     if (not candidates):
#         raise NoLinkError("No matching link")
#     else:
#         pass

# value domain classify
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
def analogSolver(assumptions: list, provides: list) -> bool:
ValueDomainSolver = {
    Digit: digitSolver,
    Analog: analogSolver
}

# port match
def isAPMatch(value_domain, left_port: Port, right_port: Port) -> bool:
    '''
    value_domain: one of special value domain class
    left_port, right_port: Port instance of left/right port

    check if left port Assumption has Provide and right port Assumption has Provide
    '''
    left_As = left_port.getAssumptions()
    left_Ps = left_port.getProvides()
    right_As = right_port.getAssumptions()
    right_Ps = right_port.getProvides()
    solver = ValueDomainSolver[value_domain]

    # check left and right assumptions is empty
    if (not left_As) and (not right_As):
        return False
    # check all left assumptions has provides in right 
    if not solver(left_As, right_Ps):
        return False
    # check all right assumptions has provides in left 
    if not solver(right_As, left_Ps):
        return False
    return True

def portMatch(value_domain, left_ports: list, right_ports: list) -> list(list):
    '''
    left_ports, right_ports: value domain ports of left/right component 

    each port do Assumption Provide match to find matched port
    '''
    matched = []
    used_left = set()
    used_right = set()
    
    # each ports do match
    for idx_l, p_l in enumerate(left_ports):
        if idx_l in used_left:
            continue
        for idx_r, p_r in enumerate(right_ports):
            if idx_r in used_right:
                continue
            if isAPMatch(value_domain, p_l, p_r):
                matched.append([p_l, p_r])
                used_left.add(idx_l)
                used_right.add(idx_r)
                break
    
    # if remain ports has assumption -> error 
    for idx_l, p_l in enumerate(left_ports):
        if (idx_l not in used_left) and (not p_l.getAssumptions()):
            print("error")
        elif (idx_l not in used_left):
            matched.append([p_l, None])
    for idx_r, p_r in enumerate(right_ports):
        if (idx_r not in used_right) and (not p_r.getAssumptions()):
            print("error")
        elif (idx_r not in used_right):
            matched.append([None, p_r])
    
    return matched

def valueDomainPortsMatch(value_domain_groups: dict) -> dict:
    '''
    each value domain do ports match
    '''
    # for v in value_domain_groups.keys():
    #     APMatch(v, value_domain_groups[v]['left_ports'], value_domain_groups[v]['right_ports'])
    results = {}
    for v in value_domain_groups.keys():
        matches = portMatch(v, value_domain_groups[v]['left_ports'], value_domain_groups[v]['right_ports'])
        results[v] = matches
    return results

def configProvide(match_ports: list(list)):
    '''
    match_ports: AP match ports

    check if provide can be configured to change to guarantee 
    '''
    

groups = classifyPortValueDomain(left_ports, right_ports)
match_results = valueDomainPortsMatch(groups)
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
comp.getPorts() -> list
comp.port.getValueDomain() -> isinstance
comp.port.getAssumptions() -> list
comp.port.getProvides() -> list

comp.port.setConnectPort(list) 
