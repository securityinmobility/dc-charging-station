from time import sleep
import sys

sys.path.insert(0, "..")

from chargebyte.chargebyte_vehicle import ChargebyteVehicle
from base_classes import ProximityPilotResitorValue, ChargingState

# run the following command on the chargebyte board to make this work:
# socat tcp-l:2020,reuseaddr,fork,crlf file:/dev/ttyAPP2,echo=0,b57600,raw

vehicle = ChargebyteVehicle("192.168.188.250", 2020)
vehicle.set_max_charge_current(ProximityPilotResitorValue.Charge13A)
vehicle.set_state(ChargingState.A)
sleep(1)
vehicle.set_state(ChargingState.B)
sleep(1)
vehicle.set_state(ChargingState.C)

sleep(1)

print(vehicle.get_pwm_duty_cycle())

# input()
# vehicle.set_state(ChargingState.A)
# TODO turn off PP

"""
import time
from chargebyte_board import ChargebyteBoard, ResistorValue, ResistorCode

# run the following command on the chargebyte board to make this work:
# socat tcp-l:2020,reuseaddr,fork,crlf file:/dev/ttyAPP2,echo=0,b57600,raw

board = ChargebyteBoard("192.168.188.250", 2020)

board.activate_proximity_pilot_resistor(ResistorCode.Ω_100.value)
time.sleep(1)
board.set_ucp(0x01)
time.sleep(1)

print(board.get_ucp())
"""
