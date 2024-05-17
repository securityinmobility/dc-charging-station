from controllingChargebyteBoard import *
import socket
import pytest
import unittest.mock as mock
import time
from multipledispatch import dispatch
from typing import overload


@pytest.fixture(autouse=True)
def mock_socket(mocker):
    mock_socket = mock.Mock()
    mock_socket.recv = mock.Mock()
    return mock_socket


@pytest.fixture(autouse=True)
def control(mocker, mock_socket):
    HOST = socket.gethostname()
    PORT = 4040  # The port used by the server
    mocker.patch('socket.socket', return_value = mock_socket)
    control = controllingChargebyteBoard(HOST,PORT)

    return control


def xor_calculator(parameter:list[int])-> int:
    answer = parameter[0]
    for number in parameter[1:]:
        answer = answer ^ number
    return answer


class TestChargeboardByte:

    def test_check_block_sum(self, control):
        data = [0x10,0x00,0x01]
        expected = 0x11
        assert control.check_block_sum(data) == expected


    def test_should_check_length(self,control,mock_socket):
        data = bytearray([0x02,0x06,0x00,0x95,0x15,0x07,0x02])
        data.append(xor_calculator(data))
        mock_socket.recv.side_effect = [data[0], data[1], data[2:]]
        with pytest.raises(Exception)as info:
            control.set_ucp(2)
        assert info.value.args[0] == 'Wrong length! something went wrong!'


    def test_should_verify_service_id(self,control,mock_socket):
        data = bytearray([0x02,0x06,0x00,0x81,0x81,0x81,0x02])
        data.append(xor_calculator(data))
        mock_socket.recv.side_effect = [data[0], data[1], data[2:]]
        with pytest.raises(Exception)as info:
            control.send_packet(0x51, bytearray())
        assert info.value.args[0] == 'this response does not corresponds to the service that was requested'


    def test_should_time_out(self, control, mock_socket):
        pass # i dont know how to implement this one


    def test_incorrect_checksum(self,control,mock_socket):
        data = bytearray([0x02,0x06,0x00,0x81,0x81,0x81,0x02])
        data.append(xor_calculator(data)+2)#check sum needs to be wrong
        mock_socket.recv.side_effect = [data[0], data[1], data[2:]]
        with pytest.raises(Exception)as info:
            control.send_packet(0x01, bytearray())
        assert info.value.args[0] == 'Something went wrong: the check block is wrong!'


    def test_should_start_with_answer_code(self,control,mock_socket):
        data = bytearray([0x05,0x04,0x00,0x95,0x1])
        data.append(xor_calculator(data))
        mock_socket.recv.side_effect = [data[0], data[1], data[2:]]
        with pytest.raises(Exception)as info:
            control.set_ucp(2)
        assert info.value.args[0] == 'beginning of message was not 0x02'


    def test_test_device_one(self, control, mock_socket):
        data = bytearray([0x02,0x06,0x00,0x81,0x81,0x81,0x02])
        data.append(xor_calculator(data))
        mock_socket.recv.side_effect = [data[0], data[1], data[2:]]
        expected_request = bytearray([0x02,0x03,0x00,0x01])
        expected_request.append(xor_calculator(expected_request))
        software_number, hardware_number, reset_value = control.test_device_one()
        mock_socket.send.assert_called_once_with(expected_request)
        assert software_number == 0x81
        assert hardware_number == 0x81
        assert reset_value.value == 0x02


    def test_test_device_two(self, control, mock_socket):
        data = bytearray([0x02,0x06,0x00,0x84,0x07,0x00,0x02])
        data.append(xor_calculator(data))
        mock_socket.recv.side_effect = [data[0], data[1], data[2:]]
        build, reset_value = control.test_device_two()
        assert build == 7
        assert reset_value.value == 0x02
        expected_request = bytearray([0x02,0x03,0x00,0x04])
        expected_request.append(xor_calculator(expected_request))
        mock_socket.send.assert_called_once_with(expected_request)


    def test_set_pwm(self,control,mock_socket):
        data = bytearray([0x02,0x04,0x00,0x91,0x00])
        data.append(xor_calculator(data))
        mock_socket.recv.side_effect = [data[0], data[1], data[2:]]
        control.set_pwm(2,3)
        expected_request = bytearray([0x02,0x07,0x00,0x11,0x02,0x00,0x03,0x00])
        expected_request.append(xor_calculator(expected_request))
        mock_socket.send.assert_called_once_with(expected_request)


    def test_get_pwm(self,control,mock_socket):
        data = bytearray([0x02,0x07,0x00,0x90,0x02,0x00,0x03,0x00])
        data.append(xor_calculator(data))
        mock_socket.recv.side_effect = [data[0], data[1], data[2:]]
        frequency, dutycicle = control.get_pwm()
        assert frequency == 2
        assert dutycicle == 3
        expected_request = bytearray([0x02,0x03,0x00,0x10])
        expected_request.append(xor_calculator(expected_request))
        mock_socket.send.assert_called_once_with(expected_request)


    def test_control_pwm(self,control,mock_socket):
        data = bytearray([0x02,0x04,0x00,0x92,0x01])
        data.append(xor_calculator(data))
        mock_socket.recv.side_effect = [data[0], data[1], data[2:]]
        control_code = control.control_pwm(1)
        assert control_code.value == 1
        expected_request = bytearray([0x02,0x04,0x00,0x12,0x01])
        expected_request.append(xor_calculator(expected_request))
        mock_socket.send.assert_called_once_with(expected_request)


    def test_get_ucp(self,control,mock_socket):
        data = bytearray([0x02,0x07,0x00,0x94,0x06,0x00,0x02,0x00])
        data.append(xor_calculator(data))
        mock_socket.recv.side_effect = [data[0], data[1], data[2:]]
        positive_cp, negative_cp = control.get_ucp()
        assert positive_cp == 6
        assert negative_cp == 2
        expected_request = bytearray([0x02,0x03,0x00,0x14])
        expected_request.append(xor_calculator(expected_request))
        mock_socket.send.assert_called_once_with(expected_request)


    def test_set_ucp(self,control,mock_socket):
        data = bytearray([0x02,0x04,0x00,0x95,0x01])
        data.append(xor_calculator(data))
        mock_socket.recv.side_effect = [data[0], data[1], data[2:]]
        resistance = control.set_ucp(1)
        assert resistance == 1
        expected_request = bytearray([0x02,0x04,0x00,0x15,0x01])
        expected_request.append(xor_calculator(expected_request))
        mock_socket.send.assert_called_once_with(expected_request)


    def test_lock_and_unlock_cable_one(self,control,mock_socket):
        data = bytearray([0x02,0x04,0x00,0x97,0x01])
        data.append(xor_calculator(data))
        mock_socket.recv.side_effect = [data[0], data[1], data[2:]]
        answer = control.lock_unlock_cable_one(2)
        assert answer.value == 1
        expected_request = bytearray([0x02,0x04,0x00,0x17,0x02])
        expected_request.append(xor_calculator(expected_request))
        mock_socket.send.assert_called_once_with(expected_request)


    def test_lock_and_unlock_cable_two(self,control,mock_socket):
        data = bytearray([0x02,0x04,0x00,0x98,0x01])
        data.append(xor_calculator(data))
        mock_socket.recv.side_effect = [data[0], data[1], data[2:]]
        answer = control.lock_unlock_cable_two(2)
        assert answer.value == 1
        expected_request = bytearray([0x02,0x04,0x00,0x18,0x02])
        expected_request.append(xor_calculator(expected_request))
        mock_socket.send.assert_called_once_with(expected_request)


    def test_get_motor_fault_pin(self,control,mock_socket):
        data = bytearray([0x02,0x04,0x00,0x9A,0x81])
        data.append(xor_calculator(data))
        mock_socket.recv.side_effect = [data[0], data[1], data[2:]]
        answer = control.get_motor_fault_pin()
        assert answer.value == 1
        expected_request = bytearray([0x02,0x03,0x00,0x1A])
        expected_request.append(xor_calculator(expected_request))
        mock_socket.send.assert_called_once_with(expected_request)


    def test_set_cyclic_process_data(self,control,mock_socket):
        data = bytearray([0x02,0x04,0x00,0xA0,0x01])
        data.append(xor_calculator(data))
        mock_socket.recv.side_effect = [data[0], data[1], data[2:]]
        answer = control.set_cyclic_process_data(4)
        assert answer.value == 1
        expected_request = bytearray([0x02,0x04,0x00,0x20,0x04])
        expected_request.append(xor_calculator(expected_request))
        mock_socket.send.assert_called_once_with(expected_request)


    def test_cyclic_process_data(self,control,mock_socket):
        pass


    def test_push_button_simple_connect(self,control,mock_socket):
        data = bytearray([0x02,0x04,0x00,0xB1,0x00])
        data.append(xor_calculator(data))
        mock_socket.recv.side_effect = [data[0], data[1], data[2:]]
        answer = control.push_button_simple_connect(1)
        assert answer.value == 0
        expected_request = bytearray([0x02,0x04,0x00,0x31,0x01])
        expected_request.append(xor_calculator(expected_request))
        mock_socket.send.assert_called_once_with(expected_request)


    def test_reset(self,control,mock_socket):
        data = bytearray([0x02,0x04,0x00,0xB3,0x00])
        data.append(xor_calculator(data))
        mock_socket.recv.side_effect = [data[0], data[1], data[2:]]
        control.reset()
        expected_request = bytearray([0x02,0x03,0x00,0x33])
        expected_request.append(xor_calculator(expected_request))
        mock_socket.send.assert_called_once_with(expected_request)


    def test_activate_proximity_pilot_resistor_(self,control,mock_socket):
        data = bytearray([0x02,0x04,0x00,0xD0,0x00])
        data.append(xor_calculator(data))
        mock_socket.recv.side_effect = [data[0], data[1], data[2:]]
        answer = control.activate_proximity_pilot_resistor(0x06)
        assert answer.value == 0
        expected_request = bytearray([0x02,0x04,0x00,0x50,0x06])
        expected_request.append(xor_calculator(expected_request))
        mock_socket.send.assert_called_once_with(expected_request)


    def test_enable_pullup_resistor(self, control, mock_socket):
        data = bytearray([0x02,0x04,0x00,0xD1,0x00])
        data.append(xor_calculator(data))
        mock_socket.recv.side_effect = [data[0], data[1], data[2:]]
        answer = control.enable_pullup_resistor()
        expected_request = bytearray([0x02,0x04,0x00,0x51,0x03])
        expected_request.append(xor_calculator(expected_request))
        mock_socket.send.assert_called_once_with(expected_request)


    def test_disable_pullup_resistor(self, control, mock_socket):
        data = bytearray([0x02,0x04,0x00,0xD1,0x00])
        data.append(xor_calculator(data))
        mock_socket.recv.side_effect = [data[0], data[1], data[2:]]
        answer = control.disable_pullup_resistor()
        expected_request = bytearray([0x02,0x04,0x00,0x51,0x00])
        expected_request.append(xor_calculator(expected_request))
        mock_socket.send.assert_called_once_with(expected_request)


    def test_get_voltage_of_proximity_signal(self, control, mock_socket):
        data = bytearray([0x02,0x05,0x00,0xD2,0x07,0x00])
        data.append(xor_calculator(data))
        mock_socket.recv.side_effect = [data[0], data[1], data[2:]]
        answer = control.get_voltage_of_proximity_signal()
        assert answer == 7
        expected_request = bytearray([0x02,0x03,0x00,0x52])
        expected_request.append(xor_calculator(expected_request))
        mock_socket.send.assert_called_once_with(expected_request)




