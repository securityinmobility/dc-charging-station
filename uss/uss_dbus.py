import click
import dbus
import dbus.service
import dbus.mainloop.glib
from gi.repository import GLib
from uss_port import uss_port

DBUS_NAME = 'de.thi.UssPort'
DBUS_INTERFACE = 'de.thi.UssPortInterface'
DBUS_PATH = '/de/thi/UssPortObject'

class UssPortService(dbus.service.Object):
    def __init__(self, bus: dbus.Bus, object_path: str, uss_port_obj: uss_port):
        dbus.service.Object.__init__(self, bus, object_path)
        self.uss_port_obj = uss_port_obj

    @dbus.service.method(DBUS_INTERFACE, in_signature='', out_signature='b')
    def device_test(self) -> bool:
        return self.uss_port_obj.device_test()

    @dbus.service.method(DBUS_INTERFACE, in_signature='uu', out_signature='b')
    def set_pwm(self, DutyInPromille: int, Frequency: int = uss_port.DEFAULT_PWM_FREQ) -> bool:
        return self.uss_port_obj.set_pwm(DutyInPromille, Frequency)

    @dbus.service.method(DBUS_INTERFACE, in_signature='', out_signature='(uu)')
    def get_pwm(self) -> tuple:
        return self.uss_port_obj.get_pwm()

    @dbus.service.method(DBUS_INTERFACE, in_signature='u', out_signature='b')
    def set_ucp(self, resistors: int) -> bool:
        return self.uss_port_obj.set_ucp(resistors)

    @dbus.service.method(DBUS_INTERFACE, in_signature='', out_signature='(dd)')
    def get_ucp_voltage(self) -> tuple:
        return self.uss_port_obj.get_ucp_voltage()

    @dbus.service.method(DBUS_INTERFACE, in_signature='u', out_signature='b')
    def set_pp(self, resistors: int) -> bool:
        return self.uss_port_obj.set_pp(resistors)

    @dbus.service.method(DBUS_INTERFACE, in_signature='b', out_signature='b')
    def set_pp_pullup(self, pullup: bool) -> bool:
        return self.uss_port_obj.set_pp_pullup(pullup)

    @dbus.service.method(DBUS_INTERFACE, in_signature='', out_signature='d')
    def get_pp_voltage(self) -> float:
        return self.uss_port_obj.get_pp_voltage()

    @dbus.service.method(DBUS_INTERFACE, in_signature='u', out_signature='b')
    def manual_association(self, delay_time: int) -> bool:
        return self.uss_port_obj.manual_association(delay_time)

    @dbus.service.method(DBUS_INTERFACE, in_signature='u', out_signature='u')
    def lock1_command(self, command: int) -> int:
        return self.uss_port_obj.lock1_command(command)

    @dbus.service.method(DBUS_INTERFACE, in_signature='u', out_signature='u')
    def lock2_command(self, command: int) -> int:
        return self.uss_port_obj.lock2_command(command)

    @dbus.service.method(DBUS_INTERFACE, in_signature='u', out_signature='b')
    def pwm_control(self, control: int) -> bool:
        return self.uss_port_obj.pwm_control(control)

    @dbus.service.method(DBUS_INTERFACE, in_signature='', out_signature='b')
    def get_motor_fault(self) -> bool:
        return self.uss_port_obj.get_motor_fault()

    @dbus.service.method(DBUS_INTERFACE, in_signature='b', out_signature='b')
    def sw_reset(self, wait_for_response: bool = True) -> bool:
        return self.uss_port_obj.sw_reset(wait_for_response)


@click.command()
@click.option('--port', type=str, default='/dev/ttyUSB0', help='Serial port to use')
@click.option('--dbus-bus', type=click.Choice(['system', 'session']), default='system', help='Bus to connect to (system or session)')
def main(port, dbus_bus):
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    match dbus_bus:
        case 'system':
            bus = dbus.SystemBus()
        case 'session':    
            bus = dbus.SessionBus()
    name = dbus.service.BusName(DBUS_NAME, bus)
    uss_port_obj = uss_port(port)
    uss_service = UssPortService(bus, DBUS_PATH, uss_port_obj)

    loop = GLib.MainLoop()
    loop.run()

if __name__ == '__main__':
    main()
