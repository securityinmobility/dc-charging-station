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

            if os.environ.get("NMK") and os.environ.get("NID"):
                slac_session.evse_set_key = types.MethodType(custom_evse_set_key, slac_session)
                await slac_session.evse_set_key()
            else:
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


# adapted evse_set_key function for the specific chargebyte charging station
async def custom_evse_set_key(self) -> bytes:
    """
    Set the EVSE key for the session.
    This function is adapted to work with the ChargebyteChargingStation.
    """
    from binascii import unhexlify
    from pyslac.layer_2_headers import EthernetHeader, HomePlugHeader
    from pyslac.messages import SetKeyReq, SetKeyCnf
    from pyslac.enums import FramesSizes, Timers, MMTYPE_REQ, CM_SET_KEY, SLAC_SETTLE_TIME

    logger.info("CM_SET_KEY: Started...")
    # Set NMK and NID with the environment variables NMK and NID 
    nmk = unhexlify(os.environ.get("NMK"))
    nid = unhexlify(os.environ.get("NID"))
    logger.debug("New NMK: %s", os.environ.get("NMK"))
    logger.debug("New NID: %s", os.environ.get("NID"))
    ethernet_header = EthernetHeader(
        dst_mac=self.evse_plc_mac, src_mac=self.evse_mac
    )
    homeplug_header = HomePlugHeader(CM_SET_KEY | MMTYPE_REQ)
    key_req_payload = SetKeyReq(nid=nid, new_key=nmk)

    frame_to_send = (
        ethernet_header.pack_big()
        + homeplug_header.pack_big()
        + key_req_payload.pack_big()
    )

    # TODO: Change this to just open a socket once for every SlacSession
    # and not every time we call send or send_recv_eth
    # Also think about including the send, rcv method as inner methods of
    # SetKeyReq. Maybe even create a class SetKey that handles both the
    # Send and the CNF of the message
    try:
        await self.send_frame(frame_to_send)
        data_rcvd = await self.rcv_frame(
            rcv_frame_size=FramesSizes.CM_SET_KEY_CNF,
            timeout=Timers.SLAC_INIT_TIMEOUT,
        )
    except asyncio.TimeoutError as e:
        raise TimeoutError("SetKey Timeout raised") from e
    try:
        SetKeyCnf.from_bytes(data_rcvd)
        self.nmk = nmk
        self.nid = nid
    except ValueError as e:
        logger.error(e)
        if self.nmk and self.nid:
            logger.debug(
                "SetKeyReq has failed, old NMK: %s and NID: %s apply",
                self.nmk,
                self.nid,
            )
        else:
            raise ValueError("SetKeyCnf data parsing into the class failed") from e
    logger.debug("Registering NMK and NID into the PLC node...")
    await asyncio.sleep(SLAC_SETTLE_TIME)
    logger.info("CM_SET_KEY: Finished!")
    return data_rcvd

def get_slac_handler(low_level_abstraction: ChargingStation, env_path: Optional[str] = None) -> SlacHandler:
    """
    Factory function to create a SlacHandler instance with the given low-level abstraction.
    """
    slac_config = Config()
    slac_config.load_envs(env_path)

    return SlacHandler(slac_config, low_level_abstraction)

def get_cs_config(network_interface) -> dict:
    """
    Factory function to get the charging station configuration.
    """
    CONFIG_PATH = Path(__file__).parent / "cs_configuration.json"

    try:
        with open(CONFIG_PATH, "r") as f:
            cs_config = json.load(f)
            if cs_config["number_of_evses"] == 1:
                cs_config["parameters"][0]["network_interface"] = network_interface
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON from {CONFIG_PATH}: {e}")
        return {}
    except FileNotFoundError:
        logger.error("cs_configuration.json not found. SLAC cannot be initialized.")
        return {}
    return cs_config


