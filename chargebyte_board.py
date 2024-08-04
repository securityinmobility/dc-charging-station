import socket
from enum import Enum
from enum import Flag, auto
from threading import Thread, Lock
import threading
import queue


#class ResistorValue(Enum):
#    kΩ_27 = 0
#    kΩ_13 = 1
#    Ω_347


class ControlCode(Enum):
    DISABLE = 0
    ENABLE = 1
    QUERY = 2


class ResetType(Flag):
    POWER_ON_RESET = auto()
    EXTERNAL_RESET = auto()
    BROWN_OUT_RESET = auto()
    WATCHDOG_RESET = auto()
    JTAG_RESET = auto()


class ResetReason(Flag):
    STOP_MODE_ERROR = auto()
    CORE_LOCKUP = auto()
    SOFTWARE_RESET = auto()
    CLOCK_LOSS_RESET = auto()
    WAKEUP_RESET = auto()


class ControlPWM(Enum):
    DISABLE_PWM = 0
    ENABLE_PWM = 1
    QUERY_PWM_STATUS = 2


class StatusPWMGeneration(Enum):
    PWM_GENERATION_IS_DISABLED = 0
    PWM_GENERATION_IS_ENABLED = 1


class SocketAction(Enum):
    UNLOCK_SOCKET = 0
    LOCK_SOCKET = 1
    QUERY_LIMIT_SWITCH_STATUS = 2
    RESERVED = 3  # Reserved values from 3 to 255


class LockStatus(Enum):
    OPEN = 0
    CLOSED = 1
    NOT_CONNECTED = 2


class ErrorCode(Enum):
    NO_ERROR = 0
    INVALID_PARAMETER = 1


class StatusCode(Enum):
    OFF = 0
    ACTIVE = 1


class ChargebyteException(Exception):
    def __init__(self, message):
        self.message=message


class ChargebyteBoard:

    def __init__(self, host:str, port:int):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((host, port))
        self.s.settimeout(15.0)
        self.answers = []
        self.mutex = Lock()


    def send_packet( self, service_id:int, payload:bytearray ) -> None:
        self.s.send(self.build_message(service_id, payload))
        self.read_response()


    def get_response( self, service_id:int ) -> bytearray:
        for response in self.answers:
            if response[3] == service_id + 0x80 :
                self.mutex.acquire()
                self.answers.remove(response)
                self.mutex.release()
                return self.parse_response(response)
        raise Exception("we didnt get an answer")


    def build_message(self, service_id: int, payload: bytearray) -> bytearray:
        if not isinstance(service_id,int):
            raise TypeError
        start_of_message = 0x02
        length_of_message = 0x03 + len(payload)
        device_adress = 0x00
        header = bytearray([start_of_message,length_of_message,device_adress,service_id]) + payload
        return header + bytearray([self.calculate_checksum(header)])


    def read_response(self) -> bytearray:
        beginning = self.s.recv(1)
        length = self.s.recv(1)
        if len(beginning) == 0 or len(length) == 0:
            raise ChargebyteException("No data returned when trying to read response")
        full_len = int(length[0]) + 2
        data = bytearray(beginning + length)
        while len(data) < full_len:
            data += self.s.recv(full_len - len(data))
        self.check_response(data)
        if data[3] != 0xC0  :
            self.answers.append(data)
        else:
            pass


    def check_response(self, response:bytearray):
        if response[0] != 0x02:
            raise ChargebyteException('beginning of message was not 0x02')
        if self.calculate_checksum(response[:-1]) != response[-1]:
            raise ChargebyteException('Something went wrong: the check block is wrong!')


    def check_response_length(self, response:list, length:int) -> None:
        if len(response) != length:
            raise Exception('Something went wrong, the response has an unexpected length!')


    def parse_response(self, response: bytearray) -> bytearray:
        return response[4:-1]


    def calculate_checksum(self, numbers: bytearray) -> int:
        response = 0
        for num in numbers:
            response = response ^ num
        return response


    def join_bytes(self, low_byte:int, high_byte:int) -> int:
        return (high_byte << 8) | low_byte


    def keep_service_alive():
        pass


    def test_device_one(self) -> tuple[int,int,ResetType]:
        self.send_packet(0x01, bytearray())
        response = self.get_response(0x01)
        self.check_response_length(response,3)
        software_version = response[0]
        hardware_version = response[1]
        last_reset_reason = ResetType(response[-1])
        return software_version, hardware_version, last_reset_reason


    def test_device_two(self) -> tuple[int,ResetReason]:
        self.send_packet(0x04, bytearray())
        response = self.get_response(0x04)
        self.check_response_length(response,3)
        build = self.join_bytes(response[0],response[1])
        last_reset_reason = ResetReason(response[2])
        return build, last_reset_reason


    def get_pwm(self) -> tuple[int,int]:
        self.send_packet(0x10, bytearray())
        response = self.get_response(0x10)
        self.check_response_length(response,4)
        frequency = self.join_bytes(response[0],response[1])
        duty_cicle = self.join_bytes(response[2], response[3])
        return frequency, duty_cicle


    def set_pwm(self, frequency: int, dutycycle: int) -> ControlPWM:
        low_freq = frequency & 0xff
        high_freq = (frequency >> 8) & 0xff
        low_duty = dutycycle & 0xff
        high_duty =  (dutycycle >> 8) & 0xff
        self.send_packet(0x11, bytearray([low_freq, high_freq, low_duty, high_duty]))
        response = self.get_response(0x11)
        self.check_response_length(response,1)
        return ControlPWM(response[0])


    def control_pwm( self, control_code: ControlCode ) -> StatusPWMGeneration:
        self.send_packet(0x12, bytearray([control_code]))
        response = self.get_response(0x12)
        self.check_response_length(response,1)
        return StatusPWMGeneration(response[0])


    def get_ucp(self) -> tuple[int,int]:
        self.send_packet(0x14, bytearray())
        response = self.get_response(0x14)
        self.check_response_length(response,4)
        positive_cp = self.join_bytes(response[0], response[1])
        negative_cp = self.join_bytes(response[2],response[3])
        return positive_cp, negative_cp


    def set_ucp(self, resistance: int) -> int:
        if resistance < 0 or resistance > 2:
            raise ValueError('The resistance is defined between 0 and 2', resistance)
        self.send_packet(0x15, bytearray([resistance]))
        response = self.get_response(0x15)
        self.check_response_length(response,1)
        return int(response[0])


    def lock_unlock_cable_one( self, command:ControlCode ) -> LockStatus:
        self.send_packet(0x17, bytearray([command]))
        response = self.get_response(0x17)
        self.check_response_length(response,1)
        return LockStatus(response[0])


    def lock_unlock_cable_two( self, command:ControlCode ) -> LockStatus:
        self.send_packet(0x18, bytearray([command]))
        response = self.get_response(0x18)
        self.check_response_length(response,1)
        return LockStatus(response[0])


    def get_motor_fault_pin(self) -> StatusCode:
        self.send_packet(0x1A, bytearray())
        response = self.get_response(0x1A)
        self.check_response_length(response,1)
        response = response[0]
        if response != 0:
            response = 1
        return StatusCode(response)


    def set_cyclic_process_data(self, interval:int) -> StatusCode:
        self.send_packet(0x20, bytearray([interval]))
        response = self.get_response(0x20)
        self.check_response_length(response,1)
        return StatusCode(response[0])


    def cyclic_process_data(self, response) -> tuple[int,int,int,int]:
        #response = self.read_response()
        ti = join_bytes(response[4],response[5])
        positive_cp = join_bytes(response[6],response[7])
        negative_cp = join_bytes(response[8],response[9])
        lock_status = join_bytes(response[10],[11])
        return ti, positive_cp, negative_cp, lock_status


    def push_button_simple_connect(self, parameter:int) -> ErrorCode:
        if parameter > 255 or parameter < 1:
            raise ValueError('This parameter is defined between 1 and 255!')
        self.send_packet(0x31, bytearray([parameter]))
        response = self.get_response(0x31)
        self.check_response_length(response,1)
        return ErrorCode(response[0])


    #execute software reset on device
    def reset(self) -> int:
        self.send_packet(0x33, bytearray())
        response = self.get_response(0x33)
        self.check_response_length(response,1)
        return response[0]


    def activate_proximity_pilot_resistor(self, control:int) -> ErrorCode:
        if control < 0 or control > 7:
            raise ValueError('Control must be between 0 and 7')
        self.send_packet(0x50, bytearray([control]))
        response = self.get_response(0x50)
        self.check_response_length(response,1)
        return ErrorCode(response[0])


    def enable_pullup_resistor(self) -> int:
        response = self.send_packet(0x51, bytearray([0x03]))
        response = self.get_response(0x51)
        self.check_response_length(response,1)
        return response[0]


    def disable_pullup_resistor(self) -> int:
        self.send_packet(0x51, bytearray([0x00]))
        response = self.get_response(0x51)
        self.check_response_length(response,1)
        return response[0]


    def get_voltage_of_proximity_signal(self) -> int:
        self.send_packet(0x52, bytearray())
        response = self.get_response(0x52)
        self.check_response_length(response,2)
        byte_voltage = self.join_bytes(response[0], response[1])
        return byte_voltage




