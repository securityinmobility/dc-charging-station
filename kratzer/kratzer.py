import socket
import struct
import threading
from threading import Thread, Lock
import threading
from master_to_slave import MasterToSlave
from slave_to_master import SlaveToMaster
from time import sleep

# Based on the circuit diagram, the charge controller shall have the IP 192.168.1.100 and the PC has 192.168.1.102


class Kratzer:
    def __init__(self, IP: str):
        self.s2m = SlaveToMaster()
        self.m2s = MasterToSlave()
        port_STM = 5000
        port_MTS = 5100
        self.socket_STM = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket_STM.bind((IP, port_STM))
        self.socket_MTS = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket_MTS.bind((IP, port_MTS))
        self.mutex = threading.Lock()
        self.ip = IP
        self.stop_event = threading.Event()

    def get_S2M_AS_SW1(self) -> int | float:
        return self.s2m.values["S2M_AS_SW1"]

    def get_S2M_AS_SW2(self):
        return self.s2m.values["S2M_AS_SW2"]

    def get_S2M_AV_U(self):
        return self.s2m.values["S2M_AV_U"]

    def get_S2M_AV_I(self):
        return self.s2m.values["S2M_AV_I"]

    def get_S2M_AV_P(self):
        return self.s2m.values["S2M_AV_P"]

    def get_S2M_SPV_Umin(self):
        return self.s2m.values["S2M_SPV_Umin"]

    def get_S2M_SPV_Umax(self):
        return self.s2m.values["S2M_SPV_Umax"]

    def get_S2M_SPV_LIMIT_Umin(self):
        return self.s2m.values["S2M_SPV_LIMIT_Umin"]

    def get_S2M_SPV_LIMIT_Umax(self):
        return self.s2m.values["S2M_SPV_LIMIT_Umax"]

    def get_S2M_SPV_LIMIT_Imin(self):
        return self.s2m.values["S2M_SPV_LIMIT_Imin"]

    def get_S2M_SPV_LIMIT_Imax(self):
        return self.s2m.values["S2M_SPV_LIMIT_Imax"]

    def get_S2M_AS_BATT_R1(self):
        return self.s2m.values["S2M_AS_BATT_R1"]

    def get_VS2M_AS_BATT_R2(self):
        return self.s2m.values["VS2M_AS_BATT_R2"]

    def get_S2M_AS_BATT_R3(self):
        return self.s2m.values["S2M_AS_BATT_R3"]

    def get_S2M_AS_BATT_R4(self):
        return self.s2m.values["S2M_AS_BATT_R4"]

    def get_S2M_AS_BATT_C1(self):
        return self.s2m.values["S2M_AS_BATT_C1"]

    def get_S2M_AV_BATT_I_filter(self):
        return self.s2m.values["S2M_AV_BATT_I_filter"]

    def get_S2M_AV_BATT_U0_A(self):
        return self.s2m.values["S2M_AV_BATT_U0_A"]

    def get_S2M_AV_REG_KP_I(self):
        return self.s2m.values["S2M_AV_REG_KP_I"]

    def get_S2M_AV_REG_TN_I(self):
        return self.s2m.values["S2M_AV_REG_TN_I"]

    def get_S2M_AV_REG_KP_U(self):
        return self.s2m.values["S2M_AV_REG_KP_U"]

    def get_S2M_AV_REG_TN_U(self):
        return self.s2m.values["S2M_AV_REG_TN_U"]

    def get_S2M_AV_REG_KP_M(self):
        return self.s2m.values["S2M_AV_REG_KP_M"]

    def get_S2M_AV_REG_TN_M(self):
        return self.s2m.values["S2M_AV_REG_TN_M"]

    def get_S2M_AV_REG_U_ramp(self):
        return self.s2m.values["S2M_AV_REG_U_ramp"]

    def get_S2M_AV_REG_I_ramp(self):
        return self.s2m.values["S2M_AV_REG_I_ramp"]

    def get_S2M_AS_REG_ParSet(self):
        return self.s2m.values["S2M_AS_REG_ParSet"]

    def get_S2M_AS_REG_ParSet_Err(self):
        return self.s2m.values["S2M_AS_REG_ParSet_Err"]

    def get_S2M_AV_REG_Mode(self):
        return self.s2m.values["S2M_AV_REG_Mode"]

    def get_S2M_AS_BATT_Model(self):
        return self.s2m.values["S2M_AS_BATT_Model"]

    def get_S2M_AS_ZR_Error_a(self):
        return self.s2m.values["S2M_AS_ZR_Error_a"]

    def get_S2M_AS_ZR_Error_b(self):
        return self.s2m.values["S2M_AS_ZR_Error_b"]

    def get_S2M_AS_UWR_Error_a(self):
        return self.s2m.values["S2M_AS_UWR_Error_a"]

    def get_S2M_AS_UWR_error_b(self):
        return self.s2m.values["S2M_AS_UWR_error_b"]

    def get_S2M_AS_RK_Error_a(self):
        return self.s2m.values["S2M_AS_RK_Error_a"]

    def get_S2M_AS_RK_Error_b(self):
        return self.s2m.values["S2M_AS_RK_Error_b"]

    def get_S2M_AS_TSB_Error_a(self):
        return self.s2m.values["S2M_AS_TSB_Error_a"]

    def get_S2M_AS_TSB_Error_b(self):
        return self.s2m.values["S2M_AS_TSB_Error_b"]

    def get_S2M_AS_BATT_C2(self):
        return self.s2m.values["S2M_AS_BATT_C2"]

    def get_S2M_AS_BATT_L1(self):
        return self.s2m.values["S2M_AS_BATT_L1"]

    def get_S2M_AV_BATT_U0_B(self):
        return self.s2m.values["S2M_AV_BATT_U0_B"]

    def get_S2M_AS_TSB_Error_c(self):
        return self.s2m.values["S2M_AS_TSB_Error_c"]

    def get_S2M_AV_BATT_SOC(self):
        return self.s2m.values["S2M_AV_BATT_SOC"]

    def set_M2S_RS_CW1(self, new_value: int):
        self.mutex.acquire()
        self.m2s.values["M2S_RS_CW1"] = new_value
        self.mutex.release()

    def set_M2S_M2S_SP_U(self, new_value: float):
        self.mutex.acquire()
        self.m2s.values["M2S_M2S_SP_U"] = new_value
        self.mutex.release()

    def set_M2S_M2S_SP_Imin(self, new_value: float):
        self.mutex.acquire()
        self.m2s.values["M2S_M2S_SP_U"] = new_value
        self.mutex.release()
        self.m2s.values["M2S_M2S_SP_Imin"] = new_value

    def set_M2S_M2S_SP_Imax(self, new_value: float):
        self.mutex.acquire()
        self.m2s.values["M2S_M2S_SP_U"] = new_value
        self.mutex.release()
        self.m2s.values["M2S_M2S_SP_Imax"] = new_value

    def set_M2S_M2S_SP_Umin(self, new_value: float):
        self.mutex.acquire()
        self.m2s.values["M2S_M2S_SP_Umin"] = new_value
        self.mutex.release()

    def set_M2S_M2S_SP_Umax(self, new_value: float):
        self.mutex.acquire()
        self.m2s.values["M2S_M2S_SP_Umax"] = new_value
        self.mutex.release()

    def set_M2S_M2S_SP_LIMIT_Umin(self, new_value: float):
        self.mutex.acquire()
        self.m2s.values["M2S_M2S_SP_LIMIT_Umin"] = new_value
        self.mutex.release()

    def set_M2S_M2S_SP_LIMIT_Umax(self, new_value: float):
        self.mutex.acquire()
        self.m2s.values["M2S_M2S_SP_LIMIT_Umax"] = new_value
        self.mutex.release()

    def set_M2S_M2S_SP_LIMIT_Imin(self, new_value: float):
        self.mutex.acquire()
        self.m2s.values["M2S_M2S_SP_LIMIT_Imin"] = new_value
        self.mutex.release()

    def set_M2S_M2S_SP_LIMIT_Imax(self, new_value: float):
        self.mutex.acquire()
        self.m2s.values["M2S_M2S_SP_LIMIT_Imax"] = new_value
        self.mutex.release()

    def set_M2S_M2S_SP_BATT_R1(self, new_value: float):
        self.mutex.acquire()
        self.m2s.values["M2S_M2S_SP_BATT_R1"] = new_value
        self.mutex.release()

    def set_M2S_M2S_SP_BATT_R2(self, new_value: float):
        self.mutex.acquire()
        self.m2s.values["M2S_M2S_SP_BATT_R2"] = new_value
        self.mutex.release()

    def set_M2S_M2S_SP_BATT_R3(self, new_value: float):
        self.mutex.acquire()
        self.m2s.values["M2S_M2S_SP_BATT_R3"] = new_value
        self.mutex.release()

    def set_M2S_M2S_SP_BATT_R4(self, new_value: float):
        self.mutex.acquire()
        self.m2s.values["M2S_M2S_SP_BATT_R4"] = new_value
        self.mutex.release()

    def set_M2S_M2S_SP_BATT_C1(self, new_value: float):
        self.mutex.acquire()
        self.m2s.values["M2S_M2S_SP_BATT_C1"] = new_value
        self.mutex.release()

    def set_M2S_M2S_SP_REG_I_Filter(self, new_value: float):
        self.mutex.acquire()
        self.m2s.values["M2S_M2S_SP_REG_I_Filter"] = new_value
        self.mutex.release()

    def set_M2S_M2S_SP_REG_U0_A(self, new_value: float):
        self.mutex.acquire()
        self.m2s.values["M2S_M2S_SP_REG_U0_A"] = new_value
        self.mutex.release()

    def set_M2S_M2S_SP_REG_KP_I(self, new_value: float):
        self.mutex.acquire()
        self.m2s.values["M2S_M2S_SP_REG_KP_I"] = new_value
        self.mutex.release()

    def set_M2S_M2S_SP_REG_TN_I(self, new_value: float):
        self.mutex.acquire()
        self.m2s.values["M2S_M2S_SP_REG_TN_I"] = new_value
        self.mutex.release()

    def set_M2S_M2S_SP_REG_KP_U(self, new_value: float):
        self.mutex.acquire()
        self.m2s.values["M2S_M2S_SP_REG_KP_U"] = new_value
        self.mutex.release()

    def set_M2S_M2S_SP_REG_TN_U(self, new_value: float):
        self.mutex.acquire()
        self.m2s.values["M2S_M2S_SP_REG_TN_U"] = new_value
        self.mutex.release()

    def set_M2S_M2S_SP_REG_KP_M(self, new_value: float):
        self.mutex.acquire()
        self.m2s.values["M2S_M2S_SP_REG_KP_M"] = new_value
        self.mutex.release()

    def set_M2S_M2S_SP_REG_TN_M(self, new_value: float):
        self.mutex.acquire()
        self.m2s.values["M2S_M2S_SP_REG_TN_M"] = new_value
        self.mutex.release()

    def set_M2S_M2S_SP_REG_U_Ramp(self, new_value: float):
        self.mutex.acquire()
        self.m2s.values["M2S_M2S_SP_REG_U_Ramp"] = new_value
        self.mutex.release()

    def set_M2S_M2S_SP_REG_I_Ramp(self, new_value: float):
        self.mutex.acquire()
        self.m2s.values["M2S_M2S_SP_REG_I_Ramp"] = new_value
        self.mutex.release()

    def set_M2S_M2S_SP_REG_ParSet(self, new_value: int):
        self.mutex.acquire()
        self.m2s.values["M2S_M2S_SP_REG_ParSet"] = new_value
        self.mutex.release()

    def set_M2S_M2S_SP_REG_Mode(self, new_value: int):
        self.mutex.acquire()
        self.m2s.values["M2S_M2S_SP_REG_Mode"] = new_value
        self.mutex.release()

    def set_M2S_M2S_SP_BATT_Model(self, new_value: int):
        self.mutex.acquire()
        self.m2s.values["M2S_M2S_SP_BATT_Model"] = new_value
        self.mutex.release()

    def set_M2S_M2S_RS_CW2(self, new_value: int):
        self.mutex.acquire()
        self.m2s.values["M2S_M2S_RS_CW2"] = new_value
        self.mutex.release()

    def set_M2S_M2S_SP_P(self, new_value: float):
        self.mutex.acquire()
        self.m2s.values["M2S_M2S_SP_P"] = new_value
        self.mutex.release()

    def set_M2S_M2S_SP_BATT_C2(self, new_value: float):
        self.mutex.acquire()
        self.m2s.values["M2S_M2S_SP_BATT_C2"] = new_value
        self.mutex.release()

    def set_M2S_M2S_SP_BATT_L1(self, new_value: float):
        self.mutex.acquire()
        self.m2s.values["M2S_M2S_SP_BATT_L1"] = new_value
        self.mutex.release()

    def set_M2S_M2S_SP_BATT_U0_B(self, new_value: float):
        self.mutex.acquire()
        self.m2s.values["M2S_M2S_SP_BATT_U0_B"] = new_value
        self.mutex.release()

    def set_M2S_M2S_SP_RPL_LF_Mode(self, new_value: int):
        self.mutex.acquire()
        self.m2s.values["M2S_M2S_SP_RPL_LF_Mode"] = new_value
        self.mutex.release()

    def set_M2S_M2S_SP_RPL_MF_Mode(self, new_value: int):
        self.mutex.acquire()
        self.m2s.values["M2S_M2S_SP_RPL_MF_Mode"] = new_value
        self.mutex.release()

    def set_M2S_M2S_SP_RPL_LF_Hz(self, new_value: float):
        self.mutex.acquire()
        self.m2s.values["M2S_M2S_SP_RPL_LF_Hz"] = new_value
        self.mutex.release()

    def set_M2S_M2S_SP_RPL_LF_U(self, new_value: float):
        self.mutex.acquire()
        self.m2s.values["M2S_M2S_SP_RPL_LF_U"] = new_value
        self.mutex.release()

    def set_M2S_M2S_SP_RPL_MF_Hz(self, new_value: int):
        self.mutex.acquire()
        self.m2s.values["M2S_M2S_SP_RPL_MF_Hz"] = new_value
        self.mutex.release()

    def set_M2S_M2S_SP_RPL_MF_I(self, new_value: float):
        self.mutex.acquire()
        self.m2s.values["M2S_M2S_SP_RPL_MF_I"] = new_value
        self.mutex.release()

    def set_M2S_M2S_SP_RPL_MF_U(self, new_value: float):
        self.mutex.acquire()
        self.m2s.values["M2S_M2S_SP_RPL_MF_U"] = new_value
        self.mutex.release()

    def set_M2S_M2S_SP_SOC_C_Nom(self, new_value: float):
        self.mutex.acquire()
        self.m2s.values["M2S_M2S_SP_SOC_C_Nom"] = new_value
        self.mutex.release()

    def set_M2S_M2S_SP_SOC_0(self, new_value: float):
        self.mutex.acquire()
        self.m2s.values["M2S_M2S_SP_SOC_0"] = new_value
        self.mutex.release()

    def set_M2S_M2S_RS_SOC_0(self, new_value: int):
        self.mutex.acquire()
        self.m2s.values["M2S_M2S_RS_SOC_0"] = new_value
        self.mutex.release()

    def initiate_threads(self) -> None:
        thread_m2s = Thread(target=send_packet, args=())
        thread_m2s.start()
        thread_s2m = Thread(target=receive_package, args=())
        thread_s2m.start()

    def end_threads(self) -> None:
        self.stop_event.set()
        self.thread_m2s.join()
        self.thread_s2m.join()
        self.socket_MTS.close()
        self.socket_STM.close()

    def get_bit(self, number, bit_position):
        return (number << bit_position) & 1

    def catch_watchdog(self, bit_position: int):
        for i in range(30):
            self.receive_package()
            if get_bit(self.s2m.values["S2M_AS_SW2"], bit_position):
                break
            sleep(0.1)
        if get_bit(self.s2m.values["S2M_AS_SW2"], bit_position) == 0:
            raise Exception("watchdog did not come")

    def request_control(self):
        self.mutex.acquire()
        self.m2s.values["M2S_RS_CW1"] |= (1 << 3)
        self.m2s.values["M2S_RS_CW1"] |= (1 << 7)
        self.mutex.release()
        self.send_package()
        sleep(1)
        self.mutex.acquire()
        self.m2s.values["M2S_RS_CW1"] |= (1 << 2)
        self.mutex.release()
        self.send_package()
        self.catch_watchdog(3)
        self.catch_watchdog(9)
        self.catch_watchdog(0)
        self.mutex.acquire()
        self.m2s.values["M2S_RS_CW1"] |= 1
        self.mutex.release()
        self.send_package()
        self.catch_watchdog(1)
        self.mutex.acquire()
        self.m2s.values["M2S_RS_CW1"] &= ~(1 << 7)
        self.mutex.release()
        self.send_package()

    def sending_thread(self):
        while not self.stop_event.is_set():
            self.send_package()
            sleep(0.1)

    def send_package(self):
        self.socket_MTS.sendto(self.build_message(), (self.ip, self.port))

    def receiving_thread(self):
        while not self.stop_event.is_set():
            self.receive_package()
            sleep(0.1)

    def receive_package(self):
        package, sender = self.socket_STM.recvfrom(142)
        self.save_package_to_fields(package)

    def save_package_to_fields(self, package):
        for line in slave_to_master:
            message = package[line['offset']: line['offset'] + line['length']]
            if line["type"] == 'Real':
                result = decode_float(message)
            if line["type"] == 'UINT':
                result = decode_unsigned_int(message)
            if line["type"] == 'SINT':
                result = decode_signed_int(message)
            self.mutex.acquire()
            self.s2m.values[line["name"]] = result
            self.mutex.release()

    def decode_signed_int(self, message: bytearray) -> int:
        if (len(message) == 4):
            return struct.unpack('i', message)[0]
        return struct.unpack('h', message)[0]

    def decode_unsigned_int(self, message: bytearray) -> int:
        if (len(message) == 4):
            return struct.unpack('I', message)[0]
        return struct.unpack('H', message)[0]

    def decode_float(self, message: bytearray) -> float:
        return struct.unpack('f', message)[0]

    def build_message(self) -> bytearray:
        result = bytearray()
        for line in self.m2s.master_to_slave:
            if line["type"] == "UINT":
                encoded = self.encode_unsigned_int(
                    self.m2s.values[line['name']], line["length"])
            elif line["type"] == "SINT":
                encoded = self.encode_signed_int(
                    self.m2s.values[line['name']], line["length"])
            elif line["type"] == "Real":
                encoded = self.encode_float(self.m2s.values[line['name']])
            result.extend(encoded)
        return result

    def encode_signed_int(self, message: int, length: int) -> bytearray:
        if length == 4:
            return struct.pack('i', message)
        if length == 2:
            return struct.pack('h', message)

    def encode_unsigned_int(self, message: int, length: int) -> bytearray:
        if length == 4:
            return struct.pack('I', message)
        if length == 2:
            return struct.pack('H', message)

    def encode_float(self, message: float) -> bytearray:
        return struct.pack('f', message)

    def activate_VES(self) -> None:
        self.set_M2S_RS_ACTIVE(1)

    def deactivate_VES(self) -> None:
        self.set_M2S_RS_ACTIVE(-1)

    def turn_off_VCU(self) -> None:
        pass
