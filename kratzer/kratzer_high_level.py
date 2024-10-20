import sys

sys.path.append("..")
from kratzer import Kratzer
from base_classes import HighVoltageSource
import time


class KratzerHighLevelControl(HighVoltageSource):
    def __init___(self, IP):
        self.kratzer = Kratzer(IP)

    @override
    def check_insulation(self) -> bool:
        m2s_rs_cw1 = self.kratzer.get_M2S_RS_CW1()
        m2s_rs_cw1 |= 1 << 4
        self.set_M2S_RS_CW1(m2s_rs_cw1)
        time.sleep(1)
        # the last bit of this field contains the result of the test
        return self.kratzer.get_S2M_AS_SW2() & 1

    @override
    def get_voltage(self) -> float:
        return self.kratzer.get_S2M_AV_U()

    @override
    def get_current(self) -> float:
        return self.kratzer.get_S2M_AV_I()

    @override
    def set_charging_target(
        self, current: float, min_voltage: float, max_voltage: float
    ):
        self.kratzer.set_M2S_SP_Umin(min_voltage)
        self.kratzer.set_M2S_SP_Umax(max_voltage)
        self.kratzer.set_M2S_SP_Imin(current)
