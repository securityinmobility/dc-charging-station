from pyslac.utils import is_distro_linux

if not is_distro_linux():
    raise EnvironmentError("Non-Linux systems are not supported")

import asyncio
import json
import logging
import os
from typing import List, Optional

from pyslac.environment import Config
from pyslac.session import SlacEvseSession, SlacSessionController
from pyslac.utils import wait_for_tasks

from base_classes import ChargingStation

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__file__)


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

    async def start(self, cs_config: dict):
        if cs_config["number_of_evses"] < 1 or (
            len(cs_config["parameters"]) != cs_config["number_of_evses"]
        ):
            raise AttributeError("Number of evses provided is invalid.")

        evse_params: dict = cs_config["parameters"][0]
        evse_id: str = evse_params["evse_id"]
        network_interface: str = evse_params["network_interface"]
        try:
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

        

    # low level state reading (extra task)


def get_slac_handler( _low_level_abstraction: ChargingStation, env_path: Optional[str] = None) -> SlacHandler:
    """
    Factory function to create a SlacHandler instance with the given low-level abstraction.
    """
    slac_config = Config()
    slac_config.load_envs(env_path)

    return SlacHandler(slac_config, _low_level_abstraction)

def get_cs_config() -> dict:
    """
    Factory function to get the charging station configuration.
    """
    try:
        with open("./iso15118impls/cs_configuration.json", "r") as f:
            cs_config = json.load(f)
    except FileNotFoundError:
        logger.error("cs_configuration.json not found. SLAC cannot be initialized.")
        return {}
    return cs_config


