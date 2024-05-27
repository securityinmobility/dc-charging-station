'''
Created on Sep 4, 2013

@author: Sven
'''

from uss_port import uss_port
from uss_port_lock import lock
from uss_port_service import pwm_commands
import logging




def build_comfort_port(portname, unsafe=False):

    if is_extended(portname, unsafe):
        logging.debug("Building extended port...")
        build_port = uss_port_comfort_ext(portname, unsafe)
    else:
        logging.debug("Building standard port...")
        build_port = uss_port_comfort(portname, unsafe)

    build_port.device_test()
    build_port.update()

    return build_port


def is_extended(portname, unsafe=False):
    with uss_port(portname, unsafe) as port:
        port.device_test()
        if port.is_extendend():
            return True
        else:
            return False


class uss_port_comfort(uss_port):

    _flag_strings = {
        "POR":
"""Indicates a reset has been caused by the power-on detection logic. Because \
the internal supply voltage was ramping up at the time, the low-voltage reset \
(LVD) status bit is also set to indicate that the reset occurred while the \
internal supply was below the LVD threshold.
""",

        "EXT":
"""Indicates a reset has been caused by an active-low level on the external \
RESET pin.
""",

        "BOR":
"""If the LVDRE bit is set and the supply drops below the LVD trip voltage, an\
 LVD reset occurs. This bit is also set by POR.
""",

        "WTD":
"""Indicates a reset has been caused by the watchdog timer Computer Operating \
Properly (COP) timing out. This reset source can be blocked by disabling the \
COP watchdog: write 00 to the SIM's COPC[COPT] field.
""",

        "DBG":
"""Indicates a reset has been caused by the host debugger system setting of the \
System Reset Request bit in the MDM-AP Control Register.
""",
    }


    def __init__(self, portname, unsafe=False):
        """Constructor which builds up the port.

        :param portname: The name of the serial port to use.
        :type portname: str
        """
        super(uss_port_comfort, self).__init__(portname, unsafe)

        self._flags = {}
        self._cp_duty = 0
        self._cp_freq = 0
        self._lock1 = lock(self, 1)

        # self.update()


    def update(self):
        self._flags = {}

        # Convert state register into flags field.
        if self._device_state1 & 0x01:
            self._flags["POR"] = 1
        if self._device_state1 & 0x02:
            self._flags["EXT"] = 1
        if self._device_state1 & 0x04:
            self._flags["BOR"] = 1
        if self._device_state1 & 0x08:
            self._flags["WTD"] = 1
        if self._device_state1 & 0x10:
            self._flags["DBG"] = 1

        self._lock1.update()
        self._cp_duty, self._cp_freq = super(uss_port_comfort, self).get_pwm()


    def get_state(self):
        """Returns the state information as human readable string."""
        state = ""
        for i in self._flags.keys():
            state += "%s: %s" % (i, self._flag_strings[i])
        return state

    def get_version(self):
        """Prints out a formated version string."""
        base = "USS port: SW %d, HW %d" % (self._software_version,
                                           self._hardware_version)
        return base

    def get_pwm(self):
        """Returns the local stored pwm data."""
        return self._cp_duty, self._cp_freq

    def lock(self, lock_number):
        """Executes the lock command of appropriate lock."""
        if lock_number == 2:
            return False
        else:
            self._lock1.lock()
            return True

    def unlock(self, lock_number):
        """Executes the unlock command of appropriate lock."""
        if lock_number == 2:
            return False
        else:
            self._lock1.unlock()
            return True

    def get_pwm_control(self):
        """Returns the state of the PWM generation."""
        return "Active."

    def __str__(self):
        """Print out some state information of this port.

        :returns: Formatted string with state information.
        :rtype: str

        """
        form="""
*******************************************************************************
%(ver)s
Current state:
%(state)s
PWM duty: %(duty)d, PWM frequency: %(freq)d Hz
Lock state 1: %(lock1)s
*******************************************************************************"""

        return form % {'ver': self.get_version(),
                       'state': self.get_state(),
                       'duty': self._cp_duty,
                       'freq': self._cp_freq,
                       'lock1': self._lock1}



class uss_port_comfort_ext(uss_port_comfort):

    _flag_strings = {

        "STOP_MODE":
"""Indicates that after an attempt to enter Stop mode, a reset has been caused \
by a failure of one or more peripherals to acknowledge within approximately \
one second to enter stop mode.
""",

        "CORE_LOCKUP":
"""Indicates a reset has been caused by the ARM core indication of a LOCKUP \
event.""",

        "SW_RESET":
"""Indicates a reset has been caused by software setting of SYSRESETREQ bit in\
 Application Interrupt and Reset Control Register in the ARM core.
""",

        "LOSS_OF_CLOCK":
"""Indicates a reset has been caused by a loss of external clock. The MCG \
clock monitor must be enabled for a loss of clock to be detected. Refer to \
the detailed MCG description for information on enabling the clock monitor.
""",

        "WAKEUP":
"""Indicates a reset has been caused by an enabled wakeup source while the \
chip was in a low leakage mode. Any enabled wakeup source in a VLLSx mode \
causes a reset. This bit is cleared by any reset except WAKEUP.
""",
    }


    def __init__(self, portname, unsafe=False):
        """Constructor which builds up the port.

        :param portname: The name of the serial port to use.
        :type portname: str
        """
        self._pwm_control = True
        self._lock2 = lock(self, 2)
        self._motor_fault = False
        self._flag_strings.update(super(uss_port_comfort_ext, self)._flag_strings)
        super(uss_port_comfort_ext, self).__init__(portname, unsafe)



    def update(self):
        """Updating the port with current state informations."""
        super(uss_port_comfort_ext, self).update()

        # Convert state register into flags field.
        if self._device_state2 & 0x01:
            self._flags["STOP_MODE"] = 1
        if self._device_state2 & 0x02:
            self._flags["CORE_LOCKUP"] = 1
        if self._device_state2 & 0x04:
            self._flags["SW_RESET"] = 1
        if self._device_state2 & 0x08:
            self._flags["LOSS_OF_CLOCK"] = 1
        if self._device_state2 & 0x10:
            self._flags["WAKEUP"] = 1

        self._cp_duty, self._cp_freq = self.get_pwm()
        self._lock2.update()
        self._motor_fault = super(uss_port_comfort_ext, self).get_motor_fault()
        self._pwm_control = self.pwm_control(pwm_commands.QUERY)

    def get_version(self):
        """Prints out a formated version string."""
        base = super(uss_port_comfort_ext, self).get_version()
        extend = "Ext. Rev. %d" % self._revision
        return "%s %s" % (base, extend)

    def lock(self, lock_number):
        if lock_number == 2:
            return self._lock2.lock()
        else:
            return self._lock1.lock()
        return True

    def unlock(self, lock_number):
        if lock_number == 2:
            return self._lock2.unlock()
        else:
            return self._lock1.unlock()
        return True

    def get_motor_fault(self):
        """"Returns the state of the motor fault pin."""
        if self._motor_fault:
            return "Active."
        else:
            return "Inactive."

    def get_pwm_control(self):
        """Returns the state of the PWM generation."""
        if self._pwm_control:
            return "Active."
        else:
            return "Inactive."

    def __str__(self):
        """Print out some state information of this port.

        :returns: Formatted string with state information.
        :rtype: str

        """
        form="""
*******************************************************************************
%(ver)s
Current state:
%(state)s
PWM generation: %(pwm_generation)s
PWM duty: %(duty)d, PWM frequency: %(freq)d Hz
Lock state 1: %(lock1)s
Lock state 2: %(lock2)s
Motor fault state: %(motor)s
*******************************************************************************"""

        return form % {'ver': self.get_version(),
                       'state': self.get_state(),
                       'duty': self._cp_duty,
                       'freq': self._cp_freq,
                       'lock1': self._lock1,
                       'lock2': self._lock2,
                       'motor': self.get_motor_fault(),
                       'pwm_generation': self.get_pwm_control()}

