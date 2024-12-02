import sys
from time import sleep
#sys.path.append("..")

from base_classes import ElectricVehicle, ChargingState
from chargebyte.chargebyte_board import ResistorCode, ControlCode
from chargebyte.chargebyte_board import ChargebyteBoard, CableLock
from typing_extensions import override
from base_classes import ProximityPilotResitorValue

class ChargebyteVehicle(ElectricVehicle):
    def __init__(
        self, host, port, set_pp_resistor: bool = False, resistance: int = 100
    ):
        self.cbb = ChargebyteBoard(host, port)
        self.frequency = 1000
        if set_pp_resistor:
            self.cbb.activate_proximity_pilot_resistor(ResistorCode.Ohm_100)
        self.cbb.disable_proximity_pilot_pullup_5V()
        self.cbb.control_pwm(ControlCode.DISABLE)
        self.cbb.set_cp(2700)
        while self.get_state() == ChargingState.A:
            sleep(2.0 / 100)
        sleep(1)
        self.cbb.set_cp(2700 + 1300)

    @override
    def get_state(self) -> ChargingState:
        precision_interval = 0.3
        positive_voltage, negative_voltage = self.cbb.get_cp()
        if abs(positive_voltage - 12) <= precision_interval:
            return ChargingState.A
        if abs(positive_voltage - 9) <= precision_interval:
            return ChargingState.B
        if abs(positive_voltage - 6) <= precision_interval:
            return ChargingState.C
        if abs(positive_voltage - 3) <= precision_interval:
            return ChargingState.D
        if abs(positive_voltage - 0) <= precision_interval:
            return ChargingState.E
        return ChargingState.E

    @override
    def set_state(self, state: ChargingState):
        if state == ChargingState.A:
            self.cbb.set_cp(0)
        elif state == ChargingState.B:
            self.cbb.set_cp(2700)
        elif state == ChargingState.C:
            self.cbb.set_cp(2700 + 1200)
        else:
            raise NotImplementedError(f"requested ChargingState {state} not implemented yet")

    @override
    def set_cable_lock(self, locked: bool):
        if locked:
            self.cbb.lock_unlock_cable_one(CableLock(1))
            self.cbb.lock_unlock_cable_two(CableLock(1))
        else:
            self.cbb.lock_unlock_cable_one(CableLock(0))
            self.cbb.lock_unlock_cable_two(CableLock(0))

    @override
    def get_pwm_duty_cycle(self) -> float:
        _, duty_cycle_int = self.cbb.get_pwm()
        duty_cycle = float(duty_cycle_int) * 0.1
        return duty_cycle

    @override
    def set_max_charge_current(self, resistance: Optional[ProximityPilotResitorValue]) -> None:
        if resistance is None:
            self.cbb.activate_proximity_pilot_resistor(ResistorCode.OFF)
        elif resistance.value == 100:
            self.cbb.activate_proximity_pilot_resistor(ResistorCode.Ohm_100)
        elif resistance.value == 220:
            self.cbb.activate_proximity_pilot_resistor(ResistorCode.Ohm_220)
        elif resistance.value == 680:
            self.cbb.activate_proximity_pilot_resistor(ResistorCode.Ohm_680)
        elif resistance.value == 1500:
            self.cbb.activate_proximity_pilot_resistor(ResistorCode.Ohm_1500)
