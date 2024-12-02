from typing import Optional

from base_classes import ElectricVehicle, ChargingState, ProximityPilotResitorValue

class MockEletricVehicle(ElectricVehicle):
    def get_state(self) -> ChargingState:
        print('MockEletricVehicle.get_state')
        return ChargingState.D

    def set_state(self, state: ChargingState):
        print('MockEletricVehicle.set_state', state)

    def set_cable_lock(self, locked: bool):
        print('MockEletricVehicle.set_cable_lock', locked)
        return True

    def get_pwm_duty_cycle(self) -> float:
        print('MockEletricVehicle.get_pwm_duty_cycle')
        return 10.0

    def get_max_charge_current(self) -> int:
        print('MockEletricVehicle.get_max_charge_current')
        return 10

    def set_max_charge_current(self, resistance: Optional[ProximityPilotResitorValue]):
        print('MockEletricVehicle.set_max_charge_current', resistance)
