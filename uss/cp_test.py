#!/usr/bin/python
# -*- coding: utf-8 -*-


'''
Created on Sep 4, 2013

@author: Sven
'''

from uss_port_comfort import build_comfort_port
import argparse
from Exceptions import UssPortError, UssPortReadError, UssStatusError
import logging
import sys
import time
from version import REVISION_NUMBER


CP_RESISTOR_HELP_STRING = """
Resistor value as flag field (values can be additive combined): \
1 => 2.7kΩ, 2 => 1.3kΩ, 4 => 270Ω"""


def parse_args():
    """Check arguments list for known parameters."""
    parser = argparse.ArgumentParser(description="""Command line interface for
    testing control pilot signal EVSE via USS protocol.""")

    parser.add_argument("--unsafe", dest="unsafe", action="store_true",
                        default=False, help="Do not hide exception traces.")

    parser.add_argument('-v', "--verbose", dest="verbose", action="count",
                        default=False,
                        help="Print out debug and info messages.")

    parser.add_argument('--version', action='version', version='"CP test" Revision %s' % REVISION_NUMBER)

    parser.add_argument('-p', '--active_port', required=True, type=str,
                        help="Specifies serial port where active EVSE is connected.")

    parser.add_argument('--passive_port', type=str,
                        help="Specifies serial port where passive EV is connected.")

    parser.add_argument('--rcp', type=int, default="0", help=CP_RESISTOR_HELP_STRING)


    return parser.parse_args()

def main():
    if '--unsafe' in sys.argv:
        main_unsafe()
    else:
        try:
            main_unsafe()
        except (UssPortReadError, UssPortError, UssStatusError) as exc:
            logging.error(str(exc))
            sys.exit(-1)


def _handle_resistors(port, rcp):
    if port.set_ucp(rcp):
        logging.info("Resistor set succeeded.")
    else:
        logging.error("Resistor set failed.")


def _control_pwm(port, enable):
    if port.is_extendend():
        if enable:
            logging.info("Enabling pwm on %s ..." % port.name)
        else:
            logging.info("Disabling pwm on %s..." % port.name)

        if port.pwm_control(enable)  != None:
            logging.info("PWM control succeeded.")
        else:
            logging.error("PWM control failed.")
    elif enable:
        logging.warning("%s is a standard port. Ensure that pwm is enabled." \
                        % port.name)
    else:
        logging.warning("%s is a standard port. Ensure that pwm is disabled." \
                        % port.name)


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

    # Preparing active port for measurements.
    active_port = build_comfort_port(args.active_port)

    # Disable pwm output
    _control_pwm(active_port, False)

    # Preparing passive port for measurements (if requested).
    if args.passive_port:
        passive_port = build_comfort_port(args.passive_port)
        # Disable resistors on active port.
        _handle_resistors(active_port, 0)
        _control_pwm(passive_port, False)
        _handle_resistors(passive_port, args.rcp)
    else:
        # No passive port given, use resistors of active port.
        _handle_resistors(active_port, args.rcp)

    # Enable pwm output
    _control_pwm(active_port, True)



    print """Requested duty, Active duty, Active frequency, Active ucp high \
pulse, Active ucp low pulse, Passive duty, Passive frequency, Passive ucp high\
 pulse, Passive ucp low pulse"""

    if args.passive_port:
        for i in xrange(1001):
            active_port.set_pwm(i)
            time.sleep(.1)
            active_port.update()
            passive_port.update()
            active_duty, active_freq = active_port.get_pwm()
            active_ucp_high, active_ucp_low = active_port.get_ucp_voltage()
            passive_duty, passive_freq = passive_port.get_pwm()
            passive_ucp_high, passive_ucp_low = passive_port.get_ucp_voltage()


            print "%d, %d, %d, %f, %f, %d, %d, %f, %f" % (i,
                    active_duty, active_freq,
                    active_ucp_high, active_ucp_low,
                    passive_duty, passive_freq,
                    passive_ucp_high, passive_ucp_low)
    else:
        for i in xrange(1001):
            active_port.set_pwm(i)
            time.sleep(.1)
            active_port.update()
            active_duty, active_freq = active_port.get_pwm()
            active_ucp_high, active_ucp_low = active_port.get_ucp_voltage()

            print "%d, %d, %d, %f, %f, 0, 0, 0, 0" % (i,
                    active_duty, active_freq,
                    active_ucp_high, active_ucp_low)



if __name__ == '__main__':
    main()