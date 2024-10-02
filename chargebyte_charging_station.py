import chargebyte_board


class CharbyteChargingStation:
    def __init__(self, host, port):
        self.cbb = chargebyte_board.ChargebyteBoard(host, port)

    def isVehicleDetected(self) -> bool:
        pass

    def isChargingReady(self) -> bool:
        pass

    def get_pwm(self):
        frequency, duty_cycle = self.bcc.get_pwm()
        duty_cycle = float(duty_cycle)*0.1
        return frequency, duty_cycle


    def setPWM(self, frequency:int, duty_cycle: float):
        self.enablePWM()
        duty_cycle = int( duty_cycle*10 )
        self.cbb.set_pwm(frequency, duty_cycle)

    def enablePWM(self)->None:
        cbb.control_pwm(chargebyte_board.ControlCode(1))


