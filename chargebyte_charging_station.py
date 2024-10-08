import chargebyte_board
from base_classes import ChargingStation, ChargingState


class CharbyteChargingStation(ChargingStation):

    def __init__(self, host, port):
        self.cbb = chargebyte_board.ChargebyteBoard(host, port)


    def set_cable_lock(self, locked: bool):
        pass


    def is_vehicle_detected(self) -> bool:
        if self.get_state != ChargingState.A :
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


    def set_pwm_duty_cycle(self, dutycycle: float):
        self.set_pwm( self.frequency, duty_cycle )


    def get_max_charge_current(self) -> ProximityPilotResitorValue:
        pass


    def set_max_charge_current(self, current: int):
        pass


    def set_pwm(self, frequency:int, duty_cycle:float):
        """
        frequency in Hz, usually 1000
        dutycicle in float represents the % of the cycle. the precision is 0.1, which means floats such as 50,456543 will become 50,4%.
        """
        self.enable_pwm()
        duty_cycle = int( duty_cycle*10 )
        self.cbb.set_pwm(frequency, duty_cycle)


    def enable_pwm(self):
        cbb.control_pwm(chargebyte_board.ControlCode(1))


    def get_state(self) -> ChargingState:
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


    """def ist_charge_possible(self) -> bool:
        state = this.get_state()
        if state == 'A':
            return False
        if state == 'B':
            return False
        if state == 'C':
            return True
        if state == 'D':
            return True
        if state == 'E':
            return False
        if state == 'F':
            return False"""


