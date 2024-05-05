import socket


class controllingChargebyteBoard:

    def __init__( self, host: str, port: int ):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((host, port))
        self.s.settimeout(60.0 * 5.0)


    def read_response( self ) -> bytearray:
        beginning = s.recv(1) # read the message beginning
        length = s.recv(1) # read the length of the message
        data = s.recv( (int)length )

        return data


    def build_message( self, service_id: int, payload: bytearray ) -> bytearray:
        start_of_message = 0x02
        length_of_message = 3 + len(payload)
        device_adress = 0 #currently all the messages have the address 0
        block_check_sum = start_of_message ^ length_of_message ^ device_adress ^ service_id ^ payload

        return bytearray([start_of_message,length_of_message,device_adress,service_id]) + payload + bytearray([block_check_sum])

    def decode_response( self, service_id:int, response:bytearray ):
        pass


    def send_packet( self, service_id: int, payload: bytearray ):
        self.s.send( self.build_message(service_id, payload) )
        self.read_response( service_id )
        #try:
        #    self.read_response( service_id )
        #except Exception:
        #    return


    def test_devices( self ):
        self.send_packet( 0x01, bytearray() )
        self.send_packet( 0x04, bytearray() )


    def get_pwm( self ):
        self.send_packet( 0x10, bytearray() )


    def set_pwm( self, frequency: int, dutycycle: int ):
        low_freq = ( frequency & 0xff )
        high_freq = ( frequency >> 8 ) & 0xff
        low_duty = ( dutycycle & 0xff )
        high_duty =  ( dutycycle >> 8 ) & 0xff
        self.send_packet( 0x11, bytearray([low_freq, high_freq, low_duty, high_duty]) )


    def control_pwm( self, control_code: int ):
        # 0 = disable pwm
        # 1 = enable pwm
        # 2 = query pwm generation status
        if( control_code < 0 or control_code > 2 ):
            raise ValueError('The control code must be 0, 1 or 2', control_code )
        self.send_packet( 0x12, bytearray( control_code ))


    def get_ucp( self ):
        self.send_packet( 0x14, bytearray())


    def set_ucp( self, resistance: int ):
        #0 = 2.7 
        #1 = 1.3
        #2 = 347
        #3 to 7 are reserved (what does reserved means?)
        if( resistance < 0 or resistance > 2 ):
            raise ValueError('The resistance is defined between 0 and 2', resistance)
        self.send_packet( 0x15, bytearray(resistance))


    def lock_unlock_cable_one( self, command:int ):
        self.send_packet( 0x17, bytearray(command) )


    def lock_unlock_cable_two( self, command:int ):
        #0 unlock the socket
        #1 lock the socket
        #2 request status
        #3 to 255 reserved
        if( command < 0 or command > 2 ):
            raise ValueError('Command must be 0, 1 or 2', command)
        self.send_packet( 0x18, bytearray(command) )


    def get_motor_fault_pin( self ):
        self.send_packet( 0x1A, bytearray() )


    def set_cyclic_process_data( self, interval:int ):
        self.send_packet( 0x20, bytearray(interval) )


    def cyclic_process_data( self, interval:int ):
        self.send_packet( 0xC0, bytearray(interval) )


    def push_button_simple_connect( self, parameter:int ):
        self.send_packet( 0x31, bytearray(parameter) )


    #execute software reset on device
    def reset( self ):
        self.send_packet( 0x33, bytearray())


    def x_is_sent_by_device_after_reset( self ):
        self.send_packet( 0xB3, bytearray())


    def activate_proximity_pilot_resistor( self, control:int ):
        if( control < 0 or control > 7 ):
            raise ValueError('Control must be between 0 and 7')
        self.send_packet( 0x50, bytearray([control]))


    def enable_pullup_resistor( self ):
        #Control=0 deactivates the pullup, all other values activate the pullup
        self.send_packet( 0x51, bytearray([3]) )


    def disable_the_pullup_resistor( self ):
        self.send_packet( 0x51, bytearray([0]))


    def get_voltage_of_proximity_signal( self ):
        self.send_packet( 0x52, bytearray([0]) )




