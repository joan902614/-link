# 一個元件只會有一個 functional feature，現在不會有 structural feature

關係: flow

    
class Slot(FeatureExpr):
    def __init__(self, name):
        super().__init__(name)
    # def set_params(self, **kwargs):
    #     for k, v in kwargs.items():
    #         self.__dict__[k] = v

    # def __repr__(self):
    #     res = f"{self.name}:\n" 
    #     for k, v in self.__dict__.items():
    #         if isinstance(v, ParametricFeature):
    #             res += f"- {k}:\n{v}\n"
    #     return res

class LinkComponent
    REQUIRED_PARAMS = { 'number_of_ports': int }
    OPTIONAL_PARAMS = { 'number_of_input_slots': int, 'number_of_output_slots': int }

class Amp(FunctionalFeature):
    # schema
    REQUIRED_PARAMS = {}
    OPTIONAL_PARAMS = {}
    def __init__(self, **kwargs):
        super().__init__("DAC", [{"amp"}], number_of_ports=?, number_of_input_slots=2, number_of_output_slots=1)
        # self.v_dd, self.i_out, self.v_out, self.p_out = symbols("i_out v_out p_out")
        
        self.inport1 = Analog(
            voltage_in = ParametricFeature(
                            name="voltage_supply", 
                            tags={"voltage", "input", "supply"},
                            symbol=self.v_dd, 
                            constraints=[Inequality(2.5, 5.5)],
                            dimension=Voltage,
                        ),
            current_in = ParametricFeature(
                            name=, 
                            tags={"current", "input"}, 
                            symbol=, 
                            constraints=[],
                            dimension=Current,
                        ),
            power_in = ParametricFeature(
                            name=,
                            tags={"power", "input"},
                            symbol=,
                            constraints=[],
                            dimension=Power,
                        ),
            impedance_in = ParametricFeature(
                            name=,
                            tags={"impedance", "input"},
                            symbol=,
                            constraints=[],
                            dimension=Resistance,
                        ),
        )(self.input_ports[0])

        self.inport2 = Analog(
            voltage_in = ParametricFeature(
                            name="voltage_input", 
                            tags={"voltage", "input"},
                            symbol=self.v_in, 
                            constraints=[Inequality(0.5, Equation(self.v_dd - 0.8))],
                            dimension=Voltage,
                        ),
            current_in = ParametricFeature(
                            name="current_in", 
                            tags={"current", "input"}, 
                            symbol=self.i_in, 
                            constraints=[],
                            dimension=Current,
                        ),
            power_in = ParametricFeature(
                            name="power_in",
                            tags={"power", "input"},
                            symbol=self.p_in,
                            constraints=[],
                            dimension=Power,
                        ),
            impedance_in = ParametricFeature(
                            name="impedance",
                            tags={"impedance", "input"},
                            symbol=self.z_in,
                            constraints=[],
                            dimension=Resistance,
                        ),
        )(self.input_ports[1])
        
        self.outport = Analog(
            voltage_out = ParametricFeature(
                            name="voltage_output", 
                            tags={"voltage", "output"},
                            symbol=self.v_out, 
                            constraints=[Equation(self.v_out * (self.z / (self.z + self.z_in)))],
                            dimension=Voltage,
                        ),
            current_out = ParametricFeature(
                            name="current_out", 
                            tags={"current", "output"}, 
                            symbol=self.i_out, 
                            constraints=[],
                            dimension=Current,
                        ),
            power_out = ParametricFeature(
                            name="power_output",
                            tags={"power", "output"},
                            symbol=self.p_out,
                            constraints=[],
                            dimension=Power,
                        ),
            impedance_out = ParametricFeature(
                            name="impedance",
                            tags={"impedance", "output"},
                            symbol=self.z_out,
                            constraints=[],
                            dimension=Resistance,
                        ),
        )(self.output_ports[0])
        # self.Gain = None
        # self.control = None
        self.impedence = ParametricFeature(
                            name="impedance",
                            tags={"impedance"},
                            symbol=self.z,
                            constraints=[Constant(40 * 1000)],
                            dimension=Resistance,
                        )

class NoLinkError(Exception):
    pass
def checkNoCandidate(candidates):
    if (not candidates):
        raise NoLinkError("No matching link")
    else:
        pass

def classifyPortValueDomain(comp1_ports, comp2_ports) -> dict:
    '''
    comp_ports, link_comp_slots: list of ports
    Classify all value domain in comp1's port and comp2's port
    return
    {
        value domain1:
        {
            left_comp: [...]
            right_comp: [...]
        }
        ...
    }
    '''
    # step 1
    value_domain_groups = {}
    for p1 in comp1_ports:
        p1_value_domain = p1.getValueDomain()
        if p1_value_domain not in value_domain_groups:
            value_domain_groups[p1_value_domain] = {'left_comp': [], 'right_comp': []}
        value_domain_groups[p1_value_domain]['left_comp'].append(p1)
    for p2 in comp2_ports:
        p2_value_domain = p2.getValueDomain()
        if p2_value_domain not in value_domain_groups:
            value_domain_groups[p2_value_domain] = {'left_comp': [], 'right_comp': []}
        value_domain_groups[p2_value_domain]['right_comp'].append(p2)

ValueDomainListAPMatcher = {
    Digit: digitAPMatch,
    Analog: analogAPMatch
}
def digitAPMatch():
    
def analogAPMatch(left_ports, right_ports):
    '''
    left_ports, right_ports: analog domain ports of left/right component 
    1. 
    '''



def valueDomainAPMatch(value_domain_groups):
    '''
    each value call itself's Assumption Provide 
    1. 
    '''
    for v in value_domain_groups.keys():
        matcher = valueDomainList[v]
        matcher(value_domain_groups[v])
   

# value domain 會有自己的套餐嗎，獨立於 functional feature?
class Flow():
    """
    1. 存入 source、destination
    2. port 的 value domain 數量要和 slot 對得起來
    3. port's constraint 和 slot's constraint 取交集，輸入成 link comp 資訊(maybe 也包含 config)?
    4. 送到 output slot
    5. output slot 再送到 destination
    """
    def __init__(self, func_feature_start, func_feature_end):
        """
        comp_start: source component
        comp_end: destination component
        link_comp: matching link components
        """
        # Step 1
        self.comp_start = func_feature_start
        self.comp_end = func_feature_end                                  
        self.link_comp = []
        self.findCandidateLink()
    
    def findCandidateLink(self):
        # Step 2
        for candidate in LinkLibrary: 
            if (matchPortSlot(self.comp_start.in_ports, candidate.out_slots) 
                and matchPortSlot(self.comp_end.out_ports, candidate.in_slots)):
                self.link_comp.append(candidate)
        checkNoCandidate(self.link_comp)
        # Step 3
        for candidate in self.link_comp:
            tmp = []
            if (propagateAssumptionGuarantee(self.comp_start.in_ports, candidate.out_slots)):
                tmp.append(candidate)
            self.link_comp = tmp
        checkNoCandidate(self.link_comp)
        # step 4
        # step 5
        for candidate in self.link_comp:
            tmp = []
            if (propagateAssumptionGuarantee(self.comp_start.in_ports, candidate.out_slots)):
                tmp.append(candidate)
            self.link_comp = tmp
        checkNoCandidate(self.link_comp)
 

dac = DAC_core()
speaker = Speaker_core()
flow_dac_speaker = Flow(dac, speaker)

# dac
class Analog:


dac_port = []
# not mine
comp.getPorts() -> list
comp.port.getValueDomain() -> isinstance