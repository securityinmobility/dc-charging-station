import sys
import asyncio
import os
import logging

from iso15118.secc import SECCHandler
from iso15118.secc.secc_settings import Config
from iso15118.secc.controller.interface import ServiceStatus
from iso15118.shared.exificient_exi_codec import ExificientEXICodec

from iso15118impls.slac_session import get_slac_handler
from pyslac.utils import wait_for_tasks

sys.path.append("../")

from chargebyte.chargebyte_charging_station import ChargebyteChargingStation
from elektroautomatik.bidi_powersupply import ElektroAutomatikBidiPowersupply
from iso15118impls.evse_controller import EVSEControllerImpl
from mocks.charging_station import MockChargingStation
from mocks.high_voltage_source import MockHighVoltageSource
from pki.chargebyte import obtain_certificate


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


async def update_certificate(evse_id: str):
    """Make sure we have an up to date SECC certificate from the Hubject PKI.

    Only runs if Hubject credentials are configured. Failures are logged but do
    not stop the charging station, it can still be used without Plug & Charge.
    """
    logger = logging.getLogger(__name__)
    if not os.environ.get("HUBJECT_CLIENT_ID") or not os.environ.get(
        "HUBJECT_CLIENT_SECRET"
    ):
        logger.info(
            "HUBJECT_CLIENT_ID/HUBJECT_CLIENT_SECRET are not set, "
            "using the stored certificates as they are"
        )
        return

    try:
        certificate = await asyncio.to_thread(obtain_certificate, evse_id)
        logger.info(f"Using the SECC certificate {certificate}")
    except Exception as e:
        logger.error(f"Could not obtain a SECC certificate from Hubject: {e}")


async def main():
    """
    Entrypoint function that starts the ISO 15118 code running on
    the SECC (Supply Equipment Communication Controller)
    """
    # Get implementation types from environment variables
    hv_impl = os.environ.get("HIGH_VOLTAGE_CONTROLLER_IMPL", "mock")
    din_impl = os.environ.get("DIN_61851_IMPL", "mock")
    evse_id = os.environ.get("EVSE_ID", "DE*THI*H007000000") 
    target_power = int(os.environ.get("TARGET_POWER", "3000"))

    await update_certificate(evse_id)

    # Create controllers based on configuration
    try:
        psu = create_high_voltage_controller(hv_impl)
        low_level = create_din_61851_controller(din_impl)
    except ValueError as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Configuration error: {e}")
        return

    config = Config()
    config.load_envs()
    config.print_settings()

    slac_handler = get_slac_handler(low_level)
    
    controller = EVSEControllerImpl(psu, low_level)
    await controller.set_status(ServiceStatus.STARTING)

    def current_adjust(target_current):
        if target_current < 1:
            return target_current

        volts = controller.evse_data_context.present_voltage
        new_target = target_power / volts
        if abs(new_target) > abs(target_current):
            return target_current

        return new_target
    controller.set_current_adjust_function(current_adjust)

    secc_handler = SECCHandler(
        exi_codec=ExificientEXICodec(),
        evse_controller=controller,
        config=config,
    )

    tasks = [
        secc_handler.start(config.iface),
        slac_handler.start(config.iface, evse_id),
    ]

    await wait_for_tasks(tasks)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger = logging.getLogger(__name__)
        logger.debug("SECC program terminated manually")