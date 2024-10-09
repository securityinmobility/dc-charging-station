from abc import ABC
from enum import Enum

class ChargingState(Enum):
    """
    Charging state as described in DIN EN 61851-1:2012
    For a short summary see: https://evsim.gonium.net/#der-control-pilot-cp
    """
    A = 'A'
    B = 'B'
    C = 'C'
    D = 'D'
    E = 'E'
    F = 'F'

class ProximityPilotResitorValue(Enum):
    """
    Resistance values between PP and PE as defined in DIN EN 61851-1:2012
    For a short summary see: https://evsim.gonium.net/#der-proximity-plug-pp
    """
    Charge63A = 100
    Charge32A = 220
    Charge20A = 680
    Charge13A = 1500

class ChargingStation(ABC):
    def get_state(self) -> ChargingState:
        """
        Get the current charging state according to the voltage measured between CP and PE
        """
        raise NotImplementedError()

    def set_cable_lock(self, locked: bool):
        """
        Lock or release the charging cable
        """
        raise NotImplementedError()

    def set_pwm_duty_cycle(self, dutycycle: float):
        """
        Set the dutycycle of the PWM between CP and PE.
        The parameter dutycycle is in %. Thus a value of 20 refers to 10A charging current.
        A value of 5 signals the vehicle to use higher level communication.
        """
        raise NotImplementedError()

    def get_max_charge_current(self) -> ProximityPilotResitorValue:
        """
        Get the current resistance between PP and PE in Ohms, which defines the maximum current of the cable.
        This value is usually ignored in ISO15118 use cases, but important for AC charging stations.
        If the resistance is not one of the values defined in DIN EN 61851-1:2012 this function shall raise a ValueError
        """
        raise NotImplementedError()

    def set_max_charge_current(self, current: int):
        """
        Signal the vehicle the maximum allowed current to be drawn (through the PWM signal between CP and PE).
        This is usually only used for AC charging.
        This function raises a ValueError for too high or too low current values.
        """
        if current < 6:
            raise ValueError("Charge current cannot be lower than 6A")
        elif current <= 51:
            self.set_pwm_duty_cycle(current / 0.6)
        elif current <= 80:
            self.set_pwm_duty_cycle(current / 2.5 + 64)
        else:
            raise ValueError("Charge current cannot be higher than 80A")

class ElectricVehicle(ABC):
    def get_state(self) -> ChargingState:
        """
        Get the current charging state according to the voltage measured between CP and PE
        """
        raise NotImplementedError()

    def set_cable_lock(self, locked: bool):
        """
        Lock or release the charging cable
        """
        raise NotImplementedError()

    def get_pwm_duty_cycle(self) -> float:
        """
        Get the current duty cycle of the PWM signal CP and PE in %
        """
        raise NotImplementedError()

    def get_max_charge_current(self) -> int:
        """
        Calculate the maximum charge current communicated by the charging
        station through the dutycycle of the PWM between CP and PE.
        The returned value is in Ampere.
        """
        dutycycle = self.get_pwm_duty_cycle()
        # we give a PWM tolerance based on the rounding error from float to int
        if dutycycle < 5.5 / 0.6 or dutycycle >= 80.5 / 2.5 + 64:
            raise ValueError(f"Unexpected dutycycle value of {dutycycle}%")

        if dutycycle < 85:
            return round(dutycycle * 0.6)
        else:
            return round((dutycycle - 64) * 2.5)

    def set_max_charge_current(self, resistance: ProximityPilotResitorValue):
        """
        Set the maximum charge current communicated to the vehicle through the
        resistor between PP and PE.

        This is only used for AC charging and most of the times already included
        in the charging cable.
        """
        raise NotImplementedError()

class HighVoltageSource(ABC):
    def check_insulation(self) -> bool:
        """
        Perform insulation and cable checks.
        Return True when successful, False otherwise.
        """
        raise NotImplementedError()

    def get_voltage(self) -> float:
        """
        Get the current voltage measured
        """
        raise NotImplementedError()

    def get_current(self) -> float:
        """
        Get the current amperage going into (or out of) the battery
        Positive means charging, negative means discharging.
        """
        raise NotImplementedError()

    def set_charging_target(self, current: float, min_voltage: float, max_voltage: float):
        """
        Set the target parameters for charging.
        The goal is to charging/discharging the battery with `current` amps,
        appying a minimum and maximum voltage of `min_voltage` and
        `max_voltage` Volts respectively.
        Positive `current` means charging, negative means discharging.

        If the device supports only one of charging and discharging, but the
        other one is requested, this function shall throw a ValueError.
        """
        raise NotImplementedError()
