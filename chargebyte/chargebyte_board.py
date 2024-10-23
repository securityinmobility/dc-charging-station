import queue
import threading
from threading import Thread, Lock
from enum import Flag, auto
from enum import Enum
import socket
import sys

sys.path.append("..")


class ResistorCode(Enum):
    Ohm_2700 = 0
    Ohm_150 = 1
    Ohm_487 = 2
    Ohm_1500 = 3
    Ohm_680 = 4
    Ohm_220 = 5
    Ohm_100 = 6
    OFF = 7


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


class CableLock(Enum):
    LOCK = 0
    UNLOCK = 1


class ErrorCode(Enum):
    NO_ERROR = 0
    INVALID_PARAMETER = 1


class StatusCode(Enum):
    OFF = 0
    ACTIVE = 1


class ChargebyteException(Exception):
    def __init__(self, message):
        self.message = message


class ChargebyteBoard:
    def __init__(self, host: str, port: int):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        self.socket.settimeout(3.0)
        self.mutex = Lock()

    def send_packet(self, service_id: int, payload: bytearray) -> None:
        self.socket.send(self.build_message(service_id, payload))

    def build_message(self, service_id: int, payload: bytearray) -> bytearray:
        if not isinstance(service_id, int):
            raise TypeError
        start_of_message = 0x02
        length_of_message = 0x03 + len(payload)
        device_adress = 0x00
        header = (
            bytearray([start_of_message, length_of_message, device_adress, service_id])
            + payload
        )
        return header + bytearray([self.calculate_checksum(header)])

    def read_response(self, service) -> bytearray:
        while self.socket.recv(1) != 0x02:
            pass
        beginning = 0x02
        length = self.socket.recv(1)
        # if len(beginning) == 0 or len(length) == 0:
        #    raise ChargebyteException("No data returned when trying to read response")
        full_len = int(length[0]) + 2
        data = bytearray(beginning + length)
        while len(data) < full_len:
            data += self.socket.recv(full_len - len(data))
        self.check_response(data)
        return data

    def check_response(self, response: bytearray):
        if response[0] != 0x02:
            raise ChargebyteException("beginning of message was not 0x02")
        # if self.calculate_checksum(response[:-1]) != response[-1]:
        #    raise ChargebyteException("Something went wrong: the check block is wrong!")

    def check_response_length(self, response: list, length: int) -> None:
        if len(response) != length:
            raise Exception(
                "Something went wrong, the response has an unexpected length!"
            )

    def parse_response(self, response: bytearray) -> bytearray:
        return response[4:-1]

    def calculate_checksum(self, numbers: bytearray) -> bytearray:
        """Returns XOR of all the elements in the bytearray"""
        checksum = 0
        for num in numbers:
            checksum ^= num
        return bytearray([checksum])

    def join_bytes(self, low_byte: int, high_byte: int) -> int:
        """join the 2 bytes on a single number"""

        return (high_byte << 8) | low_byte

    def keep_service_alive():
        pass

    def test_device_one(self) -> tuple[int, int, ResetType]:
        """This service gives access to system reset causes as well as the Software and the Hardware version (one byte each) of the coprocessor"""

        self.send_packet(0x01, bytearray())
        response = self.read_response(0x01)
        self.check_response_length(response, 3)
        software_version = response[0]
        hardware_version = response[1]
        last_reset_reason = ResetType(response[-1])
        return software_version, hardware_version, last_reset_reason

    def test_device_two(self) -> tuple[int, ResetReason]:
        """This service gives access to reset causes (i.e. why the coprocessor restarted) as well as the software build number"""

        self.send_packet(0x04, bytearray())
        response = self.read_response(0x04)
        self.check_response_length(response, 3)
        build = self.join_bytes(response[0], response[1])
        last_reset_reason = ResetReason(response[2])
        return build, last_reset_reason

    def get_pwm(self) -> tuple[int, int]:
        """The pulse width of the PWM signal can be read by sending the device-get PWM service."""

        self.send_packet(0x10, bytearray())
        response = self.read_response(0x10)
        self.check_response_length(response, 4)
        frequency = self.join_bytes(response[0], response[1])
        duty_cicle = self.join_bytes(response[2], response[3])
        return frequency, duty_cicle

    def set_pwm(self, frequency: int, dutycycle: int) -> ControlCode:
        """The pulse width of the PWM signal can be set by sending the device-set PWM service with the resolution 0.1 % and modulation frequency Fi in Hz (normally 1000). This command requires that the PWM generation is already on."""

        low_freq = frequency & 0xFF
        high_freq = (frequency >> 8) & 0xFF
        low_duty = dutycycle & 0xFF
        high_duty = (dutycycle >> 8) & 0xFF
        self.send_packet(0x11, bytearray([low_freq, high_freq, low_duty, high_duty]))
        response = self.read_response(0x11)
        self.check_response_length(response, 1)
        return ControlCode(response[0])

    def control_pwm(self, control_code: ControlCode) -> StatusPWMGeneration:
        """The control PWM service turns the generation of the PWM on or off or queries the state. This allows you to switch roles between EVSE and EV via software control."""

        self.send_packet(0x12, bytearray([control_code]))
        response = self.read_response(0x12)
        self.check_response_length(response, 1)
        return StatusPWMGeneration(response[0])

    def get_cp(self) -> tuple[int, int]:
        """
        Device-Get-Ucp is the request for the control pilot (CP) voltage. Due to the fact that the voltage is changing with 1 kHz, the highest and lowest voltage value will be measured. The data resolution is 10 bit. The measuring limit is set by the maximum of ±15 V. The resolution is 29 mV/bit. The corresponding request and response are given in the tables below.
        """

        self.send_packet(0x14, bytearray())
        response = self.read_response(0x14)
        self.check_response_length(response, 4)
        positive_cp = self.join_bytes(response[0], response[1])
        negative_cp = self.join_bytes(response[2], response[3])
        return positive_cp, negative_cp

    def set_cp(self, resistance: int) -> int:
        """
        This service switches the load resistors for the CP signal
        The status of every switch will be stated in the parameter as independend bits, where a bit that is set (1) means that the load resistor is connected and a reset bit (0) means that the resistor is not connected. The parameter resistance of the response should match the request parameter
        The parameter resistance is defined only by the 3 LSB bits.
        Note: that not every number can be set. only combinations of: 347, 1300, 2700.
        """

        resistance_bits = 0
        if resistance >= 2700:
            resistance_bits |= 1
            resistance -= 2700
        if resistance >= 1300:
            resistance_bits |= 1 << 1
            resistance -= 1300
        if resistance >= 347:
            resistance_bits |= 1 << 2
        self.send_packet(0x15, bytearray([resistance_bits]))
        response = self.read_response(0x15)
        self.check_response_length(response, 1)
        return int(response[0])

    def lock_unlock_cable_one(self, command: CableLock) -> LockStatus:
        """The device supports two separate locks for locking the charging sockets."""
        self.send_packet(0x17, bytearray([command.value]))
        response = self.read_response(0x17)
        self.check_response_length(response, 1)
        return LockStatus(response[0])

    def lock_unlock_cable_two(self, command: CableLock) -> LockStatus:
        """The device supports two separate locks for locking the charging sockets.

        A connected DC motor is driven into either lock or unlock position dependingon the command value.
        The response to the command is send immediately after the request.
        The locking motor of each channel is driven for the fixed period of 0.5 seconds.
        For a qualified status a separate query command should be sent after this time to get the lock state.
        The motor fault service could be used to get more information about failures.
        """

        self.send_packet(0x18, bytearray([command.value]))
        response = self.read_response(0x18)
        self.check_response_length(response, 1)
        return LockStatus(response[0])

    def get_motor_fault_pin(self) -> StatusCode:
        """The full bridge drivers for both, lock motors 1 and 2, have a fault pin. This fault pin is activated in case one or both full bridges detect the following problems:
            Overcurrent condition
            Undervoltage condition
            Thermal shutdown
        The motor fault pin is wired OR of all possible conditions of both full bridges

        Return Value: The status code is 0 if the motor fault pin is not activated. The status code is not 0 if the motor fault pin is activated.
        """

        self.send_packet(0x1A, bytearray())
        response = self.read_response(0x1A)
        self.check_response_length(response, 1)
        response = response[0]
        if response != 0:
            response = 1
        return StatusCode(response)

    def set_cyclic_process_data(self, interval: int) -> StatusCode:
        """The device is able to send cyclic data messages in a given interval. The messages contain the PWM values, the CP voltage and the plug lock status. The device-set request is given with the parameter interval. Valid values are in the range of 0..FF, where 0=off, 1=100ms, 2=200ms, etc..

                The measured duty cycle has the resolution of the signal as 0.1 %, meaning the value “500” corresponds to 50,0 % PWM.
        The data resolution of the measured voltages is 10 bit. The measuring limit is set by the maximum of ±15 V. The resolution is 29 mV/bit.
        """

        self.send_packet(0x20, bytearray([interval]))
        response = self.read_response(0x20)
        self.check_response_length(response, 1)
        return StatusCode(response[0])

    def cyclic_process_data(self) -> tuple[int, int, int, int]:
        """TODO:"""
        response = self.read_response("0xC0")
        ti = join_bytes(response[4], response[5])
        positive_cp = join_bytes(response[6], response[7])
        negative_cp = join_bytes(response[8], response[9])
        lock_status = join_bytes(response[10], [11])
        return ti, positive_cp, negative_cp, lock_status

    def push_button_simple_connect(self, parameter: int) -> ErrorCode:
        """The request parameter can be 1 = execute. Optionally the time to wait before execution in ms (i.e. 2..255) can be given with this parameter.

        The response is given immediatly independent of the delayed execution time. After the requested delay the command activates the push button simple connected for approx. 1 second. If other push button simple connect services arrive within this time they lengthen the activation time accordingly.

        Return Value: parameter stating the occurrence of errors, 0 = executed without errors, 1 = invalid parameter.
        """

        if parameter > 255 or parameter < 1:
            raise ValueError("This parameter is defined between 1 and 255!")
        self.send_packet(0x31, bytearray([parameter]))
        response = self.read_response(0x31)
        self.check_response_length(response, 1)
        return ErrorCode(response[0])

    def reset(self) -> int:
        """Executes a software reset on device

        No direct response is sent, we may wait for the first message on Device initialization to double check the reset was performed. The POR message on initialization is currently set to zero.
        """
        self.send_packet(0x33, bytearray())
        # response = self.read_response(0x33)
        # self.check_response_length(response,1)
        # return response[0]

    def activate_proximity_pilot_resistor(self, control: ResistorCode) -> ErrorCode:
        """This service enables or disables resistors that load the proximity signal. These resistors are switched between proximity and GND."""

        self.send_packet(0x50, bytearray([control.value]))
        response = self.read_response(0x50)
        self.check_response_length(response, 1)
        return ErrorCode(response[0])

    def enable_proximity_pilot_pullup_5V(self) -> int:
        """There is a pullup resistor of 330 Ohm to +5 V at the proximity pilot signal which can be activated with this service
        Control=0 deactivates the pullup, all other values activate the pullup
        """

        self.send_packet(0x51, bytearray([0x03]))
        response = self.read_response(0x51)
        self.check_response_length(response, 1)
        return response[0]

    def disable_proximity_pilot_pullup_5V(self) -> int:
        """There is a pullup resistor of 330 Ohm to +5 V at the proximity pilot signal which can be deactivated with this service. Control=0 deactivates the pullup, all other values activate the pullup."""

        self.send_packet(0x51, bytearray([0x00]))
        response = self.read_response(0x51)
        self.check_response_length(response, 1)
        return response[0]

    def get_voltage_of_proximity_signal(self) -> float:
        """The service requests the measured voltage at the proximity pilot pin. The resolution is 29 mV/LSB.

        return value: is the voltage.
        """

        self.send_packet(0x52, bytearray())
        response = self.read_response(0x52)
        self.check_response_length(response, 2)
        byte_voltage = self.join_bytes(response[0], response[1])
        return float(byte_voltage) * 0.029
