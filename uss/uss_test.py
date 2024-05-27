#!/usr/bin/python
# -*- coding: utf-8 -*-


'''
Created on Oct 8, 2013

@author: Sven
'''

from uss_port_comfort import build_comfort_port
import argparse
from Exceptions import UssPortError, UssPortReadError, UssStatusError
import logging
import os
import time
from version import REVISION_NUMBER

PWM_TEST_DUTY = (20,500,700,900)
PWM_STANDARD_FREQUENCY = 1000


def parse_args():
    """Check arguments list for known parameters."""
    parser = argparse.ArgumentParser(description="""Command line interface for
    long time testing all measured values of the co processor. Finish with CTRL-C.""")

    parser.add_argument('-v', "--verbose", dest="verbose", action="count",
                        default=False,
                        help="Print out debug and info messages.")

    parser.add_argument('--version', action='version', version='"USS test" Revision %s' % REVISION_NUMBER)

    parser.add_argument('-p', '--port', required=True, type=str,
                        help="Specifies serial device where EVSE is connected.")

    parser.add_argument('-ddiff', '--duty_cycle_diff', required=True, type=int,
                        help="Maximum allowed difference of measured pwm duty cycle to check.")

    parser.add_argument('-fdiff', '--frequency_diff', required=True, type=int,
                        help="Maximum allowed difference of measured frequency to check.")

    parser.add_argument('-ul', '--ucp_low', required=True, type=float,
                        help="Nominal value of control pilot low voltage to check.")

    parser.add_argument('-uld', '--ucp_low_diff', required=True, type=float,
                        help="Maximum allowed difference of control pilot low voltage to check.")

    parser.add_argument('-uh', '--ucp_high', required=True, type=float,
                        help="Nominal value of control pilot high voltage to check.")

    parser.add_argument('-uhd', '--ucp_high_diff', required=True, type=float,
                        help="Maximum allowed difference of control pilot high voltage to check.")

    parser.add_argument('-pp', '--pp', required=True, type=float,
                        help="Nominal value of proximity pilot voltage to check.")

    parser.add_argument('-ppd', '--pp_diff', required=True, type=float,
                        help="Maximum allowed difference of proximity pilot voltage to check.")

    parser.add_argument('-d', '--measurement_delay', default=.1, type=float,
                        help="The time to wait between measurements in seconds. Default is 0.1 s.")

    parser.add_argument('-f', '--valid_file', default="valid", type=str,
                        help="The file path for the file to create if all parameter are in valid range. Default is 'valid'.")

    parser.add_argument('--pid_file', default="", type=str,
                        help="The file path for the file which stores the process ID. Default is None.")

    return parser.parse_args()


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


def _handle_validation_file(valid_file, error_state):
    # Check whether validation file exists.
    try:
        with open(valid_file):
            pass
        file_exists = True
    except IOError:
        file_exists = False

    if error_state:
        # Remove validation file if exists...
        if file_exists:
            os.remove(valid_file)
    else:
        # Creating file for showing that all parameter are in valid range.
        if not file_exists:
            logging.info("Validation results back to normal.")
            open(valid_file, 'w')


def _test_port(args):

    # Preparing port for measurements.
    with build_comfort_port(args.port) as port:

        # Enable pwm output
        _control_pwm(port, True)

        # Enable PP pullup resistor
        port.set_pp_pullup(True)

        try:
            error = {}
            while True:
                for i in PWM_TEST_DUTY:
                    port.set_pwm(i)
                    time.sleep(args.measurement_delay)
                    port.update()
                    duty, freq = port.get_pwm()
                    ucp_high, ucp_low = port.get_ucp_voltage()
                    pp = port.get_pp_voltage()

                    if abs(duty-i) > args.duty_cycle_diff:
                        if not error.get('duty'):
                            logging.warn("Duty cycle has reached limit: (Measured %d per mill, expected %d)" % (duty, i))
                        error['duty'] = True
                    else:
                        if error.get('duty'):
                            logging.info("Duty is back to normal: %f" % duty)
                        error['duty'] = False

                    if abs(freq-PWM_STANDARD_FREQUENCY) > args.frequency_diff:
                        if not error.get('freq'):
                            logging.warn("Frequency has reached limit: (Measured %d Hz, expected 1000Hz)" % freq)
                        error['freq'] = True
                    else:
                        if error.get('freq'):
                            logging.info("Frequency is back to normal: %f" % freq)
                        error['freq'] = False

                    if abs(ucp_high-args.ucp_high) > args.ucp_high_diff:
                        if not error.get('ucp_high'):
                            logging.warn("High CP voltage has reached limit @ duty %d: (Measured %f, expected %f)" % (i, ucp_high, args.ucp_high))
                        error['ucp_high'] = True
                    else:
                        if error.get('ucp_high'):
                            logging.info("High CP voltage is back to normal: %f" % ucp_high)
                        error['ucp_high'] = False

                    if abs(ucp_low-args.ucp_low) > args.ucp_low_diff:
                        if not error.get('ucp_low'):
                            logging.warn("Low CP voltage has reached limit @ duty %d: (Measured %f, expected %f)" % (i, ucp_low, args.ucp_low))
                        error['ucp_low'] = True
                    else:
                        if error.get('ucp_low'):
                            logging.info("Low CP voltage is back to normal: %f" % ucp_low)
                        error['ucp_low'] = False

                    if abs(pp-args.pp) > args.pp_diff:
                        if not error.get('pp'):
                            logging.warn("PP voltage has reached limit: (Measured %f, expected %f)" % (pp, args.pp))
                        error['pp'] = True
                    else:
                        if error.get('pp'):
                            logging.info("PP voltage is back to normal: %f" % pp)
                        error['pp'] = False


                    for error_state in error.values():
                        if error_state:
                            break

                    _handle_validation_file(args.valid_file, error_state)


        except KeyboardInterrupt:
            # User break. Clean up.

            # Disable PP pullup resistor
            port.set_pp_pullup(False)

            # Disable pwm output
            _control_pwm(port, True)

            # Give away the KeyboardInterrupt to the caller...
            raise KeyboardInterrupt


def main():
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


    # Remove the validation file for now.
    _handle_validation_file(args.valid_file, True)

    # Create PID file
    if args.pid_file:
        logging.info("Creating PID file...")
        with open(args.pid_file, 'w') as f:
            f.write("%d\n" % os.getpid())


    # Test the port forever...
    while True:
        try:
            # Function never returns if no exceptions occur..
            _test_port(args)
        except KeyboardInterrupt:
            break
        except (UssPortReadError, UssPortError, UssStatusError) as exc:
            try:
                # Remove validation file
                logging.warn("Error on USS port occured: %s" % exc)
                _handle_validation_file(args.valid_file, True)
                # Just wait for a second and try again to open and handle port...
                time.sleep(2)
            except KeyboardInterrupt:
                break


    # Remove the validation file at the end.
    _handle_validation_file(args.valid_file, True)


if __name__ == '__main__':
    main()
