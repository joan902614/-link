import pint
ureg = pint.UnitRegistry()



time = ["Peak", "Temporary", "Continuous"]



class Port:
    def __init__(self, connect=False, connect_type=None, type=None, data=None):
        self.connect = connect              # Boolean
        self.connect_type = connect_type    # String
        self.type = type                    # String
        # feature: [name, direction, value] # String, String, Number
        self.data = data

class DAC:
    def __init__(self):
        self.in_port = Port(type="analog", data=[["vin", "input", 0]])
        self.out_port = Port(type="analog", data=[["vout", "output", 0], ["rin", "input", 0]])
        self.voltage # [input, output]
        self.current # [self(cal)]
        self.impedense # [input]

#要怎麼把輸入、本體、輸出連起來??????
    @property
    def voltage(self):
        for in_item in self.in_port.data:
            if in_item[0] == "vin":
                for out_item in self.out_port.data:
                    if out_item[0] == "vout":
                        out_item[2] = in_item[2]
                return in_item[2] 
        return 0
    
    

############ component library ############
# MSPM0G1507
class MSPM0G1507:
    def __init__(self):
        self.vdd = InputPort()
        self.vss = InputPort()
        self.dac = DAC() # module
    def dac_module():
        self.dac.input_port = self.vdd



self.vdd [input]
self.dac.vdd -> self.dac.vdd = self.vdd  [self(cal), output]
self.dac.current [self(cal)]
self.dac.impedense [input]



## basic condition
context MSPM0G1507 inv VDD: 
    # 對外連接的 vdd port 一定要連、是 analog、範圍在 1.62V ~ 3.6V
    self.vdd.connect = True and self.vdd.connect_type = self.vdd.type   
    1.62 * ureg.voltage <= self.vdd.value <= 3.6 * ureg.voltage 
context MSPM0G1507 inv VSS:
    # 對外連接的 vss port 一定要連、是 analog、範圍為 0
    self.vss.connect = True and self.vss.connect_type = self.vss.type  
    self.vss.value = 0 * ureg.voltage

## dac
context MSPM0G1507 inv DAC: 
    # 啟動這個 DAC module(有連到 dac 的 port)
    self.dac.connect = True and self.dac.type = "analog" implies (
        # current 要在 -1mA ~ 1mA 
        -1 * ureg.milli * ampere <= self.dac.current <= 1 * ureg.milli * ureg.ampere
    )   

 
# Dayton Audio CE32A-4
self.impedense = 4 * ureg.ohm [output]

context DaytonAudioCE32A-4 inv Port: 
    # 對外連接的 port 一定要連、是 analog
    self.spk.connect = True and self.spk.connect_type = self.spk.type 
context DaytonAudioCE32A-4 inv Power:
    # power 要在 2W 以下、2~4W 只能是 Peak 的執行時間
    (0 * ureg.watt <= self.power <= 2 * ureg.watt) or (self.power <= 2 * ureg.watt and self.time == Peak)

############ link library ############


############ user spec ############
# user mcu block

# user speaker block



```
connection
```
speaker 和 mcu
def connect_up(Ba, Bb):
    Ba.port.connect = True
    Ba.port.connect_type = Bb.type
    Bb.port.connect = True
    Bb.port.connect_type = Ba.type
    Ba.input = Bb.output
    Bb.input = Ba.output



不管怎麼拿到 input 和 output 資料

solver


analog: 
1. V = IR
2. P = IV

currentA.min <= A.current <= currentA.max [constraint]
currentB.min <= B.current <= currentB.max [constraint]
powerA.min <= A.power <= powerA.max [constraint]
powerB.min <= B.power <= powerB.max [constraint]
voltageB.min <= B.voltage <= voltageB.max [constraint]
voltageA.min <= A.voltage <= voltageA.max [constraint]

def getConstraint(object, tag: [string])
    for tag in object.constraint
    return [string...] 

def solverAnalog():
    1. 跟 analog 相關的 constraint 選起來 (透過 tag，實際值也放在 constraint，constraint 假設字串)
    2. 加入補充的 constraint
    3. 拿 input 和 output
    4. solver


Impedence 限制 

def require(object, string):
    = find(oject, [solver_type, "input", string])
    return [] 
def findProvide(object, list):
    for item in list:
        = find(oject, [solver_type, "input", string])
    return [] 

require(DAC, "analog") # return DAC.impedense, ["impedense"]
findProvide(Speaker, ["impedense"])


require(Speaker, "analog") # return Speaker.voltage, ["voltage"]
findProvide(DAC, ["analog", "voltage"])


DAC constraint:
    self
        DAC.voltage
        1.62V <= DAC.voltage <= 3.6V 
        -1mA <= DAC.current <= 1mA 
    add
        DAC.voltage = DAC.current * DAC.impedense
        DAC.power = DAC.current * DAC.voltage

Speaker: 
    self
        Speaker.impedense = 4 * OHM
        Speaker.power <= 2W or (2W <= Speaker.power <= 4W and Speaker.time == Peak)
    add
        Speaker.voltage = Speaker.current * Speaker.impedense
        Speaker.power = Speaker.current * Speaker.voltage





























