import sys
import asyncio
import os
import json
import logging

from iso15118.secc import SECCHandler
from iso15118.secc.secc_settings import Config as SeccConfig # Renamed to avoid conflict
from iso15118.secc.controller.interface import ServiceStatus
from iso15118.shared.exificient_exi_codec import ExificientEXICodec

sys.path.append("../")

from chargebyte.chargebyte_charging_station import ChargebyteChargingStation
from elektroautomatik.bidi_powersupply import ElektroAutomatikBidiPowersupply
from iso15118impls.evse_controller import EVSEControllerImpl
from mocks.charging_station import MockChargingStation
from mocks.high_voltage_source import MockHighVoltageSource

### SLAC imports ###
from pyslac.environment import Config as SlacConfig
from pyslac.utils import is_distro_linux


def create_high_voltage_controller(impl_type: str):
    """Create high voltage controller based on implementation type"""
    if impl_type == "elektroautomatik":
        return ElektroAutomatikBidiPowersupply("192.168.188.100", 5025, 3000)
    elif impl_type == "mock":
        return MockHighVoltageSource()
    else:
        raise ValueError(f"Unknown HIGH_VOLTAGE_CONTROLLER_IMPL: {impl_type}")


def create_din_61851_controller(impl_type: str):
    """Create DIN 61851 controller based on implementation type"""
    if impl_type == "chargebyte":
        return ChargebyteChargingStation("192.168.188.250", 2020, True)
    elif impl_type == "mock":
        return MockChargingStation()
    else:
        raise ValueError(f"Unknown DIN_61851_IMPL: {impl_type}")


async def run_slac_simulation(controller: EVSEControllerImpl):
    """
    Simulates the CP state changes to trigger the SLAC matching process.
    """
    await asyncio.sleep(2)
    
    if not controller.running_sessions:
        logger.error("No running SLAC sessions to simulate.")
        return

    session_to_test = controller.running_sessions[0]
    logger.info(f"Starting SLAC simulation for EVSE {session_to_test.evse_id}")
    
    await controller.enable_hlc_charging(session_to_test.evse_id)
    await controller.process_cp_state(session_to_test, "B")
    await asyncio.sleep(2)
    await controller.process_cp_state(session_to_test, "C")
    await asyncio.sleep(20)
    await controller.process_cp_state(session_to_test, "A")
    logger.info("SLAC simulation finished.")

logger = logging.getLogger(__name__)

async def main():
    """
    Entrypoint function that starts the ISO 15118 code running on
    the SECC (Supply Equipment Communication Controller)
    """

    logger = logging.getLogger(__name__)

    # Slac
    if not is_distro_linux():
        raise EnvironmentError("Non-Linux systems are not supported for SLAC")
    #

    # Get implementation types from environment variables
    hv_impl = os.environ.get("HIGH_VOLTAGE_CONTROLLER_IMPL", "mock")
    din_impl = os.environ.get("DIN_61851_IMPL", "mock")
     
    # Create controllers based on configuration
    try:
        psu = create_high_voltage_controller(hv_impl)
        low_level = create_din_61851_controller(din_impl)
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        return

    secc_config = SeccConfig()
    secc_config.load_envs()
    secc_config.print_settings()

    ## Slac
    slac_config = SlacConfig()
    slac_config.load_envs()

    try:
        with open("cs_configuration.json", "r") as f:
            cs_config = json.load(f)
    except FileNotFoundError:
        logger.error("cs_configuration.json not found. SLAC cannot be initialized.")
        return

    controller = EVSEControllerImpl(psu, low_level, slac_config)

    try:
        await controller.start_slac_sessions(cs_config)
    except (RuntimeError, AttributeError) as e:
        logger.error(f"Failed to start SLAC: {e}")
        return 
    ##
    
    secc_handler_task = SECCHandler(
        exi_codec=ExificientEXICodec(),
        evse_controller=controller,
        config=secc_config,
    ).start(secc_config.iface)

    slac_sim_task = run_slac_simulation(controller)

    await asyncio.gather(secc_handler_task, slac_sim_task)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("SECC program terminated manually")