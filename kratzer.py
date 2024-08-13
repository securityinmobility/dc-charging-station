import socket
import struct


class kratzer:
    fields = [
        { "name": "S2M_AS_SW1",         "offset": 0, "length": 2, "type": "UNIT" },
        { "name": "S2M_AS_SW2",         "offset": 2, "length": 2, "type": "UNIT" },
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
        { "name": "S2M_AS_REG_ParSet_Err", "offset": 102, "length": 2, "type": "UNIT" },
        { "name": "S2M_AV_REG_Mode",    "offset": 104, "length": 2, "type": "UNIT" },
        { "name": "S2M_AS_BATT_Model",  "offset": 106, "length": 2, "type": "SINT" },
        { "name": "S2M_AS_ZR_Error_a",  "offset": 108, "length": 2, "type": "UNIT" },
        { "name": "S2M_AS_ZR_Error_b",  "offset": 110, "length": 2, "type": "UNIT" },
        { "name": "S2M_AS_UWR_Error_a", "offset": 112, "length": 2, "type": "UNIT" },
        { "name": "S2M_AS_UWR_error_b", "offset": 114, "length": 2, "type": "UNIT" },
        { "name": "S2M_AS_RK_Error_a",  "offset": 116, "length": 2, "type": "UNIT" },
        { "name": "S2M_AS_RK_Error_b",  "offset": 118, "length": 2, "type": "UNIT" },
        { "name": "S2M_AS_TSB_Error_a", "offset": 120, "length": 2, "type": "UNIT" },
        { "name": "S2M_AS_TSB_Error_b", "offset": 122, "length": 2, "type": "UNIT" },
        { "name": "S2M_AS_BATT_C2",     "offset": 124, "length": 4, "type": "Real" },
        { "name": "S2M_AS_BATT_L1",     "offset": 128, "length": 4, "type": "Real" },
        { "name": "S2M_AV_BATT_U0_B",   "offset": 132, "length": 4, "type": "Real" },
        { "name": "S2M_AS_TSB_Error_c", "offset": 136, "length": 2, "type": "UNIT" },
        { "name": "S2M_AV_BATT_SOC",    "offset": 138, "length": 4, "type": "Real" }]

    dictionary = [
        { "name": "M2S_RS_CW1", "offset": 0, "length": 2, "type": "UNIT" },
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
        {"offset": 66, "name": "M2S_SP_REG_KP_I",    "length": 4, "type": "Real"},
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

    #    packet = receiveUdpSomehow()
    #    result = {}
    #    for field in fields:
    #        if field["type"] == "Real":
    #          result[field["name"]] = # ... somehow decode real 

    # print("received message: %s" % data)

    def __init__(self, IP:str, port:str):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((IP, port))
        self.mutex = Lock()


    def send_package(self, message):
        pass


    def receive_package(self):
        pass


