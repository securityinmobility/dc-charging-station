import socket
import struct


class kratzer:
    slave_to_master = [
        { "name": "S2M_AS_SW1",         "offset": 0, "length": 2, "type": "UINT" },
        { "name": "S2M_AS_SW2",         "offset": 2, "length": 2, "type": "UINT" },
        { "name": "S2M_AV_U",           "offset": 4, "length": 4, "type": "Real" },
        { "name": "S2M_AV_I",           "offset": 8, "length": 4, "type": "Real" },
        { "name": "S2M_AV_P",           "offset": 12, "length": 4, "type": "Real" },
        { "name": "S2M_SPV_Umin",       "offset": 16, "length": 4, "type": "Real" },
        { "name": "S2M_SPV_Umax",       "offset": 20, "length": 4, "type": "Real" },
        { "name": "S2M_SPV_LIMIT_Umin", "offset": 24, "length": 4, "type": "Real" },
        { "name": "S2M_SPV_LIMIT_Umax", "offset": 28, "length": 4, "type": "Real" },
        { "name": "S2M_SPV_LIMIT_Imin", "offset": 32, "length": 4, "type": "Real" },
        { "name": "S2M_SPV_LIMIT_Imax", "offset": 36, "length": 4, "type": "Real" },
        { "name": "S2M_AS_BATT_R1",     "offset": 40, "length": 4, "type": "Real" },
        { "name": "VS2M_AS_BATT_R2",    "offset": 44, "length": 4, "type": "Real" },
        { "name": "S2M_AS_BATT_R3",     "offset": 48, "length": 4, "type": "Real" },
        { "name": "S2M_AS_BATT_R4",     "offset": 52, "length": 4, "type": "Real" },
        { "name": "S2M_AS_BATT_C1",     "offset": 56, "length": 4, "type": "Real" },
        { "name": "S2M_AV_BATT_I_filter", "offset": 60, "length": 4, "type": "Real"},
        { "name": "S2M_AV_BATT_U0_A",   "offset": 64, "length": 4, "type": "Real" },
        { "name": "S2M_AV_REG_KP_I",    "offset": 68, "length": 4, "type": "Real" },
        { "name": "S2M_AV_REG_TN_I",    "offset": 72, "length": 4, "type": "Real" },
        { "name": "S2M_AV_REG_KP_U",    "offset": 76, "length": 4, "type": "Real" },
        { "name": "S2M_AV_REG_TN_U",    "offset": 80, "length": 4, "type": "Real" },
        { "name": "S2M_AV_REG_KP_M",    "offset": 84, "length": 4, "type": "Real" },
        { "name": "S2M_AV_REG_TN_M",    "offset": 88, "length": 4, "type": "Real" },
        { "name": "S2M_AV_REG_U_ramp",  "offset": 92, "length": 4, "type": "Real" },
        { "name": "S2M_AV_REG_I_ramp",  "offset": 96, "length": 4, "type": "Real" },
        { "name": "S2M_AS_REG_ParSet",  "offset": 100, "length": 2, "type": "SINT" },
        { "name": "S2M_AS_REG_ParSet_Err", "offset": 102, "length": 2, "type": "UINT" },
        { "name": "S2M_AV_REG_Mode",    "offset": 104, "length": 2, "type": "UINT" },
        { "name": "S2M_AS_BATT_Model",  "offset": 106, "length": 2, "type": "SINT" },
        { "name": "S2M_AS_ZR_Error_a",  "offset": 108, "length": 2, "type": "UINT" },
        { "name": "S2M_AS_ZR_Error_b",  "offset": 110, "length": 2, "type": "UINT" },
        { "name": "S2M_AS_UWR_Error_a", "offset": 112, "length": 2, "type": "UINT" },
        { "name": "S2M_AS_UWR_error_b", "offset": 114, "length": 2, "type": "UINT" },
        { "name": "S2M_AS_RK_Error_a",  "offset": 116, "length": 2, "type": "UINT" },
        { "name": "S2M_AS_RK_Error_b",  "offset": 118, "length": 2, "type": "UINT" },
        { "name": "S2M_AS_TSB_Error_a", "offset": 120, "length": 2, "type": "UINT" },
        { "name": "S2M_AS_TSB_Error_b", "offset": 122, "length": 2, "type": "UINT" },
        { "name": "S2M_AS_BATT_C2",     "offset": 124, "length": 4, "type": "Real" },
        { "name": "S2M_AS_BATT_L1",     "offset": 128, "length": 4, "type": "Real" },
        { "name": "S2M_AV_BATT_U0_B",   "offset": 132, "length": 4, "type": "Real" },
        { "name": "S2M_AS_TSB_Error_c", "offset": 136, "length": 2, "type": "UINT" },
        { "name": "S2M_AV_BATT_SOC",    "offset": 138, "length": 4, "type": "Real" }]

    master_to_slave = [
        { "name": "M2S_RS_CW1", "offset": 0, "length": 2, "type": "UINT" },
        { "name": "M2S_SP_U",   "offset": 2, "length": 4, "type": "Real" },
        {"offset": 6,  "name": "M2S_SP_Imin",        "length": 4, "type": "Real"},
        {"offset": 10, "name": "M2S_SP_Imax",        "length": 4, "type": "Real"},
        {"offset": 14, "name": "M2S_SP_Umin",        "length": 4, "type": "Real"},
        {"offset": 18, "name": "M2S_SP_Umax",        "length": 4, "type": "Real"},
        {"offset": 22, "name": "M2S_SP_LIMIT_Umin",  "length": 4, "type": "Real"},
        {"offset": 26, "name": "M2S_SP_LIMIT_Umax",  "length": 4, "type": "Real"},
        {"offset": 30, "name": "M2S_SP_LIMIT_Imin",  "length": 4, "type": "Real"},
        {"offset": 34, "name": "M2S_SP_LIMIT_Imax",  "length": 4, "type": "Real"},
        {"offset": 38, "name": "M2S_SP_BATT_R1",     "length": 4, "type": "Real"},
        {"offset": 42, "name": "M2S_SP_BATT_R2",     "length": 4, "type": "Real"},
        {"offset": 46, "name": "M2S_SP_BATT_R3",     "length": 4, "type": "Real"},
        {"offset": 50, "name": "M2S_SP_BATT_R4",     "length": 4, "type": "Real"},
        {"offset": 54, "name": "M2S_SP_BATT_C1",     "length": 4, "type": "Real"},
        {"offset": 58, "name": "M2S_SP_REG_I_Filter","length": 4, "type": "Real"},
        {"offset": 62, "name": "M2S_SP_REG_U0_A",    "length": 4, "type": "Real"},
        {"offset": 66, "nam:e": "M2S_SP_REG_KP_I",    "length": 4, "type": "Real"},
        {"offset": 70, "name": "M2S_SP_REG_TN_I",    "length": 4, "type": "Real"},
        {"offset": 74, "name": "M2S_SP_REG_KP_U",    "length": 4, "type": "Real"},
        {"offset": 78, "name": "M2S_SP_REG_TN_U",    "length": 4, "type": "Real"},
        {"offset": 82, "name": "M2S_SP_REG_KP_M",   "length": 4, "type": "Real"},
        {"offset": 86, "name": "M2S_SP_REG_TN_M",   "length": 4, "type": "Real"},
        {"offset": 90, "name": "M2S_SP_REG_U_Ramp", "length": 4, "type": "Real"},
        {"offset": 94, "name": "M2S_SP_REG_I_Ramp", "length": 4, "type": "Real"},
        {"offset": 98, "name": "M2S_SP_REG_ParSet", "length": 2, "type": "UINT"},
        {"offset": 100,"name": "M2S_SP_REG_Mode",   "length": 2, "type": "UINT"}
        {"offset": 102,"name": "M2S_SP_BATT_Model", "length": 2, "type": "UINT"}
        {"offset": 104,"name": "M2S_RS_CW2",        "length": 2, "type": "UINT"}
        {"offset": 106,"name": "M2S_SP_P",          "length": 4, "type": "UINT"}
        {"offset": 110,"name": "M2S_SP_BATT_C2",    "length": 4, "type": "UINT"}
        {"offset": 114,"name": "M2S_SP_BATT_L1",    "length": 4, "type": "UINT"}
        {"offset": 118,"name": "M2S_SP_BATT_U0_B",  "length": 4, "type": "UINT"}
        {"offset": 122,"name": "M2S_SP_RPL_LF_Mode","length": 2, "type": "UINT"}
        {"offset": 124,"name": "M2S_SP_RPL_MF_Mode","length": 2, "type": "UINT"}
        {"offset": 126,"name": "M2S_SP_RPL_LF_Hz",  "length": 4, "type": "UINT"}
        {"offset": 130,"name": "M2S_SP_RPL_LF_U",   "length": 4, "type": "UINT"}
        {"offset": 134,"name": "M2S_SP_RPL_MF_Hz",  "length": 2, "type": "UINT"}
        {"offset": 136,"name": "M2S_SP_RPL_MF_I",   "length": 4, "type": "UINT"}
        {"offset": 140,"name": "M2S_SP_RPL_MF_U",   "length": 4, "type": "UINT"}
        {"offset": 144,"name": "M2S_SP_SOC_C_Nom",  "length": 4, "type": "UINT"}
        {"offset": 148,"name": "M2S_SP_SOC_0",      "length": 4, "type": "UINT"}
        {"offset": 152,"name": "M2S_RS_SOC_0",      "length": 2, "type": "UINT"}
        ]

    def __init__(self, IP:str, port:str):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((IP, port))
        self.mutex = Lock()

    def set_M2S_RS_CW1(self, new_value:int):
        self.M2S_RS_CW1 = new_value

    def set_M2S_M2S_SP_U(self, new_value:float):
        self.M2S_M2S_SP_U = new_value

    def set_M2S_M2S_SP_Imin(self, new_value:float):
        self.M2S_M2S_SP_Imin = new_value

    def set_M2S_M2S_SP_Imax(self, new_value:float):
        self.M2S_M2S_SP_Imax = new_value

    def set_M2S_M2S_SP_Umin(self, new_value:float):
        self.M2S_M2S_SP_Umin = new_value

    def set_M2S_M2S_SP_Umax (self, new_value:float):
        self.M2S_M2S_SP_Umax = new_value

    def set_M2S_M2S_SP_LIMIT_Umin(self, new_value:float):
        self.M2S_M2S_SP_LIMIT_Umin = new_value

    def set_M2S_M2S_SP_LIMIT_Umax(self, new_value:float):
        self.M2S_M2S_SP_LIMIT_Umax = new_value

    def set_M2S_M2S_SP_LIMIT_Imin(self, new_value:float):
        self.M2S_M2S_SP_LIMIT_Imin = new_value

    def set_M2S_M2S_SP_LIMIT_Imax(self, new_value:float):
        self.M2S_M2S_SP_LIMIT_Imax = new_value

    def set_M2S_M2S_SP_BATT_R1(self, new_value:float):
        self.M2S_M2S_SP_BATT_R1 = new_value

    def set_M2S_M2S_SP_BATT_R2(self, new_value:float):
        self.M2S_M2S_SP_BATT_R2 = new_value

    def set_M2S_M2S_SP_BATT_R3(self, new_value:float):
        self.M2S_M2S_SP_BATT_R3 = new_value

    def set_M2S_M2S_SP_BATT_R4(self, new_value:float):
        self.M2S_M2S_SP_BATT_R4 = new_value

    def set_M2S_M2S_SP_BATT_C1(self, new_value:float):
        self.M2S_M2S_SP_BATT_C1 = new_value

    def set_M2S_M2S_SP_REG_I_Filter(self, new_value:float):
        self.M2S_M2S_SP_REG_I_Filter = new_value

    def set_M2S_M2S_SP_REG_U0_A(self, new_value:float):
        self.M2S_M2S_SP_REG_U0_A = new_value

    def set_M2S_M2S_SP_REG_KP_I(self, new_value:float):
        self.M2S_M2S_SP_REG_KP_I = new_value

    def set_M2S_M2S_SP_REG_TN_I(self, new_value:float):
        self.M2S_M2S_SP_REG_TN_I = new_value

    def set_M2S_M2S_SP_REG_KP_U(self, new_value:float):
        self.M2S_M2S_SP_REG_KP_U = new_value

    def set_M2S_M2S_SP_REG_TN_U(self, new_value:float):
        self.M2S_M2S_SP_REG_TN_U = new_value

    def set_M2S_M2S_SP_REG_KP_M(self, new_value:float):
        self.M2S_M2S_SP_REG_KP_M = new_value

    def set_M2S_M2S_SP_REG_TN_M(self, new_value:float):
        self.M2S_M2S_SP_REG_TN_M = new_value

    def set_M2S_M2S_SP_REG_U_Ramp(self, new_value:float):
        self.M2S_M2S_SP_REG_U_Ramp = new_value

    def set_M2S_M2S_SP_REG_I_Ramp(self, new_value:float):
        self.M2S_M2S_SP_REG_I_Ramp = new_value

    def set_M2S_M2S_SP_REG_ParSet(self, new_value:int):
        self.M2S_M2S_SP_REG_ParSet = new_value

    def set_M2S_M2S_SP_REG_Mode(self, new_value:int):
        self.M2S_M2S_SP_REG_Mode = new_value

    def set_M2S_M2S_SP_BATT_Model(self, new_value:int):
        self.M2S_M2S_SP_BATT_Model = new_value

    def set_M2S_M2S_RS_CW2(self, new_value:int):
        self.M2S_M2S_RS_CW2 = new_value

    def set_M2S_M2S_SP_P(self, new_value:float):
        self.M2S_M2S_SP_P = new_value

    def set_M2S_M2S_SP_BATT_C2(self, new_value:float):
        self.M2S_M2S_SP_BATT_C2 = new_value

    def set_M2S_M2S_SP_BATT_L1(self, new_value:float):
        self.M2S_M2S_SP_BATT_L1 = new_value

    def set_M2S_M2S_SP_BATT_U0_B(self, new_value:float):
        self.M2S_M2S_SP_BATT_U0_B = new_value

    def set_M2S_M2S_SP_RPL_LF_Mode(self, new_value:int):
        self.M2S_M2S_SP_RPL_LF_Mode = new_value

    def set_M2S_M2S_SP_RPL_MF_Mode(self, new_value:int):
        self.M2S_M2S_SP_RPL_MF_Mode = new_value

    def set_M2S_M2S_SP_RPL_LF_Hz(self, new_value:float):
        self.M2S_M2S_SP_RPL_LF_Hz = new_value

    def set_M2S_M2S_SP_RPL_LF_U(self, new_value:float):
        self.M2S_M2S_SP_RPL_LF_U = new_value

    def set_M2S_M2S_SP_RPL_MF_Hz(self, new_value:int):
        self.M2S_M2S_SP_RPL_MF_Hz = new_value

    def set_M2S_M2S_SP_RPL_MF_I(self, new_value:float):
        self.M2S_M2S_SP_RPL_MF_I = new_value

    def set_M2S_M2S_SP_RPL_MF_U(self, new_value:float):
        self.M2S_M2S_SP_RPL_MF_U = new_value

    def set_M2S_M2S_SP_SOC_C_Nom(self, new_value:float):
        self.M2S_M2S_SP_SOC_C_Nom = new_value

    def set_M2S_M2S_SP_SOC_0(self, new_value:float):
        self.M2S_M2S_SP_SOC_0 = new_value

    def set_M2S_M2S_RS_SOC_0(self, new_value:int):
        self.M2S_M2S_RS_SOC_0 = new_value

    def send_package(self, message):


    def receive_package(self):
        message, sender = self.socket.recvfrom(142)


    def decode( message:bytearray, code:str ) -> list:
        result = {}
        for field in self.slave_to_master:
            if field["type"] == "Real":
                decode_real(message[field["offset"] : field["offset"] + field["length"]])
            if field["type"] == "UINT":
                decode_uint(message[field["offset"] : field["offset"] + field["length"]])
            if field["type"] == "SINT":
                decode_sint(message[field["offset"] : field["offset"] + field["length"]])
         print("received message: %s" % data)


    def decode_sint( message:bytearray ) -> int:
        # Assuming 16-bit signed integer
        return struct.unpack('<h', byte_array)[0]


    def decode_uint( message:bytearray ) -> int:
        # Assuming 16-bit unsigned integer
        return struct.unpack('<H', byte_array)[0]


    def decode_real( message:bytearray ) -> float:
        # Assuming 32-bit float
        return struct.unpack('<f', byte_array)[0]



