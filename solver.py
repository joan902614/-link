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



def matchPortSlot(comp_ports, link_comp_slots) -> bool:
    '''
    match the ports' number and domain with slot
    '''
def intersectAssumptionGuarantee(comp_ports, link_comp_slots):
    '''
    intersect port's assumption and slot's guarantee 
    intersect slot's assumption and port's guarantee 
    '''

class Flow():
    def __init__(self, func_feature_start, func_feature_end):
        """
        comp_start: source component
        comp_end: destination component
        link_comp: matching link components
        
        1. 存入 source、destination
        2. port 的 value domain 數量要和 slot 對得起來
        3. port's assumption 和 slot's guarantee 取交集，反之
        4. 交集完的送到 output slot
        5. output slot 再送到 destination
        """
        self.comp_start = func_feature_start
        self.comp_end = func_feature_end                                  
        self.link_comp = []
        # problem: slot 不會全部和 port 對，可能其中一個有連起來就好?
        for candidate in LinkLibrary: 
            if (matchPortSlot(self.comp_start.in_ports, candidate.out_slots) 
                and matchPortSlot(self.comp_end.out_ports, candidate.in_slots)):
                self.link_comp.append(candidate)
        for candidate in self.link_comp:
            tmp = []
            if (intersectAssumptionGuarantee(self.comp_start.in_ports, candidate.out_slots) 
                and intersectAssumptionGuarantee(self.comp_end.out_ports, candidate.in_slots)):
                tmp.append(candidate)
            self.link_comp = tmp
 

dac = DAC_core()
speaker = Speaker_core()
flow_dac_speaker = Flow(dac, speaker)



1. 建立關係
    * Flow
        1. 存入 source、destination
2. 每個 link component functional feature 都會有自己的套餐，裡面包含 slot
3. port 的 value domain 數量要和 slot 對得起來
4. port's assumption 和 slot's guarantee 取交集，反之

必須要有個方式表示哪些是一定要連起來的 port 和 slot
value domain 會有自己的套餐嗎，獨立於 functional feature?
要怎麼知道 assumption, guarantee, provide, require?，應該會需要直接透過一個方式表明，像是 tag

