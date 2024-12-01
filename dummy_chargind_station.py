from base_classes import ChargingState
from base_classes import ChargingStation
from base_classes import ProximityPilotResitorValue


class DummyChargingStation(ChargingStation):
    def get_state(self) -> ChargingState:
        return ChargingState.D

    def set_cable_lock(self, locked: bool):
        print(locked)
        return None

    def set_pwm_duty_cycle(self, dutycycle: float):
        print(dutycycle)
        return None

    def get_max_charge_current(self) -> ProximityPilotResitorValue:
        return ProximityPilotResitorValue.Charge13A

    def set_max_charge_current(self, current: int):
        print(current)
        return None
