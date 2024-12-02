from time import sleep
from chargebyte_board import *

IP = '192.168.188.250'
port = 2020

cbb = ChargebyteBoard(IP,port)

print('test device 2, build and last reset reason', cbb.test_device_two())
print('test device one. software version, hardware version and last reset reason',cbb.test_device_one())

input()
print('reset the system', cbb.reset())

print('enabling pwm', cbb.control_pwm(1))
sleep(0.5)
print('set pwm',cbb.set_pwm(1000, 500))
print('get pwm, should be 1000 and 50% ',cbb.get_pwm())
input()
print('set pwm',cbb.set_pwm(1000, 50))
print('get pwm, should be 1000 and 50% ',cbb.get_pwm())

input()
print('reset the system', cbb.reset())

print('enabling pwm', cbb.control_pwm(1))
print('set pwm',cbb.set_pwm(1000, 500))
input()
print('set cp',cbb.set_cp(3047))
input()
print('set cp',cbb.set_cp(2700))
input()
print('set cp',cbb.set_cp(1300))

#print('disable cable 1', cbb.lock_unlock_cable_one(ControlCode(0)))
#print('query cable 1, should be disabled or 1', cbb.lock_unlock_cable_one(ControlCode(2)))
#print('enable cable 2', cbb.lock_unlock_cable_two(ControlCode(1)))
#print('query cable 2, should be on or 0', cbb.lock_unlock_cable_two(ControlCode(2)))

input()
print('reset the system', cbb.reset())
print('get motor fault pin',cbb.get_motor_fault_pin())


#TODO:cyclic process data

input()
print('reset the system', cbb.reset())
print('push button connect', cbb.push_button_simple_connect(1))



input()
print('reset the system', cbb.reset())

print('set PP resistor 2700', cbb.activate_proximity_pilot_resistor(ResistorCode.Ω_2700.value))
input()
print('set PP resistor 150', cbb.activate_proximity_pilot_resistor(ResistorCode.Ω_150.value))
input()
print('set PP resistor 680', cbb.activate_proximity_pilot_resistor(ResistorCode.Ω_680.value))

input()
print('reset the system', cbb.reset())
print('enable pullup resistor = ',cbb.enable_pullup_resistor())

input()
print('reset the system', cbb.reset())
print('disable pullup resistor = ',cbb.disable_pullup_resistor())

input()
print('reset the system', cbb.reset())

print('enable pullup resistor = ',cbb.enable_pullup_resistor())
print('voltage of proximity signal = ',cbb.get_voltage_of_proximity_signal())
