from base_classes import (
    ChargingStation,
    ChargingState,
    ProximityPilotResitorValue,
    ElectricVehicle,
)
from typing import Optional
import os

from vendors.bmw.mitm_lldc_code.python_lib.mitm_lldc import LLDC


def get_serial_port():
    """detect serial port for OS"""
    return 'COM7' if os.name == 'nt' else '/dev/ttyUSB0'

lldc_instance = LLDC(get_serial_port())


class lldc_ChargingStation(ChargingStation):

    def get_state(self) -> ChargingState:
        """
        Get the current charging state according to the voltage measured between CP and PE.
        """
        measured_cp_state = lldc_instance.get_cp_state()

        pev_to_chargingstate = {
        LLDC.PEV.A: ChargingState.A,
        LLDC.PEV.B: ChargingState.B,
        LLDC.PEV.C: ChargingState.C,
        LLDC.PEV.D: ChargingState.D,
        LLDC.PEV.DIODE_SHORT: ChargingState.E,
        LLDC.PEV.SHORTCIRCUIT: ChargingState.F
        }
        
        return pev_to_chargingstate[measured_cp_state]  
        

    def set_cable_lock(self, locked: bool):
        """
        Lock or release the charging cable
        """

        if locked:
            lldc_instance.set_plugsim(LLDC.PLUG.CONNECTED)
        else:
            lldc_instance.setset_plugsim(LLDC.PLUG.DISCONNECTED)


    def set_pwm_duty_cycle(self, dutycycle: float):
        """
        Set the dutycycle of the PWM between CP and PE.
        The parameter dutycycle is in %. Thus a value of 20 refers to 10A charging current.
        A value of 5 signals the vehicle to use higher level communication.
        """

        lldc_instance.set_evsesim(pwm=dutycycle)


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



class ElectricVehicle(ElectricVehicle):
    def get_state(self) -> ChargingState:
        """
        Get the current charging state according to the voltage measured between CP and PE
        """

        measured_cp_state = lldc_instance.get_cp_state()

        pev_to_chargingstate = {
        LLDC.PEV.A: ChargingState.A,
        LLDC.PEV.B: ChargingState.B,
        LLDC.PEV.C: ChargingState.C,
        LLDC.PEV.D: ChargingState.D,
        LLDC.PEV.DIODE_SHORT: ChargingState.E,
        LLDC.PEV.SHORTCIRCUIT: ChargingState.F
        }
        
        return pev_to_chargingstate[measured_cp_state]


    def set_state(self, state: ChargingState):
        """
        Set the diode/resistor communication (charging state)
        Can raise a NotImplementedError if switching to the given ChargingState is not supported/implemented
        """

        chargingState_to_pev = {
        ChargingState.A: LLDC.PEV.A,
        ChargingState.B: LLDC.PEV.B,
        ChargingState.C: LLDC.PEV.C,
        ChargingState.D: LLDC.PEV.D,
        ChargingState.E: LLDC.PEV.DIODE_SHORT,
        ChargingState.F: LLDC.PEV.SHORTCIRCUIT
        }

        lldc_instance.set_pev_sim(chargingState_to_pev[state])


    def set_cable_lock(self, locked: bool):
        """
        Lock or release the charging cable
        """

        if locked:
            lldc_instance.set_plugsim(LLDC.PLUG.CONNECTED)
        else:
            lldc_instance.set_plugsim(LLDC.PLUG.DISCONNECTED)


    def get_pwm_duty_cycle(self) -> float:
        """
        Get the current duty cycle of the PWM signal CP and PE in %
        """

        return float(lldc_instance.get_cp_pwm())


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

    def set_max_charge_current(self, resistance: Optional[ProximityPilotResitorValue]):
        """
        Set the maximum charge current communicated to the vehicle through the
        resistor between PP and PE.
        Giving None as a parameter shall turn off the resistor.

        This is only used for AC charging and most of the times already included
        in the charging cable.
        """
        raise NotImplementedError()
