import asyncio
import logging
import traceback
from typing import List, Optional, Callable, NamedTuple

from iso15118.secc import SECCHandler
from iso15118.secc.secc_settings import Config
from iso15118.secc.controller.interface import ServiceStatus
from iso15118.shared.utils import load_requested_auth_modes, load_requested_protocols
from iso15118.shared.messages.enums import AuthEnum, Protocol
from iso15118.shared.exificient_exi_codec import ExificientEXICodec

from chargebyte.chargebyte_charging_station import ChargebyteChargingStation, ResistorCode
from elektroautomatik.bidi_powersupply import ElektroAutomatikBidiPowersupply
from iso15118impls.evse_controller import EVSEControllerImpl

from mocks.charging_station import MockChargingStation
from mocks.high_voltage_source import MockHighVoltageSource

logger = logging.getLogger(__name__)

class CapabilityTest(NamedTuple):
    name: str
    duration: float
    protocols: List[Protocol]
    auth_options: List[AuthEnum]
    enforce_tls: bool
    current_adjustment: Optional[Callable[[float], float]]

all_protocols = Protocol.allowed_protocols()
eim = [AuthEnum.EIM, AuthEnum.EIM_V2]
pnc = [AuthEnum.PNC, AuthEnum.PNC_V2]

tests = [
    #              name,                duration, protocols            auth,enforce TLS, current_adjustment
    CapabilityTest("basic charging",           3 * 60, all_protocols,                     eim, False, None),
    CapabilityTest("dinspec only",             60,     ["DIN_SPEC_70121"],                eim, False, None),
    CapabilityTest("-2 only",                  60,     ["ISO_15118_2"],                   eim, False, None),
    CapabilityTest("-20 AC only",              60,     ["ISO_15118_20_AC"],               eim, False, None),
    CapabilityTest("-20 DC only",              60,     ["ISO_15118_20_DC"],               eim, False, None),
    CapabilityTest("-2 with enforced TLS",     60,     ["ISO_15118_2"],                   eim, True,  None),
    CapabilityTest("-20 AC with enforced TLS", 60,     ["ISO_15118_20_AC"],               eim, True,  None),
    CapabilityTest("-20 DC with enforced TLS", 60,     ["ISO_15118_20_DC"],               eim, True,  None),
    CapabilityTest("discharging",              3 * 60, ["DIN_SPEC_70121", "ISO_15118_2"], eim, False, lambda current: current if current < 1 else -1 * current),
    CapabilityTest("-2 PnC",                   5,      ["ISO_15118_2"],                   pnc, False, None),
    CapabilityTest("-20 AC PnC",               5,      ["ISO_15118_20_AC"],               pnc, False,  None),
    CapabilityTest("-20 DC PnC",               5,      ["ISO_15118_20_DC"],               pnc, False,  None),
]

async def run_secc(controller: EVSEControllerImpl, config: Config):
    await controller.set_status(ServiceStatus.STARTING)
    await SECCHandler(
        exi_codec=ExificientEXICodec(),
        evse_controller=controller,
        config=config,
    ).start(config.iface)

async def run_one_test(controller: EVSEControllerImpl, config: Config, low_level: ChargebyteChargingStation, test: CapabilityTest):
    logging.info("TEST %s: Initializing: %s", test.name, str(test))
    config.supported_protocols = load_requested_protocols(test.protocols)
    config.supported_auth_options = test.auth_options
    config.enforce_tls = test.enforce_tls
    controller.set_current_adjust_function(test.current_adjustment)

    logging.info("TEST %s: Enabling PP resistor and CP PWM", test.name)
    low_level.enable_pp_resistor()
    low_level.set_pwm_duty_cycle(5)

    logging.info("TEST %s: Waiting for charging to start", test.name)
    wait_time = 0
    while not controller.is_busy.is_set():
        await asyncio.sleep(0.1)
        wait_time += 0.1
        if wait_time >= 10:
            raise TimeoutError("Vehicle did not connect in time / Charging did not start correctly")

    logging.info("TEST %s: Running chargeloop for %s seconds", test.name, test.duration)
    duration = test.duration
    while duration > 0:
        if not controller.is_busy.is_set():
            logging.info("TEST %s: Chargeloop stopped before planned", test.name)
            break

        await asyncio.sleep(min(1, duration))
        duration -= 1

    logging.info("TEST %s: Stopping charge", test.name)
    controller.shall_stop.set()
    # TODO add timeout
    while controller.is_busy.is_set():
        await asyncio.sleep(0.1)

    logging.info("TEST %s: Waiting 5s for charge stop to settle", test.name)
    await asyncio.sleep(5)
    controller.shall_stop.clear()

    logging.info("TEST %s: Virtually disconnecting charge cable", test.name)
    low_level.set_pwm_duty_cycle(0)
    low_level.disable_pp_resistor()

async def run_all_tests(controller: EVSEControllerImpl, config: Config, low_level: ChargebyteChargingStation):
    for test in tests:
        try:
            await run_one_test(controller, config, low_level, test)
        except:
            traceback.print_exc()

        logging.info("Waiting 10 seconds between tests...")
        await asyncio.sleep(10)

        # clear shall stop in case this was not correctly cleared because of abnormal stopping
        controller.shall_stop.clear()

    logging.info("Done running all tests!")


async def main():
    """
    Entrypoint function that starts the ISO 15118 code running on
    the SECC (Supply Equipment Communication Controller)
    """
    low_level = MockChargingStation()
    psu = MockHighVoltageSource()

    #low_level = ChargebyteChargingStation("192.168.188.250", 2020, True)
    #psu = ElektroAutomatikBidiPowersupply("192.168.188.100", 5025, 3000)

    config = Config()
    config.load_envs()

    controller = EVSEControllerImpl(psu, low_level)

    await asyncio.gather(run_secc(controller, config), run_all_tests(controller, config, low_level))



if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.debug("SECC program terminated manually")

