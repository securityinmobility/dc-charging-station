import time
import sys

sys.path.insert(0, "...")
from chargebyte.chargebyte_board import ChargebyteBoard, ControlCode, ResistorCode

# run the following command on the chargebyte board to make this work:
# socat tcp-l:2020,reuseaddr,fork,crlf file:/dev/ttyAPP2,echo=0,b57600,raw

board = ChargebyteBoard("192.168.188.250", 2020)

board.control_pwm(ControlCode.DISABLE)
time.sleep(5)

# board.disable_pullup_resistor()
board.activate_proximity_pilot_resistor(ResistorCode.OFF)
time.sleep(1)

print(board.get_pwm())
print(board.get_cp())
