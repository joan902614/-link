import pint
ureg = pint.UnitRegistry()

time = ["Peak", "Temporary", "Continuous"]

class Port:
    def __init__(self):
        
class InputPort:
    def __init__(self):
        self.connect = False        # Boolean
        self.connect_type = None    # String
        self.type = None            # String
        self.value = 0              # Number
class OutputPort:
    def __init__(self):
        self.connect = False        # Boolean
        self.connect_type = None    # String
        self.type = None            # String
        self.value = 0              # Number

class DAC:
    def __init__(self):
        self. = InputPort() 
        self. = OutputPort()
        self.voltage # [input, output]
        self.current # [self(cal)] 
        self.impedense # [input]
    

############ component library ############
# MSPM0G1507
class MSPM0G1507:
    def __init__(self):
        self.vdd = InputPort()
        self.vss = InputPort()
        self.dac = DAC() # module
    def voltage():
        self.dac.voltage = self.vdd



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






