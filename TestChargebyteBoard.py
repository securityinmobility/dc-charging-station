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

    def test_should_check_length(self,control,mock_socket):
        data = bytearray([0x00,0x95,0x15,0x07,0x02,0x02])
        mock_socket.recv = mock.Mock()
        mock_socket.recv.side_effect = [0x02, 0x06, data ]
        with pytest.raises(Exception) as info:
            control.set_ucp(2)
        assert info.value.args[0] == 'Wrong length! something went wrong!'


    def test_should_verify_service_id(self,control,mock_socket):
        data = bytearray([0x00,0x81,0x81,0x81,0x02,0x02])
        mock_socket.recv = mock.Mock()
        mock_socket.recv.side_effect = [0x02, 0x06, data ]
        with pytest.raises(Exception) as info:
            control.send_packet(0x51, bytearray())
        assert info.value.args[0] == 'this response does not corresponds to the service that was requested'


    def test_should_time_out(self, control, mock_socket):
        pass # i dont know how to implement this one


    def test_incorrect_checksum(self,control,mock_socket):
        #how to code a xor calculator on byteaddays?
        pass


    def test_should_start_with_answer_code(self,control,mock_socket):
        data = bytearray([0x00,0x95,0x1,0x22])
        mock_socket.recv = mock.Mock()
        mock_socket.recv.side_effect = [0x05, 0x04, data ]
        with pytest.raises(Exception) as info:
            control.set_ucp(2)
        assert info.value.args[0] == 'beginning of message was not 0x02'


    def test_test_device_one(self, control, mock_socket):
        data = bytearray([0x00,0x81,0x81,0x81,0x02,0x00])
        mock_socket.recv = mock.Mock()
        mock_socket.recv.side_effect = [0x02, 0x6, data ]
        software_number, hardware_number, reset_value = control.test_device_one()
        assert software_number == 0x81
        assert hardware_number == 0x81
        assert reset_value.value == 0x02
        mock_socket.send.assert_called_once_with(bytearray([0x02,0x03,0x00,0x01,0x00]))


    def test_test_device_two(self, control, mock_socket):
        data = bytearray([0x00,0x84,0x70,0x70,0x02,0x00])
        mock_socket.recv = mock.Mock()
        mock_socket.recv.side_effect = [0x02, 0x6, data ]
        build, reset_value = control.test_device_two()
        assert build == 11312
        assert reset_value.value == 0x02
        mock_socket.send.assert_called_once_with(bytearray([0x02,0x03,0x00,0x04,0x05]))


    def test_set_pwm(self,control,mock_socket):
        data = bytearray([0x00,0x81,0x81,0x81,0x02,0x00])
        mock_socket.recv = mock.Mock()
        mock_socket.recv.side_effect = [0x02, 0x06, data]
        control.test_device_one()
        pass


    def test_get_pwm(self,control,mock_socket):
        data = bytearray([0x00,0x81,0x81,0x81,0x02,0x00])
        mock_socket.recv = mock.Mock()
        mock_socket.recv.side_effect = [0x02, 0x06, data ]
        control.test_device_one()
        pass


    def test_control_pwm(self,control,mock_socket):
        data = bytearray([0x00,0x81,0x81,0x81,0x02,0x00])
        mock_socket.recv = mock.Mock()
        mock_socket.recv.side_effect = [0x02, 0x06, data ]
        control.test_device_one()
        pass


    def test_get_ucp(self,control,mock_socket):
        data = bytearray([0x00,0x81,0x81,0x81,0x02,0x00])
        mock_socket.recv = mock.Mock()
        mock_socket.recv.side_effect = [0x02, 0x06, data ]
        control.test_device_one()
        pass


    def test_set_ucp(self,control,mock_socket):
        data = bytearray([0x00,0x81,0x81,0x81,0x02,0x00])
        mock_socket.recv = mock.Mock()
        mock_socket.recv.side_effect = [0x02, 0x06, data ]
        control.test_device_one()
        pass


    def test_lock_and_unlock_cable_one(self,control,mock_socket):
        data = bytearray([0x00,0x81,0x81,0x81,0x02,0x00])
        mock_socket.recv = mock.Mock()
        mock_socket.recv.side_effect = [0x02, 0x06, data ]
        control.test_device_one()
        pass


    def test_lock_and_unlock_cable_two(self,control,mock_socket):
        data = bytearray([0x00,0x81,0x81,0x81,0x02,0x00])
        mock_socket.recv = mock.Mock()
        mock_socket.recv.side_effect = [0x02, 0x06, data ]
        control.test_device_one()
        pass


    def test_get_lock_motor_fault_pin(self,control,mock_socket):
        data = bytearray([0x00,0x81,0x81,0x81,0x02,0x00])
        mock_socket.recv = mock.Mock()
        mock_socket.recv.side_effect = [0x02, 0x06, data ]
        control.test_device_one()
        pass


    def test_set_cyclic_process_data(self,control,mock_socket):
        data = bytearray([0x00,0x81,0x81,0x81,0x02,0x00])
        mock_socket.recv = mock.Mock()
        mock_socket.recv.side_effect = [0x02, 0x06, data ]
        control.test_device_one()
        pass


    def test_cyclic_process_data(self,control,mock_socket):
        data = bytearray([0x00,0x81,0x81,0x81,0x02,0x00])
        mock_socket.recv = mock.Mock()
        mock_socket.recv.side_effect = [0x02, 0x06, data ]
        control.test_device_one()
        pass


    def test_push_button_simple_connect(self,control,mock_socket):
        data = bytearray([0x00,0x81,0x81,0x81,0x02,0x00])
        mock_socket.recv = mock.Mock()
        mock_socket.recv.side_effect = [0x02, 0x06, data ]
        control.test_device_one()
        pass


    def test_execute_software_reset_on_device(self,control,mock_socket):
        data = bytearray([0x00,0x81,0x81,0x81,0x02,0x00])
        mock_socket.recv = mock.Mock()
        mock_socket.recv.side_effect = [0x02, 0x06, data ]
        control.test_device_one()
        pass


    def test_x_is_sent_by_device_after_reset(self,control,mock_socket):
        data = bytearray([0x00,0x81,0x81,0x81,0x02,0x00])
        mock_socket.recv = mock.Mock()
        mock_socket.recv.side_effect = [0x02, 0x06, data ]
        control.test_device_one()
        pass


    def test_activate_proximity_pilot_resistor_(self,control,mock_socket):
        data = bytearray([0x00,0x81,0x81,0x81,0x02,0x00])
        mock_socket.recv = mock.Mock()
        mock_socket.recv.side_effect = [0x02, 0x06, data ]
        control.test_device_one()
        pass


