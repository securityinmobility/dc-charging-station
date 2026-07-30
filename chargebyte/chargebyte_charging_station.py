from base_classes import ChargingStation, ChargingState, ProximityPilotResitorValue
from chargebyte.chargebyte_board import (
    ChargebyteBoard,
    ResistorCode,
    ControlCode,
    CableLock,
)
from typing_extensions import override
import sys
from time import sleep

sys.path.append("..")


class ChargebyteChargingStation(ChargingStation):
    def __init__(
        self, host, port, set_pp_resistor: bool = False
    ):
        """receives host and port. sets frequency to the most used frequency of 1000Hz."""
        self.cbb = ChargebyteBoard(host, port)

        self.enable_pp_resistor(ResistorCode.Ohm_1500)

        """
        if set_pp_resistor:
            self.cbb.activate_proximity_pilot_resistor(ResistorCode.Ohm_100)
        self.cbb.control_pwm(ControlCode.ENABLE)
        self.cbb.enable_proximity_pilot_pullup_5V()
        # set constant 12V output (or PWM) ?
        while self.get_state() == ChargingState.A:
            sleep(2.0 / 100)
        self.cbb.set_pwm(self.frequency, 50)
        while self.get_state() == ChargingState.B:
            sleep(2.0 / 100)
        """

    # specific Chargebyte functions
    def enable_pp_resistor(self, resistance = ResistorCode.Ohm_100):
        self.cbb.activate_proximity_pilot_resistor(resistance)

    def disable_pp_resistor(self):
        self.cbb.activate_proximity_pilot_resistor(ResistorCode.OFF)

    @override
    def set_cable_lock(self, locked: bool):
        """Returns None
        Can be used to lock or unlock both cables. if locked is True, both cables will be locked, otherwise both will be unlocked. Doesn't check for the current situation.
        """
        if locked:
            self.cbb.lock_unlock_cable_one(CableLock(1))
            self.cbb.lock_unlock_cable_two(CableLock(1))
        else:
            self.cbb.lock_unlock_cable_one(CableLock(0))
            self.cbb.lock_unlock_cable_two(CableLock(0))

    def is_vehicle_detected(self) -> bool:
        """Returns bools
        Tells if the vehicle was detected or not
        """
        if self.get_state != ChargingState.A:
            return True
        return False

    def get_pwm(self) -> tuple:
        """returns one int and one float

        the int represents the frequency in Hz
        the float represents the dutycycle, with precision 0.1
        """
        frequency, duty_cycle_int = self.cbb.get_pwm()
        duty_cycle = float(duty_cycle_int) * 0.1
        return frequency, duty_cycle

    def get_pwm_duty_cycle(self):
        """returns duty_cycle, already converted to %."""
        _, duty_cycle = self.bcc.get_pwm()
        duty_cycle = float(duty_cycle) * 0.1
        return duty_cycle

    @override
    def set_pwm_duty_cycle(self, duty_cycle: float):
        """
        dutycicle in float represents the % of the cycle. the precision is 0.1, which means floats such as 50,456543 will become 50,4%.
        """
        if duty_cycle == 0:
            self.cbb.control_pwm(ControlCode.DISABLE)
        else:
            self.cbb.control_pwm(ControlCode.ENABLE)
            self.cbb.set_pwm(1000, int(duty_cycle * 10))

    def get_max_charge_current(self) -> ProximityPilotResitorValue:
        precision = 3
        resistance = self.cbb.get_voltage_of_proximity_signal()
        if resistance - 100 <= precision:
            return ProximityPilotResitorValue(100)
        if resistance - 220 <= precision:
            return ProximityPilotResitorValue(220)
        if resistance - 680 <= precision:
            return ProximityPilotResitorValue(680)
        if resistance - 1500 <= precision:
            return ProximityPilotResitorValue(1500)
        raise Exception("Something went wrong: unexpected result for resistance")

    @override
    def get_state(self) -> ChargingState:
        """returns ChargingState enum.
        Gets the current state of the system.
        """
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
