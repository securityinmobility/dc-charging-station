'''
Created on Sep 12, 2013

@author: Sven
'''


class pwm_commands:
    DISABLE = 0
    ENABLE = 1
    QUERY = 2


class uss_service(object):
    DEVICE_TEST = 0
    DEVICE_TEST2 = 1
    GET_PWM = 2
    SET_PWM= 3
    GET_UCP = 4
    SET_UCP = 5
    SET_PP_RESISTORS = 6
    SET_PP_PULLUP = 7
    GET_PP_VOLTAGE = 8
    EXECUTE_MA = 9
    LOCK1 = 10
    LOCK2 = 11
    GET_MOTOR_FAULT = 12
    PWM_CONTROL = 13
    SW_RESET = 14
    ERROR = 15

    # Erroro code in error response messages.
    CRC_ERROR = 0x43
    UNKNOWN_SERVICE_ERROR = 0x44

    _services = {    # (Request Service, Response service, length of response payload, extended)
        DEVICE_TEST: (0x01, 0x81, 3, False),
        DEVICE_TEST2: (0x04, 0x84, 3, True),
        GET_PWM: (0x10, 0x90, 4, False),
        SET_PWM: (0x11, 0x91, 1, False),
        GET_UCP: (0x14, 0x94, 4, False),
        SET_UCP: (0x15, 0x95, 1, False),
        SET_PP_RESISTORS: (0x50, 0xD0, 1, True),
        SET_PP_PULLUP: (0x51, 0xD1, 1, True),
        GET_PP_VOLTAGE: (0x52, 0xD2, 2, True),
        EXECUTE_MA: (0x31, 0xB1, 1, False),
        LOCK1: (0x17, 0x97, 1, False),
        LOCK2: (0x18, 0x98, 1, True),
        GET_MOTOR_FAULT: (0x1A, 0x9A, 1, True),
        PWM_CONTROL: (0x12, 0x92, 1, True),
        SW_RESET: (0x33, 0xB3, 1, True),
        ERROR: (0x00, 0x99, 2, False)
    }

    def __init__(self, service):
        """Constructor which builds the object.

        :param service: An integer which states the service.
        :type service: integer
        """
        self._service = service

    def service_code(self):
        """Return the service code for request messages.

        :returns: The request service code.
        :rtype: byte
        """
        return self._services[self._service][0]

    def response_code(self):
        """Return the service code for response messages.

        :returns: The response service code.
        :rtype: byte
        """
        return self._services[self._service][1]

    def response_length(self):
        """The length of a typical reponse message.

        :returns: The length of reponse messages.
        :rtype: integer
        """
        return self._services[self._service][2]

    def is_extended(self):
        """return whether the service is part of the original uss specification
        or is not.

        :returns: True if is part of the extended uss protocol, False if not.
        :rtype: boolean
        """
        return self._services[self._service][3]

