import chargebyte_board
from base_classes import ChargingStation, ChargingState


class CharbyteChargingStation(ChargingStation):

    def __init__(self, host, port):
        """receives host and port. sets frequency to the most used frequency of 1000Hz.
        """
        self.cbb = chargebyte_board.ChargebyteBoard(host, port)
        self.frequency = 1000 #most used frequency, we can change later

    @override
    def set_cable_lock(self, locked: bool):
        """Returns None
        Can be used to lock or unlock both cables. if locked is True, both cables will be locked, otherwise both will be unlocked. Doesn't check for the current situation.
        """
        if(locked):
            self.cbb.lock_unlock_cable_one(chargebyte_board.ControlCode(1))
            self.cbb.lock_unlock_cable_two(chargebyte_board.ControlCode(1))
        else:
            self.cbb.lock_unlock_cable_one(chargebyte_board.ControlCode(0))
            self.cbb.lock_unlock_cable_two(chargebyte_board.ControlCode(0))


    def is_vehicle_detected(self) -> bool:
        """Returns bools
        Tells if the vehicle was detected or not
        """
        if self.get_state != ChargingState.A:
            return True
        return False


    def get_pwm(self) -> [int,float]:
        """returns one int and one float

        the int represents the frequency in Hz
        the float represents the dutycycle, with precision 0.1
        """
        frequency, duty_cycle = self.bcc.get_pwm()
        duty_cycle = float(duty_cycle)*0.1
        return frequency, duty_cycle


    def get_pwm_duty_cycle(self):
        """returns duty_cycle, already converted to %.
        """
        _, duty_cycle = self.bcc.get_pwm()
        duty_cycle = float(duty_cycle)*0.1
        return duty_cycle


    @override
    def set_pwm_duty_cycle(self, duty_cycle:float):
        """
        dutycicle in float represents the % of the cycle. the precision is 0.1, which means floats such as 50,456543 will become 50,4%.
        """
        self.enable_pwm()
        duty_cycle = int(duty_cycle*10)
        self.cbb.set_pwm(self.frequency, duty_cycle)


    def enable_pwm(self):
        """returns None
        PWM needs to be enabled before we can control it.
        """
        self.cbb.control_pwm(chargebyte_board.ControlCode(1))


    @override
    def get_state(self) -> ChargingState:
        """ returns ChargingState enum.
        Gets the current state of the system.
        """
        precision_interval = 0.3
        positive_voltage, negative_voltage = self.cbb.get_ucp()
        if abs(positive_voltage - 12) <= precision_interval:
            return ChargingState.A
        if abs(positive_voltage - 9) <= precision_interval:
            return ChargingState.B
        if abs( positive_voltage - 6 ) <= precision_interval:
            return ChargingState.C
        if abs( positive_voltage - 3 ) <= precision_interval:
            return ChargingState.D
        if abs( positive_voltage - 0 ) <= precision_interval:
            return ChargingState.E
        return ChargingState.E


    def is_charging_possible(self) -> bool:
        """Returns bool
        tells if we can initiate the chargind
        """
        state = this.get_state()
        if state == ChargingStation.C or state == ChargingStation.D:
            return True
        return False


    @override
    def get_max_charge_current(self):
        """returns the voltage in Volts
        converts the volt from the hardware, which has the resolution of 29mV/bit to volts
        """
        return float(self.cbb.get_voltage_of_proximity_signal())*29.0/1000.0


    @override
    def set_max_charge_current(self, current: int):
        pass




