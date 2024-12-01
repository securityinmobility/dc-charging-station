from base_classes import ChargingState
from base_classes import HighVoltageSource


class DummyHighVoltageSource(HighVoltageSource):
    def check_insulation(self) -> bool:
        return True

    def get_voltage(self) -> float:
        return 10.0

    def get_current(self) -> float:
        return 10.0

    def set_charging_target(
        self, current: float, min_voltage: float, max_voltage: float
    ):
        print("current: ", current)
        print("min voltage: ", min_voltage)
        print("max voltage: ", max_voltage)
        return None
