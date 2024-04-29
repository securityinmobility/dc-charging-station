import socket



class controllingChargebyteBoard:


    def __init__( self, host: str, port: int ):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((host, port))


    def send_packet( self, service_id: int, payload: bytearray ):
        pass


    def set_pwm( self, frequency: int, dutycycle: int ):
        low_freq = ( frequency & 0xff )
        high_freq = ( frequency >> 8 ) & 0xff
        low_duty = ( dutycycle & 0xff )
        high_duty =  ( dutycycle >> 8 ) & 0xff
        self.send_packet( 0x11, bytearray([low_freq, high_freq, low_duty, high_duty]) )


    def get_pwm( self ):
        self.send_packet( 0x10, bytearray() )


    def control_pwm():
        self.send_packet( 0x12, bytearray())


    def get_ucp():
        self.send_packet( 0x14, bytearray())


    def set_ucp():
        self.send_packet( 0x15, bytearray())


    def lock_cable_one():
        self.send_packet( 0x17, bytearray())


    def unlock_cable_two():
        self.send_packet( 0x18, bytearray())


    def get_motor_fault_pin():
        self.send_packet( 0x1A, bytearray())


    def set_cyclic_process_data():
        self.send_packet( 0x20, bytearray())


    def cyclic_process_data():
        self.send_packet( 0x20, bytearray())


    def push_button_simple_connect():
        self.send_packet( 0x31, bytearray())


    #execute software reset on device
    def reset():
        self.send_packet( 0x33, bytearray())


    def x_is_sent_by_device_after_reset():
        self.send_packet( 0x12, bytearray())


    def activate_proximity_pilot_resistor():
        self.send_packet( 0x50, bytearray())


    def enable_disable_the_pullup_resistor_of_the_proximity_pin():
        self.send_packet( 0x51, bytearray())



