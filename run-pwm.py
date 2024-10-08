import time
from chargebyte_board import ChargebyteBoard, ControlPWM

# run the following command on the chargebyte board to make this work:
# socat tcp-l:2020,reuseaddr,fork,crlf file:/dev/ttyAPP2,echo=0,b57600,raw

board = ChargebyteBoard("192.168.188.250", 2020)

board.control_pwm(1)
board.set_pwm(1000, 500)
time.sleep(1)

print(board.get_pwm())
