import chargebyte_board


class CharbyteChargingStation:
    def __init__(self, host, port):
        self.cbb = chargebyte_board.ChargebyteBoard(host, port)

    def isVehicleDetected(self) -> bool:
        pass

    def isChargingReady(self) -> bool:
        pass

    def setPWM(self, dutycycle: float):
        self.enablePWM()
        self.cbb.set_pwm(1000, dutycicle)

    def enablePWM(self)->None:
        cbb.control_pwm(chargebyte_board.ControlCode(1))


