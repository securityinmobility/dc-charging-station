from controllingChargebyteBoard import *
import socket
import pytest
import unittest.mock as mock
import time


@pytest.fixture(autouse=True)
def mock_socket(mocker):
    mock_socket = mock.Mock()
    return mock_socket


@pytest.fixture(autouse=True)
def control(mocker, mock_socket):
    HOST = socket.gethostname()
    PORT = 4040  # The port used by the server
    mocker.patch('socket.socket', return_value = mock_socket)
    control = controllingChargebyteBoard(HOST,PORT)

    return control


def xor_calculator( parameters:list[int] ) -> int:
    answer = parameters [0]
    for number in parameters[1:]:
        answer = answer ^ number
    return answer


class TestChargeboardByte:

    def test_check_length(self,control,mock_socket):
        pass


    def test_should_verify_service_id(self,control,mock_socket):
        data = bytearray([0x00,0x81,0x81,0x81,0x02,0x02])
        mock_socket.recv = mock.Mock()
        mock_socket.recv.side_effect = [0x02, 0x06, data ]
        with pytest.raises(Exception) as info:
            control.send_packet(0x51, bytearray())
        assert info.value.args[0] == 'this response does not corresponds to the service that was requested'


    def test_should_time_out(self, control, mock_socket):
        #control.send_packet( 0x51, bytearray())
        pass


    def test_incorrect_checksum(self,control,mock_socket):
        pass


    def test_answer_code(self,control,mock_socket):
        pass


    def test_test_device(self, control, mock_socket):
        cbs = xor_calculator([0x02,0x06,0x00,0x81,0x81,0x81,0x02])
        data = bytearray([0x00,0x81,0x81,0x81,0x02,cbs])
        mock_socket.recv = mock.Mock()
        mock_socket.recv.side_effect = [0x02, 0x06, data ]
        control.test_device_one()

    def test_set_pwm(self,control,mock_socket):
        pass

    def test_get_pwm(self,control,mock_socket):
        pass

    def test_control_pwm(self,control,mock_socket):
        pass

    def test_get_ucp(self,control,mock_socket):
        pass

    def test_set_ucp(self,control,mock_socket):
        pass

    def test_lock_and_unlock_cable_one(self,control,mock_socket):
        pass

    def test_lock_and_unlock_cable_two(self,control,mock_socket):
        pass

    def test_get_lock_motor_fault_pin(self,control,mock_socket):
        pass

    def test_set_cyclic_process_data(self,control,mock_socket):
        pass

    def test_cyclic_process_data(self,control,mock_socket):
        pass

    def test_push_button_simple_connect(self,control,mock_socket):
        pass

    def test_execute_software_reset_on_device(self,control,mock_socket):
        pass

    def test_x_is_sent_by_device_after_reset(self,control,mock_socket):
        pass

    def test_activate_proximity_pilot_resistor_(self,control,mock_socket):
        pass

