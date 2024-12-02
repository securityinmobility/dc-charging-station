from base_classes import ChargingState
from base_classes import ChargingStation
from base_classes import ProximityPilotResitorValue


class MockChargingStation(ChargingStation):
    def get_state(self) -> ChargingState:
        print('MockChargingStation.get_state')
        return ChargingState.C

    def set_cable_lock(self, locked: bool):
        print('MockChargingStation.set_cable_lock', locked)
        return None

    def set_pwm_duty_cycle(self, dutycycle: float):
        print('MockChargingStation.set_pwm_duty_cycle', dutycycle)

    def get_max_charge_current(self) -> ProximityPilotResitorValue:
        print('MockChargingStation.get_max_charge_current')
        return ProximityPilotResitorValue.Charge13A

    def set_max_charge_current(self, current: int):
        print('MockChargingStation.set_max_charge_current', current)
