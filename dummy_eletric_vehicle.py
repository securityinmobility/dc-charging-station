from typing import Optional

from base_classes import ElectricVehicle, ChargingState, ProximityPilotResitorValue

class MockEletricVehicle(ElectricVehicle):
    def get_state(self) -> ChargingState:
        return ChargingState.D

    def set_state(self, state: ChargingState):
        print(state)

    def set_cable_lock(self, locked: bool):
        return True

    def get_pwm_duty_cycle(self) -> float:
        return 10.0

    def get_max_charge_current(self) -> int:
        return 10

    def set_max_charge_current(self, resistance: Optional[ProximityPilotResitorValue]):
        print(resistance)
