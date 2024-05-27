#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on Aug 19, 2013

@author: Sven
'''

import sys
import cmd
import logging
import argparse
from version import REVISION_NUMBER
from uss_port_comfort import build_comfort_port
from Exceptions import UssPortError, UssPortReadError, UssStatusError



DEFAULT_PWM_DUTY = 500
DEFAULT_PWM_FREQ = 1000



CP_RESISTOR_HELP_STRING = """
Resistor value as flag field (values can be additive combined): \
1 => 2.7kΩ, 2 => 1.3kΩ, 4 => 270Ω"""

PP_RESISTOR_HELP_STRING = """
Resistor value as enumerator (only one value can be set): \
0 => 2.7kΩ, 1 => 150Ω, 2 => 487Ω, 3 => 1.5kΩ, 4 => 680Ω, 5 => 220Ω, 6 => 100Ω,\
 7 = Off"""



def parse_args():
    """Check arguments list for known parameters."""
    parser = argparse.ArgumentParser(description="""Command line interface for
    accessing EVSE via USS protocol.""")

    parser.add_argument("--unsafe", dest="unsafe", action="store_true",
                        default=False, help="Do not hide exception traces.")

    parser.add_argument('--version', action='version', version='"USS port" Revision %s' % REVISION_NUMBER)

    parser.add_argument('-v', "--verbose", dest="verbose", action="count",
                        default=False,
                        help="Print out debug and info messages.")

    parser.add_argument('-c', "--interactive", action="store_true",
                        default=False, help="Starts interactive mode.")

    parser.add_argument('-p', '--port', required=True, type=str,
                        help="Specifies serial port where EVSE is connected.")

    parser.add_argument('-i', '--info', action='store_true',
                        help="Prints state information of uss port.")

    parser.add_argument('-ma', '--manual-association', type=int,
                        help="""Controls manual association, given number is a
                        delay in ms (i.e. 10 means execution after 10ms).""")

    parser.add_argument('-r', "--reset", action="store_true",
                        default=False, help="Resets the target device and waits on POR message (Extended only).")
    parser.add_argument('-ri', "--reset_nowait", action="store_true",
                        default=False, help="Resets the target device (Extended only).")


    pwm_group = parser.add_argument_group('pwm')
    pwm_group.add_argument('-pwm', action='store_true',
                           help="Measures PWM and returns duty and frequency.")
    pwm_enable_group = pwm_group.add_mutually_exclusive_group()
    pwm_enable_group.add_argument('--enable', action='store_true',
                        help="""Explicitly enables PWM before doing some action
                                (Extended only).""")
    pwm_enable_group.add_argument('--disable', action='store_true',
                        help="""Explicitly disables PWM (Extended only).
                                Ignores -d and -f option.""")
    pwm_group.add_argument('-d', '--duty', type=int,
                        help="PWM duty cycle in promille.")
    pwm_group.add_argument('-f', '--freq', type=int,
                        help="PWM frequency in Hertz.")


    ucp_group = parser.add_argument_group('ucp')
    ucp_group.add_argument('-ucp', action='store_true', help="Executes UCP command.")
    ucp_group.add_argument('--rcp', type=int, help=CP_RESISTOR_HELP_STRING)


    pp_group = parser.add_argument_group('pp')
    pp_group.add_argument('-pp', action='store_true', help="Executes PP command (Extended only).")
    pp_group.add_argument('--rpp', type=int, help=PP_RESISTOR_HELP_STRING)
    pp_pullup_group = pp_group.add_mutually_exclusive_group()
    pp_pullup_group.add_argument('--pullup', action='store_true', help="PP pullup (330 Ohms) is enabled.")
    pp_pullup_group.add_argument('--nopullup', action='store_true', help="PP pullup (330 Ohms) is disabled.")


    lock1_group = parser.add_mutually_exclusive_group()
    lock1_group.add_argument('--lock1', action='store_true', help='Locks "Lock 1"')
    lock1_group.add_argument('--unlock1', action='store_true', help='Unlocks "Lock 1"')

    lock2_group = parser.add_mutually_exclusive_group()
    lock2_group.add_argument('--lock2', action='store_true', help='Locks "Lock 2"')
    lock2_group.add_argument('--unlock2', action='store_true', help='Unlocks "Lock 2"')

    return parser.parse_args()


def _handle_reset(uss_port, wait):
    print('Executing software reset...', end=' ')
    if uss_port.sw_reset(wait):
        print('Success.')
    else:
        print('Failed.')


def _handle_lock(uss_port, locking, number):
    if locking==True:
        print('Locking...', end=' ')
        ret = uss_port.lock(number)
    elif locking==False:
        print('Unlocking...', end=' ')
        ret = uss_port.unlock(number)
    if ret:
        print("Success.")
    else:
        print("Failed.")


def _handle_pp(uss_port, rpp=None, pullup=None):
    if rpp==None and pullup==None:
        print("Fetching pp voltage...", end=' ')
        pp = uss_port.get_pp_voltage()
        if pp==None:
            print("Failed.")
        else:
            print("PP voltage: %f V" % pp)
    else:
        if rpp!=None:
            print("Setting pp resistor...", end=' ')
            if uss_port.set_pp(rpp):
                print("Success.")
            else:
                print("Failed.")
        if pullup!=None:
            if pullup==True:
                print("Enabling pp pullup resistor...", end=' ')
                if uss_port.set_pp_pullup(True):
                    print("Success.")
                else:
                    print("Failed.")
            else:
                print("Disabling pp pullup resistor...", end=' ')
                if uss_port.set_pp_pullup(False):
                    print("Success.")
                else:
                    print("Failed.")


def _handle_ucp(uss_port, rcp=None):
    if rcp==None:
        print("Fetching cp voltages...", end=' ')
        ucp =  uss_port.get_ucp_voltage()
        if ucp:
            print("High voltage: %f V, low voltage: %f V" % ucp)
        else:
            print("Failed.")
    else:
        print("Setting cp resistors...", end=' ')
        if uss_port.set_ucp(rcp):
            print("Success.")
        else:
            print("Failed.")


def _pwm_control(uss_port, enable):
    if enable:
        print("Enabling PWM...", end=' ')
        if uss_port.pwm_control(1) != None:
            print("Success.")
        else:
            print("Failed.")
    else:
        print("Disabling PWM...", end=' ')
        if uss_port.pwm_control(0) != None:
            print("Success.")
        else:
            print("Failed.")


def _handle_pwm(uss_port, duty=None, freq=None):
    if freq==None and duty==None:
        print("Fetching duty and frequency...", end=' ')
        pwm = uss_port.get_pwm()
        if pwm:
            print("PWM duty: %d, PWM frequency: %d Hz" % pwm)
        else:
            print("Failed.")
    else:
        print("Setting duty and frequency...", end=' ')
        if duty==None:
            duty = DEFAULT_PWM_DUTY
        elif freq==None:
            freq = DEFAULT_PWM_FREQ

        if uss_port.set_pwm(duty, freq):
            print("Success.")
        else:
            print("Failed.")


def _handle_ma(uss_port, delay_time):
    print("Executing manual association...", end=' ')
    if uss_port.manual_association(delay_time):
        print("Success.")
    else:
        print("Failed.")


class uss_command_line(cmd.Cmd):

    def __init__(self, uss_port):
        cmd.Cmd.__init__(self)
        self._port = uss_port
        self.prompt = "> "

    def help_ma(self):
        print("""Executes push button simple connect.
Needs an integer as parameter which gives execution delay in milliseconds.""")

    def do_ma(self, line):
        delay = None
        try:
            delay = int(line)
        except:
            print("Failed.")
            return
        _handle_ma(self._port, delay)

    def help_pp(self):
        print("""Executes proximity pilot (pp) commands.
Execpts one optiona parameter:
None: Reads measured pp voltage.
First: Command for setting the pp resistor.
""")

    def do_pp(self, line):
        rpp = None
        parts = line.split()
        if len(parts) == 1:
            try:
                rpp = int(parts[0])
            except ValueError:
                pass
        _handle_pp(self._port, rpp)

    def help_pullup(self):
        print("""Enables pullup resistor at proximity pilot (pp).""")

    def do_pullup(self, line):
        _handle_pp(self._port, None, True)

    def help_nopullup(self):
        print("""Disables pullup resistor at proximity pilot (pp).""")

    def do_nopullup(self, line):
        _handle_pp(self._port, None, False)

    def help_pwm(self):
        print("""Executes pwm command.
Excepts up to two optional parameters:
None: Reads pwm frequency and duty cycle from port.
First: Integer which gives duty cycle in per mill.
Second: Integer which gives frequency in Hz.""")

    def do_pwm(self, line):
        duty = None
        freq = None
        parts = line.split()
        if len(parts) >= 1:
            try:
                duty = int(parts[0])
            except ValueError:
                pass
        if len(parts) == 2:
            try:
                freq = int(parts[1])
            except ValueError:
                pass

        _handle_pwm(self._port, duty, freq)

    def help_pwmdis(self):
        print("""Disbles the PWM output.""")

    def do_pwmdis(self, line):
        _pwm_control(self._port, 0)

    def help_pwmena(self):
        print("""Enables the PWM output.""")

    def do_pwmena(self, line):
        _pwm_control(self._port, 1)

    def help_ucp(self):
        print("""Executes ucp command-
Excepts one optional parameter:
None: Reads ucp voltages from port.
First: Integer which is a flag value for enabling resistors to ground.
        """)

    def do_ucp(self, line):
        rcp = None
        if len(line):
            try:
                rcp = int(line)
            except ValueError:
                pass
        _handle_ucp(self._port, rcp)

    def help_lock1(self):
        print("""Locks "Lock 1".""")

    def do_lock1(self, line):
        _handle_lock(self._port, True, 1)

    def help_lock2(self):
        print("""Locks "Lock 2".""")

    def do_lock2(self, line):
        _handle_lock(self._port, True, 2)

    def help_unlock1(self):
        print("""Unlocks "Lock 1".""")

    def do_unlock1(self, line):
        _handle_lock(self._port, False, 1)

    def help_unlock2(self):
        print("""Unlocks "Lock 2".""")

    def do_unlock2(self, line):
        _handle_lock(self._port, False, 2)

    def help_update(self):
        print("""Refetches state of port and prints it on screen.""")

    def do_update(self, line):
        self._port.update()
        print(self._port)

    def help_exit(self):
        print("""Close port and exit program.""")

    def do_exit(self, line):
        return True

    def help_EOF(self):
        print("""Close port and exit program.""")

    def do_EOF(self, line):
        return True



def main():
    if '--unsafe' in sys.argv:
        main_unsafe()
    else:
        try:
            main_unsafe()
        except (UssPortReadError, UssPortError, UssStatusError) as exc:
            logging.error(str(exc))
            sys.exit(-1)


def main_unsafe():
    args = parse_args()

    if not args.verbose:
        log_level = logging.ERROR
    else:
        if args.verbose == 1:
            log_level = logging.WARNING
        elif args.verbose == 2:
            log_level = logging.INFO
        else:
            log_level = logging.DEBUG

    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s',
                        level=log_level)

    port = build_comfort_port(args.port, args.unsafe)

    if args.reset:
        # Do  wait for response of the device.
        _handle_reset(port, True)

    if args.reset_nowait:
        # Do not wait for response of the device.
        _handle_reset(port, False)

    if args.info:
        print(port)

    if args.manual_association:
        delay_time = args.manual_association
        _handle_ma(port, delay_time)

    ###########################################################################
    # Processing control pilot group (pwm).
    if args.disable:
        _pwm_control(port, 0)
        args.freq=None
        args.duty=None
    elif args.enable:
        _pwm_control(port, 1)
    if args.duty!=None or args.freq!=None or args.pwm:
        _handle_pwm(port, args.duty, args.freq)

    if args.ucp:
        _handle_ucp(port, args.rcp)


    ###########################################################################
    # Processing proximity pilot group (pp)
    if args.pp or args.rpp or args.pullup or args.nopullup:
        pullup = None
        if args.pullup:
            pullup = True
        elif args.nopullup:
            pullup = False
        _handle_pp(port, args.rpp, pullup)


    ###########################################################################
    # Processing lock1 requests
    if args.lock1:
        _handle_lock(port, True, 1)
    elif args.unlock1:
        _handle_lock(port, False, 1)


    ###########################################################################
    # Processing lock2 requests
    if args.lock2:
        _handle_lock(port, True, 2)
    elif args.unlock2:
        _handle_lock(port, False, 2)


    if args.interactive:
        command_line = uss_command_line(port)
        command_line.cmdloop()


if __name__ == '__main__':
    main()

