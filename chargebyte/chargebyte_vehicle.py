from base_classes import ElectricVehicle
import chargebyte_board
from chargebyte_board import ChargingState
from typing import override
import sys
from time import sleep

sys.path.append("..")


class ChargebyteVehicle(ElectricVehicle):
    def __init__(
        self,
        host,
        port,
        cp_resistance: int,
        set_pp_resistor: bool = False,
        resistance: int = 100,
    ):
        self.cbb = chargebyte_board.ChargebyteBoard(host, port)
        self.frequency = 1000  # most used frequency, we can change later
        if set_pp_resistor:
            self.cbb.activate_proximity_pilot_resistor(
                chargebyte_board.ResistorCode.Ohm_100
            )
        self.cbb.disable_proximity_pilot_pullup_5V()
        self.cbb.control_pwm(chargebyte_board.ControlCode.DISABLE)
        self.cbb.set_cp(cp_resistance)
        while self.get_state() == ChargingState.A:
            sleep(2.0 / 100)
        sleep(1)
        # set second CP resistor

    @override
    def get_state(self) -> ChargingState:
        precision_interval = 0.3
        positive_voltage, negative_voltage = self.cbb.get_ucp()
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
    def set_cable_lock(self, locked: bool):
        if locked:
            self.cbb.lock_unlock_cable_one(chargebyte_board.ControlCode(1))
            self.cbb.lock_unlock_cable_two(chargebyte_board.ControlCode(1))
        else:
            self.cbb.lock_unlock_cable_one(chargebyte_board.ControlCode(0))
            self.cbb.lock_unlock_cable_two(chargebyte_board.ControlCode(0))

    @override
    def get_pwm_duty_cycle(self) -> float:
        _, duty_cycle = self.bcc.get_pwm()
        duty_cycle = float(duty_cycle) * 0.1
        return duty_cycle

    @override
    def set_max_charge_current(self, resistance: ProximityPilotResitorValue) -> None:
        if resistance.value == 100:
            self.cbb.activate_proximity_pilot_resistor(ResistorCode.Ohm_100)
        if resistance.value == 220:
            self.cbb.activate_proximity_pilot_resistor(ResistorCode.Ohm_220)
        if resistance.value == 680:
            self.cbb.activate_proximity_pilot_resistor(ResistorCode.Ohm_680)
        if resistance.value == 1500:
            self.cbb.activate_proximity_pilot_resistor(ResistorCode.Ohm_1500)
