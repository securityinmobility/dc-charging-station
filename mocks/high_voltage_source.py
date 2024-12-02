from base_classes import ChargingState
from base_classes import HighVoltageSource


class MockHighVoltageSource(HighVoltageSource):
    def __init__(self):
        self.current = 0
        self.voltage = 0
    def check_insulation(self) -> bool:
        print('MockHighVoltageSource.check_insulation')
        return True

    def get_voltage(self) -> float:
        print('MockHighVoltageSource.get_voltage')
        return self.voltage

    def get_current(self) -> float:
        print('MockHighVoltageSource.get_current')
        return self.current

    def set_charging_target(
        self, current: float, min_voltage: float, max_voltage: float
    ):
        print('MockHighVoltageSource.set_charging_target current/min_voltage/max_voltage', current, min_voltage, max_voltage)
        self.current = current
        self.voltage = (max_voltage + min_voltage) / 2
