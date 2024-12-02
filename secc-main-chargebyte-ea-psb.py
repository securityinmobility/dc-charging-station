import sys
import asyncio

from iso15118.secc import SECCHandler
from iso15118.secc.secc_settings import Config
from iso15118.secc.controller.interface import ServiceStatus
from iso15118.shared.exificient_exi_codec import ExificientEXICodec

sys.path.append('../')

from chargebyte.chargebyte_charging_station import ChargebyteChargingStation
from elektroautomatik.bidi_powersupply import ElektroAutomatikBidiPowersupply
from iso15118impls.evse_controller import EVSEControllerImpl

from mocks.charging_station import MockChargingStation
from mocks.high_voltage_source import MockHighVoltageSource

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
    config.print_settings()

    controller = EVSEControllerImpl(psu, low_level)
    await controller.set_status(ServiceStatus.STARTING)
    await SECCHandler(
        exi_codec=ExificientEXICodec(),
        evse_controller=controller,
        config=config,
    ).start(config.iface)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.debug("SECC program terminated manually")

