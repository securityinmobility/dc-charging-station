from binascii import unhexlify
from pyslac.utils import is_distro_linux

if not is_distro_linux():
    raise EnvironmentError("Non-Linux systems are not supported")

import asyncio
import json
from pathlib import Path
import logging
import types
import os
from typing import List, Optional
from binascii import unhexlify

from pyslac.environment import Config
from pyslac.session import SlacEvseSession, SlacSessionController
from pyslac.utils import wait_for_tasks

from base_classes import ChargingStation

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__file__)

class SpecificSlacEvseSession(SlacEvseSession):
    """
    A subclass of SlacEvseSession that overrides the evse_set_key method
    to work with the ChargebyteChargingStation.
    """
    def __init__(self, evse_id: str, network_interface: str, slac_config: Config, NMK: str, NID: str):
        super().__init__(evse_id, network_interface, slac_config)
        self.NMK = NMK
        self.NID = NID

    async def evse_set_key(self):
        """
        Set the EVSE key for the session.
        This function is adapted to work with the ChargebyteChargingStation.
        """
        logger.info("CM_SET_KEY: Started...")
        # Set NMK and NID with the environment variables NMK and NID 
        nmk = unhexlify(self.NMK)
        nid = unhexlify(self.NID)
        logger.debug("New NMK: %s", self.NMK)
        logger.debug("New NID: %s", self.NID)

        self.nmk = nmk
        self.nid = nid
        logger.info("CM_SET_KEY: Finished!")


class SlacHandler(SlacSessionController):
    def __init__(self, slac_config: Config, _low_level_abstraction: ChargingStation):
        SlacSessionController.__init__(self)
        self.slac_config = slac_config
        self.running_sessions: List["SlacEvseSession"] = []

        self.low_level_abstraction = _low_level_abstraction

    async def notify_matching_ongoing(self, evse_id: str):
        """overrides the notify matching ongoing method defined in
        SlacSessionController"""
        logger.info(f"Matching is ongoing for {evse_id}")

    async def notify_matching_failed(self, evse_id: str):
        """overrides the notify matching failed method defined in
        SlacSessionController"""
        logger.info(f"Matching failed for {evse_id}")

    async def enable_hlc_charging(self, evse_id: str):
        """
        overrides the enable_hlc_charging method defined in SlacSessionController
        """
        self.low_level_abstraction.set_pwm_duty_cycle(5.0)
        logger.info(f"Enable PWM and set 5% duty cycle for evse {evse_id}")

    async def start(self, network_interface: str, evse_id: str):
        if network_interface is None:
            raise ValueError("Network interface must be provided")

        if evse_id is None:
            raise ValueError("EVSE ID must be provided")

        try:
            if os.environ.get("NMK") and os.environ.get("NID"):
                slac_session = SpecificSlacEvseSession(evse_id, network_interface, self.slac_config, os.environ.get("NMK"), os.environ.get("NID"))
                await slac_session.evse_set_key()
            else:
                slac_session = SlacEvseSession(evse_id, network_interface, self.slac_config)
                await slac_session.evse_set_key()

            self.running_sessions.append(slac_session)
        except (OSError, TimeoutError, ValueError) as e:
            logger.error(
                f"PLC chip initialization failed for "
                f"EVSE {evse_id}, interface "
                f"{network_interface}: {e}. \n"
                f"Please check your settings."
            )
            return

        await self.enable_hlc_charging(self.running_sessions[0].evse_id)

        while True:
            try:
                state = self.low_level_abstraction.get_state()
                await self.process_cp_state(self.running_sessions[0], state.value)
            except Exception as e:
                logger.error(f"Error during polling: {e}")

            await asyncio.sleep(0.2)  # Polling interval


def get_slac_handler(low_level_abstraction: ChargingStation, env_path: Optional[str] = None) -> SlacHandler:
    """
    Factory function to create a SlacHandler instance with the given low-level abstraction.
    """
    slac_config = Config()
    slac_config.load_envs(env_path)

    return SlacHandler(slac_config, low_level_abstraction)



