from kratzer import Kratzer
from base_classes import HighVoltageSource


class KratzerHighLevelControl(HighVoltageSource):
    self.min_voltage
    self.max_voltage

    def __init___(self, IP):
        self.kratzer = Kratzer(IP)


    def check_insulation(self) -> bool:
        #self.kratzer.set_M2S_RS_ISO(1)#activate isolation check
        pass


    def get_voltage(self) -> float:
        pass


    def get_current(self) -> float:
        pass


    def set_charging_target(self, current: float, min_voltage: float, max_voltage: float):
        self.kratzer.set_M2S_SP_Umin(min_voltage)
        self.kratzer.set_M2S_SP_Umax(max_voltage)
        self.kratzer.set_M2S_SP_Imin(current)

