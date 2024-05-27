'''
Created on Sep 2, 2013

@author: Sven
'''

import serial
import logging
import time
from uss_port_service import uss_service
from Exceptions import UssPortError, UssStatusError
from Exceptions import UssServiceNotSupportedError
from Exceptions import UssServiceReponseError
from Exceptions import UssPortReadError, UssResponseChecksumError
from Exceptions import UssInvalidLengthError, UssInvalidAddressError
from Exceptions import UssInvalidResponseError
from Exceptions import UssRemoteChecksumError
from Exceptions import UssRemoteUnknownError


class uss_port(serial.Serial):

    STX = 0x02
    DEVICE_ADDRESS = 0
    MIN_MESSAGE_LENGTH = 3

    USS_DIGIT_VOLTAGE = 0.029
    DEFAULT_PWM_FREQ = 1000


    def __init__(self, portname, unsafe=False):
        """Constructor which opens the port and fetches the device state.

        :param portname: The name of the serial port to use.
        :type portname: str

        unsafe: Indicates whether the port fetches exceptions.
        :type unsafe: boolean
        """
        try:
            super(uss_port, self).__init__(portname, 57600, timeout=.1)
        except serial.SerialException as val:
            raise UssPortError("Error while opening USS port: %s" % val)

        logging.info("USS port %s successfully opened." % portname)

        self._unsafe = unsafe


    def device_test(self):
        self.flush()

        # Just try all commands before deciding to be non extended.
        self._extended=True

        # Get version information and state first:
        service = uss_service(uss_service.DEVICE_TEST)
        self._send_message(service)

        data = self._get_message(service)
        if data:
            self._software_version = data[0]
            self._hardware_version = data[1]
            self._device_state1 = data[2]
        else:
            raise UssStatusError("Error while retrieving status information.")


        # Try also to get extend state information for seeing if the extend USS
        # protocol is supported.
        service = uss_service(uss_service.DEVICE_TEST2)
        try:
            self._send_message(service)
            data = self._get_message(service)
            self._extended=True
            self._revision = data[0] + (data[1] << 8)
            self._device_state2 = data[2]
        except UssServiceNotSupportedError:
            self._extended=False
            self._revision = 0
            self._device_state2 = 0


    def is_extendend(self):
        """Return whether the port is extendend.

        :returns: True if the port is connected to a device with extended USS
                  instruction set else False.
        :rtype: boolean
        """
        return self._extended


    def _send_message(self, service, data=None):
        """Function for sending service. The message is build up, optional
        payload is included and sent to the port.

        :param service: The service object for assembling the message.
        :type service: An uss_services object.
        :param data: The optional data array which is put into the message.
        :type data: bytearray

        """
        if not self._extended and service.is_extended():
            raise UssServiceNotSupportedError(
                        "Device supports no extended USS commands.")

        msg_len = self.MIN_MESSAGE_LENGTH
        if data:
            msg_len += len(data)
        msg = bytearray([self.STX, msg_len,
                     self.DEVICE_ADDRESS,
                     service.service_code()])
        bcc = self.STX ^ msg_len ^ self.DEVICE_ADDRESS ^ service.service_code()

        # Build bcc over data and add to msg.
        if data:
            for x in data:
                bcc ^= x
                msg.extend([x])

        msg.extend([bcc])

        debug_str = "Sending values:"
        for byte in msg:
            debug_str += "0x%x, " % byte
        logging.debug(debug_str)

        self.write(msg)


    def _get_byte(self):
        """Get a byte from port.

        :returns: The received byte as integer value.
        :rtype: int

        """
        tmp = self.read(1)
        if len(tmp) == 0:
            raise UssPortReadError("Read timeout")
        return ord(tmp)


    def _get_message(self, service):
        """Calls internally _get_next_message. Waits for the appropriate
        message. Fetches all UssServiceReponseError exceptions until a valid
        response is received.

        :param service: The service object for indicating the received message.
        :type service: An uss_services object.
        :returns: A bytearray with the received payload is returned (can have
                  the length 0).
        :rtype: bytearray
        """
        while True:
            try:
                data = self._get_next_message(service)
            except UssServiceReponseError:
                # Check next response, this was not ours.
                continue
            return data


    def _get_next_message(self, service):
        """Wait for a message from port with given service id. If received
        the message is verified. If the message is ok the received payload is
        returned as bytearray.

        :param service: The service object for indicating the received message.
        :type service: An uss_services object.
        :returns: A bytearray with the received payload is returned (can have
                  the length 0).
        :rtype: bytearray

        """

        # Wait for start of frame delimiter:
        while True:
            if self._get_byte() == self.STX:
                break

        # Fetch data length.
        received_len = self._get_byte()

        # Fetch pending data for further processing.
        data = bytearray(self.read(received_len))
        if len(data) != received_len:
            raise UssPortReadError("Read timeout")

        # Check all the received bytes for correctness.
        bcc = self.STX ^ received_len
        for x in data:
            bcc ^= x
        if bcc != 0:
            # Wrong checksum
            raise UssResponseChecksumError("Checksum error")


        # Check whether we are addressed:
        if data[0] != self.DEVICE_ADDRESS:
            raise UssInvalidAddressError("Address error")


        # Check whether the response was an error respsonse:
        service_error = uss_service(uss_service.ERROR)
        if data[1] == service_error.response_code():
            logging.warning("Error response received!")
            expected_len = self.MIN_MESSAGE_LENGTH + service_error.response_length()
        else:
            expected_len = self.MIN_MESSAGE_LENGTH + service.response_length()


        # Check length parameter:
        if received_len != expected_len:
            # Read the rest of bytes and go back.
            self.read(received_len)
            raise UssInvalidLengthError("Wrong length received. \
Expected %d, got %d" % (expected_len, received_len))


        # Check the service code again:
        if data[1] == service_error.response_code():
            # We have got an error response.
            if data[2] == service.service_code():
                #Error: Our message was not accepted!
                if data[3] == service.CRC_ERROR:
                    raise UssRemoteChecksumError("Checksum error on remote site")
                elif data[3] == service.UNKNOWN_SERVICE_ERROR:
                    raise UssServiceNotSupportedError("""Service not
supported on remote site""")
                else:
                    raise UssRemoteUnknownError("""Invalid error response code
 received from remote.""")
            raise UssInvalidResponseError("Reponse error")

        if data[1] != service.response_code():
            # This was not the response we waiting for. Wait for next message.
            raise UssInvalidResponseError("Reponse error")


        debug_str = "Received values:"
        for byte in data[2:-1]:
            debug_str += "0x%x, " % byte
        logging.debug(debug_str)

        return data[2:-1]


    def set_pwm(self, DutyInPromille, Frequency=DEFAULT_PWM_FREQ):
        """Execute set pwm service on port.

        :param DutyInPromille: The duty cycle of the PWM in promille.
        :type DutyInPromille: unsigned integer
        :param Frequency: The frequency of the PWM which defaults to 1 kHz.
        :type Frequency: unsigned integer

        :returns: True if operation was successful, False if not.
        :rtype: bool

        """
        data = bytearray([Frequency & 0xFF, (Frequency >> 8) & 0xFF,
                      DutyInPromille & 0xFF, (DutyInPromille >> 8) & 0xFF])

        service = uss_service(uss_service.SET_PWM)
        self._send_message(service, data)

        data = self._get_message(service)
        if not data or (data[0] != 0):
            return False
        else:
            return True


    def get_pwm(self):
        """Execute get pwm serive on port and return the measured frequency
        and duty cycle.

        :returns: None, if operation has failed or a tuple of two values:
                  First is the measured PWM duty cycle in promille.
                  Second is the measured frequency in Hertz.
        :rtype: tuple

        """
        service = uss_service(uss_service.GET_PWM)
        self._send_message(service)
        data = self._get_message(service)

        if not data:
            return None
        else:
            freq = data[0] + (data[1] << 8)
            duty = data[2] + (data[3] << 8)
            return duty, freq


    def _convert_2s_complement(self, value):
        """Convert a 16 bit binary value into Python signed integer.

        :param value: The 16 bit integer to convert.
        :returns: The converted signed Python integer.
        :rtype: signed integer

        """
        if value & 0x8000:
            # Its a negative number, convert it!
            value -= 65536
        return value


    def set_ucp(self, resistors):
        """Sets up to three resistors which can be enabled through the given bitfield.

        :param resistors:

                          * If Bit 0 is set, 2700 Ohm are enabled else disabled.
                          * If Bit 1 is set, 1300 Ohm are enabled else disabled.
                          * If Bit 2 is set, 270 Ohm are enabled else disabled.
        :type resistors: unsigned integer but only the three least significant
                         bits are used.
        :returns: True if operation was successful, False if not.
        :rtype: bool

        """
        service = uss_service(uss_service.SET_UCP)
        self._send_message(service, bytearray([resistors]))

        data = self._get_message(service)

        if not data or (data[0] != resistors):
            return False
        else:
            return True


    def get_ucp_voltage(self):
        """Execute get ucp service on port and return the measured voltage.

        :returns: None, if operation has failed or a tuple of two values:
                  First is the measured high pulse voltage.
                  Second is the measured low pulse voltage.
        :rtype: tuple

        """
        service = uss_service(uss_service.GET_UCP)
        self._send_message(service)

        data = self._get_message(service)
        if not data:
            return None
        else:
            pos = self._convert_2s_complement(data[0] + (data[1] << 8))
            pos *= self.USS_DIGIT_VOLTAGE
            neg = self._convert_2s_complement(data[2] + (data[3] << 8))
            neg *= self.USS_DIGIT_VOLTAGE
            return pos, neg


    def set_pp(self, resistors):
        """Enables one or none of the proximity resistors.

        :param resistors: It is an enumeration field (only one resistor is
                          active):

                          * 0 => Enables 2700 Ohm
                          * 1 => Enables 150 Ohm
                          * 2 => Enables 487 Ohm
                          * 3 => Enables 1500 Ohm
                          * 4 => Enables 680 Ohm
                          * 5 => Enables 220 Ohm
                          * 6 => Enables 100 Ohm
                          * 7 => Enables no resistor

                          The function will not check the value range, instead
                          the connected device will do the check before execution.
        :type resistors: int with allowed values 0..7
        :returns: True if operation was successful, False if not.
        :rtype: bool

        """
        service = uss_service(uss_service.SET_PP_RESISTORS)
        self._send_message(service, bytearray([resistors]))
        data = self._get_message(service)
        if not data or (data[0] != 0):
            return False
        else:
            return True


    def set_pp_pullup(self, pullup):
        """Enables or disables the proximity pullup resistor.

        :param pullup: 0 or False disables pullup, !=0 or True enables pullup.
        :type pullup: int or bool

        :returns: True if operation was successful, False if not.
        :rtype: bool

        """
        service = uss_service(uss_service.SET_PP_PULLUP)
        self._send_message(service, bytearray([pullup]))
        data = self._get_message(service)
        if not data or (data[0] != 0):
            return False
        else:
            return True


    def get_pp_voltage(self):
        """Execute get pp voltage service on port and return the measured
        voltage.

        :returns: None, if operation has failed or an integer with the voltage
                 in volts.
        :rtype: integer

        """
        service = uss_service(uss_service.GET_PP_VOLTAGE)
        self._send_message(service)

        data = self._get_message(service)
        if not data:
            return None

        val = self._convert_2s_complement(data[0] + (data[1] << 8))
        val *= self.USS_DIGIT_VOLTAGE
        return val


    def manual_association(self, delay_time):
        """Executes manual association.

        :param delay_time: Any value > 0 and < 256. The values states the delay
                           time before execution on the device is really
                           executed.
        :type delay_time: int

        :returns: True if operation was successful, False if not.
        :rtype: boolean

        """
        service = uss_service(uss_service.EXECUTE_MA)
        self._send_message(service, bytearray([delay_time]))
        data = self._get_message(service)
        if not data or (data[0] != 0):
            return False
        else:
            return True


    def lock1_command(self, command):
        """Executes lock1 command on the device.

        :param command: The command which should be executed on device.
        :type command: Integer

        :returns: None if function has failed else the state of the lock.
        :rtype: Integer which indicates state.

        """
        service = uss_service(uss_service.LOCK1)
        self._send_message(service, bytearray([command]))
        data = self._get_message(service)
        if not data:
            return None
        else:
            return data[0]


    def lock2_command(self, command):
        """Executes lock2 command on the device.

        :param command: The command which should be executed on device.
        :type command: Integer

        :returns: None if function has failed else the state of the lock.
        :rtype: Integer which indicates state.

        """
        service = uss_service(uss_service.LOCK2)
        self._send_message(service, bytearray([command]))
        data = self._get_message(service)
        if not data:
            return None
        else:
            return data[0]


    def pwm_control(self, control):
        """Executes PWM control on the device.

        :param control: 0 disables, 1 enables PWM control, 2 queries the state.
        :type control: Integer

        :returns: None if operation was not successful.
                  True if pwm generation is enabled.
                  False if pwm generation is disabled.
        :rtype: bool

        """
        service = uss_service(uss_service.PWM_CONTROL)
        self._send_message(service, bytearray([control]))
        data = self._get_message(service)
        if not data:
            return False
        elif data[0]:
            return True
        else:
            return False


    def get_motor_fault(self):
        """Fetch the motor fault pin state from port and return it.

        :returns: None, if operation has failed or a tuple of two values:
                  True if motor fault state is active.
                  False if motor fault state is not active.
        :rtype: boolean

        """
        service = uss_service(uss_service.GET_MOTOR_FAULT)
        self._send_message(service)
        data = self._get_message(service)

        if not data:
            return None
        elif data[0]:
            return True
        else:
            return False


    def sw_reset(self, wait_for_response=True):
        """Executes a soft reset on connected target.

        :param wait_for_response: If True the function sends the reset command
                                  and waits for the response.
                                  If False the function sends the reset command
                                  and retuirns immediatly with True.
        :type control: Integer

        :returns: True if operation was successful, False if not.
        :rtype: boolean

        """
        service = uss_service(uss_service.SW_RESET)
        self._send_message(service)

        if wait_for_response:
            time.sleep(1)   # Wait some time for POR...
            data = self._get_message(service)
            if not data or (data[0] != 0):
                return False

        return True
