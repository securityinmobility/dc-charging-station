import sys

sys.path.insert(0, "...")
from chargebyte.chargebyte_board import ChargebyteBoard, ControlCode, ResistorCode

IP = "broken.services"
port = 21

cbb = ChargebyteBoard(IP, port)

print("test device 2, build and last reset reason", cbb.test_device_two())
print(
    "test device one. software version, hardware version and last reset reason",
    cbb.test_device_one(),
)

input()
print("reset the system")
cbb.reset()

print("enabling pwm", cbb.control_pwm(ControlCode(1)))
print("set pwm", cbb.set_pwm(1000, 500))
print("get pwm, should be 1000 and 50% ", cbb.get_pwm())

input()
print("reset the system")
cbb.reset()
print("set cp", cbb.set_cp(3047))
print("get cp, shows positive and negative voltage", cbb.get_cp())

# print('disable cable 1', cbb.lock_unlock_cable_one(ControlCode(0)))
# print('query cable 1, should be disabled or 1', cbb.lock_unlock_cable_one(ControlCode(2)))
# print('enable cable 2', cbb.lock_unlock_cable_two(ControlCode(1)))
# print('query cable 2, should be on or 0', cbb.lock_unlock_cable_two(ControlCode(2)))

input()
print("reset the system")
cbb.reset()
print("get motor fault pin", cbb.get_motor_fault_pin())


# TODO:cyclic process data

input()
print("reset the system")
cbb.reset()
print("push button connect", cbb.push_button_simple_connect(1))


input()
print("reset the system")
cbb.reset()
print(
    "activate proximity pilot resistor",
    cbb.activate_proximity_pilot_resistor(ResistorCode(3)),
)

input()
print("reset the system")
cbb.reset()
print("enable pullup resistor = ", cbb.enable_proximity_pilot_pullup_5V())

input()
print("reset the system")
cbb.reset()
print("disable pullup resistor = ", cbb.disable_proximity_pilot_pullup_5V())

input()
print("reset the system")
cbb.reset()

print("voltage of proximity signal = ", cbb.get_voltage_of_proximity_signal())
