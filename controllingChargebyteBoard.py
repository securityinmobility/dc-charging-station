import socket
from enum import Enum


class SerialSetting(Enum):
    BAUD_RATE = 57600
    DATA_BITS = 8
    STOP_BITS = 1
    PARITY = "None"
    FLOW_CONTROL = "None"


class ResetType(Enum):
    POWER_ON_RESET = 0
    EXTERNAL_RESET = 1
    BROWN_OUT_RESET = 2
    WATCHDOG_RESET = 3
    JTAG_RESET = 4


class ResetReason(Enum):
    STOP_MODE_ERROR = 0
    CORE_LOCKUP = 1
    SOFTWARE_RESET = 2
    CLOCK_LOSS_RESET = 3
    WAKEUP_RESET = 4


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


class controllingChargebyteBoard:

    def __init__( self, host: str, port: int ):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((host, port))
        self.s.settimeout(15.0)


    def read_response( self ) -> bytearray:
        beginning = s.recv(1) # read the message beginning
        length = s.recv(1) # read the length of the message
        data = s.recv( int(length) )

        return bytearray([beginning,length])+data


    def build_message( self, service_id: int, payload: bytearray ) -> bytearray:
        start_of_message = 0x02
        length_of_message = 3 + len(payload)
        device_adress = 0 #currently all the messages have the address 0
        block_check_sum = start_of_message ^ length_of_message ^ device_adress ^ service_id ^ payload

        return bytearray([start_of_message,length_of_message,device_adress,service_id]) + payload + bytearray([block_check_sum])


    #TODO: have a function to read the cyclic message from device to host
    #TODO: we need to send function to device every few minutes using thread
    #TODO:check length: map the expected length to each service on a dictonary
    def check_response( self, service_id:int, response:bytearray ):
        if( response[0] != 0x02 ):
            raise Exception('beginning of message was not 0x02')
        if( response[3] != service_id + 0x80 ):
            raise Exception('this response does not corresponds to the service that was requested')
        expected_check_sum = response[0]
        for byte in response[1:-1]:
            expected_check_sum = expected_check_sum ^ byte
        if( expected_check_sum != response[-1] ):
            raise Exception('Something went wrong: the check block is wrong!')


    def join_bytes( self, low_byte, high_byte ):

        return low_byte + 100*high_byte


    def get_bit_position( self ):
        pass


    def parse_response( self, service_id:int, response:bytearray ):
        response = response[4:-1]
        return response


    def send_packet( self, service_id: int, payload: bytearray ):
        self.s.send( self.build_message(service_id, payload) )
        response = self.read_response( service_id )
        check_response( service_id, response )
        return self.parse_response( service_id, response )


    def test_device_one( self ):
        response = self.send_packet( 0x01, bytearray() )
        software_version = response[0]
        hardware_version = response[1]
        last_reset_reason = ResetType(response[-1])

        return software_version, hardware_version, last_reset_reason


    def test_device_two( self ):
        response = self.send_packet( 0x04, bytearray() )
        build = join_bytes(response[0],response[1])
        last_reset_reason = ResetType(response[2])

        return build, last_reset_reason


    def get_pwm( self ):
        response = self.send_packet( 0x10, bytearray() )
        frequency = join_bytes(response[0],response[1])
        duty_cicle = join_bytes(response[2], response[3])

        return frequency, duty_cicle


    def set_pwm( self, frequency: int, dutycycle: int ):
        low_freq = ( frequency & 0xff )
        high_freq = ( frequency >> 8 ) & 0xff
        low_duty = ( dutycycle & 0xff )
        high_duty =  ( dutycycle >> 8 ) & 0xff
        response = self.send_packet( 0x11, bytearray([low_freq, high_freq, low_duty, high_duty]) )

        return ControlPWM( response[0] )


    def control_pwm( self, control_code: int ):
        if( control_code < 0 or control_code > 2 ):
            raise ValueError('The control code must be 0, 1 or 2', control_code )
        response = self.send_packet( 0x12, bytearray( control_code ))

        return StatusPWMGeneration( response[0] )


    def get_ucp( self ):
        response = self.send_packet( 0x14, bytearray())
        positive_cp = join_bytes(response[0], response[1])
        negative_cp = join_bytes(response[2],response[3])

        return positive_cp, negative_cp


    def set_ucp( self, resistance: int ):
        #0 = 2.7 
        #1 = 1.3
        #2 = 347
        #3 to 7 are reserved (what does reserved means?)
        if( resistance < 0 or resistance > 2 ):
            raise ValueError('The resistance is defined between 0 and 2', resistance)
        return self.send_packet( 0x15, bytearray(resistance))


    def lock_unlock_cable_one( self, command:int ):
        if( command < 0 or command > 2 ):
            raise ValueError('Command must be 0, 1 or 2', command)
        response = self.send_packet( 0x17, bytearray(command) )
        return LockStatus( response[0] )


    def lock_unlock_cable_two( self, command:int ):
        if( command < 0 or command > 2 ):
            raise ValueError('Command must be 0, 1 or 2', command)
        return self.send_packet( 0x18, bytearray(command) )


    def get_motor_fault_pin( self ):
        #TODO : fix case if i get other numbers that are not 0 and not 1
        #The status code is 0 if the motor fault pin is not activated. The status code is not 0 if the motor fault pin is activated.
        return StatusCode(self.send_packet(0x1A, bytearray()))


    def set_cyclic_process_data( self, interval:int ):
        response = self.send_packet( 0x20, bytearray(interval) )

        return StatusCode(response([0]))


    def cyclic_process_data( self, interval:int ):
        return self.send_packet( 0xC0, bytearray(interval) )


    def push_button_simple_connect( self, parameter:int ):
        response = self.send_packet( 0x31, bytearray(parameter) )

        return ErrorCode(response[0])


    #execute software reset on device
    def reset( self ):
        return self.send_packet( 0x33, bytearray())


    def x_is_sent_by_device_after_reset( self ):
        return self.send_packet( 0xB3, bytearray())


    def activate_proximity_pilot_resistor( self, control:int ):
        if( control < 0 or control > 7 ):
            raise ValueError('Control must be between 0 and 7')
        response = self.send_packet( 0x50, bytearray([control]))
        return ErrorCode(response[0])


    def enable_pullup_resistor( self ):
        #Control=0 deactivates the pullup, all other values activate the pullup
        return self.send_packet( 0x51, bytearray([3]) )


    def disable_the_pullup_resistor( self ):
        return self.send_packet( 0x51, bytearray([0]))


    def get_voltage_of_proximity_signal( self ):
        response = self.send_packet( 0x52, bytearray([0]) )
        byte_voltage = join_bytes(response[0], response[1])

        return byte_voltage




