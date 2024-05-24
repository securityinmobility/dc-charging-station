# Kratzer Interface

This document describes the interface of the Kratze High-Power Battery Tester that acts as DC power supply in the configurable charging station.

The battery tester is mounted across several rooms in the CARISSMA and has two outlets in H010 (climate chamber) and in H007. The second outlet is extended to be available near the lifting platform / the later test bench.

## Abbreviations

Abbreviations used in the Kratzer documentation and this document are described here.

|Abbreviation|Long Form|Description
|---|---|---|
|VES|Vehicle Energy System|Power part of the test bench|
|VCU|VES Control Unit|PFR and Control Computer?|
|PFR|Process control computer *(Prozessführungsrechner)*| PC controlling the VES


## Target description

The Kratzer test bench is a powerful equipment with many functions to test or simulate batteries. In our use-case, we simply want a controllable power supply. As this test bench is able to provide 800V / 500A / 150kW, this is perfectly suitable for a charging station.

As we use a vehicle connector without active cooling, we have to limit the current to 250A. This reduces the "usual" charging power with standard 400V-based vehicles to about 100kW.

The vehicle will talk to a specific charging controller board over a ISO15118 connection. This board has to extract the necessary charging parameters, like requested current and voltage limit and has to provide them to the Kratzer test bench. The test bench then provides the requested power to charge the vehicle.

The connection between the charging control board and the Kratzer test bench is focus of this document.

## Hardware Overview

The test bench consists of the VES, the VCU, two NRG-Boxes (to connect test devices), and two Bus-Boxes (to connect communication lines).
How the connection will be established in detail is not yet known. Three different typed seem possible: CAN, EtherCAT and Ethernet. Ethernet will be the preferred way and, as far as the documentation is correct, this is possible. Therefore, the charge controller would be able to directly control the power supply by simply sending UDP packets.


## UDP Interface

The UDP connection uses two ports:

Slave -> Master on Port 5000
Master -> Slave on Port 5100

The documentation states an Intel format (supposed to be little endian).

Based on the circuit diagram, the charge controller shall have the IP 192.168.1.100
The PFR has 192.168.1.100 -> cannot be correct.
The PC has 192.168.1.102

### Data Structure

In general, the signals have the following meaning:

|Abbreviation|Meaning|
|---|---|
|SP|Setpoint|
|AS|Current state *(aktueller Status)*|
|RS|Requested state|
|AV|actual value|
|SPC|current setpoint value|

#### Communication Slave to Master

| No. | Name                  | Offset | Size | Type | Dimension | Scale | Usage |
|-----|-----------------------|--------|------|------|-----------|-------|-------|
| 1   | S2M_AS_SW1            | 0      | 2    | UINT |           | 1k    |
| 2   | S2M_AS_SW2            | 2      | 2    | UINT |           | 1k    |
| 3   | S2M_AV_U              | 4      | 4    | Real | V         | 1k    |
| 4   | S2M_AV_I              | 8      | 4    | Real | A         | 1k    |
| 5   | S2M_AV_P              | 12     | 4    | Real | kW        | 10    |
| 6   | S2M_SPV_Umin          | 16     | 4    | Real | V         | 10    |
| 7   | S2M_SPV_Umax          | 20     | 4    | Real | V         | 10    |
| 8   | S2M_SPV_LIMIT_Umin    | 24     | 4    | Real | V         | 10    |
| 9   | S2M_SPV_LIMIT_Umax    | 28     | 4    | Real | V         | 10    |
| 10  | S2M_SPV_LIMIT_Imin    | 32     | 4    | Real | A         | 10    |
| 11  | S2M_SPV_LIMIT_Imax    | 36     | 4    | Real | A         | 10    |
| 12  | S2M_AS_BATT_R1        | 40     | 4    | Real | Ohm       | 10    |
| 13  | VS2M_AS_BATT_R2       | 44     | 4    | Real | Ohm       | 10    |
| 14  | S2M_AS_BATT_R3        | 48     | 4    | Real | Ohm       | 10    |
| 15  | S2M_AS_BATT_R4        | 52     | 4    | Real | Ohm       | 10    |
| 16  | S2M_AS_BATT_C1        | 56     | 4    | Real | F         | 10    |
| 17  | S2M_AV_BATT_I_filter  | 60     | 4    | Real | ms        | 10    |
| 18  | S2M_AV_BATT_U0_A      | 64     | 4    | Real | V         | 10    |
| 19  | S2M_AV_REG_KP_I       | 68     | 4    | Real |           | 10    |
| 20  | S2M_AV_REG_TN_I       | 72     | 4    | Real |           | 10    |
| 21  | S2M_AV_REG_KP_U       | 76     | 4    | Real |           | 10    |
| 22  | S2M_AV_REG_TN_U       | 80     | 4    | Real |           | 10    |
| 23  | S2M_AV_REG_KP_M       | 84     | 4    | Real |           | 10    |
| 24  | S2M_AV_REG_TN_M       | 88     | 4    | Real |           | 10    |
| 25  | S2M_AV_REG_U_ramp     | 92     | 4    | Real | FS/ms     | 10    |
| 26  | S2M_AV_REG_I_ramp     | 96     | 4    | Real | FS/ms     | 10    |
| 27  | S2M_AS_REG_ParSet     | 100    | 2    | SINT |           | 10    |
| 28  | S2M_AS_REG_ParSet_Err | 102    | 2    | UINT |           | 10    |
| 29  | S2M_AV_REG_Mode       | 104    | 2    | UINT |           | 10    |
| 30  | S2M_AS_BATT_Model     | 106    | 2    | SINT |           | 10    |
| 31  | S2M_AS_ZR_Error_a     | 108    | 2    | UINT |           | 10    |
| 32  | S2M_AS_ZR_Error_b     | 110    | 2    | UINT |           | 10    |
| 33  | S2M_AS_UWR_Error_a    | 112    | 2    | UINT |           | 10    |
| 34  | S2M_AS_UWR_error_b    | 114    | 2    | UINT |           | 10    |
| 35  | S2M_AS_RK_Error_a     | 116    | 2    | UINT |           | 10    |
| 36  | S2M_AS_RK_Error_b     | 118    | 2    | UINT |           | 10    |
| 37  | S2M_AS_TSB_Error_a    | 120    | 2    | UINT |           | 10    |
| 38  | S2M_AS_TSB_Error_b    | 122    | 2    | UINT |           | 10    |
| 39  | S2M_AS_BATT_C2        | 124    | 4    | Real | F         | 10    |
| 40  | S2M_AS_BATT_L1        | 128    | 4    | Real | H         | 10    |
| 41  | S2M_AV_BATT_U0_B      | 132    | 4    | Real | V         | 10    |
| 42  | S2M_AS_TSB_Error_c    | 136    | 2    | UINT |           | 10    |
| 43  | S2M_AV_BATT_SOC       | 138    | 4    | Real |           | 10    |

These are all signals that are sent from Master to Slave (VCU to Charge Controller, S2M).

#### Communication Master to Slave

| No. | Name                  | Offset | Size | Type | Dimension    | Scale |
|-----|-----------------------|--------|------|------|--------------|-------|
| 1   | M2S_RS_CW1            | 0      | 2    | UINT |              | 1k    |
| 2   | M2S_SP_U              | 2      | 4    | Real | V            | 1k    |
| 3   | M2S_SP_Imin           | 6      | 4    | Real | A            | 1k    |
| 4   | M2S_SP_Imax           | 10     | 4    | Real | kW           | 1k    |
| 5   | M2S_SP_Umin           | 14     | 4    | Real | V            | 1k    |
| 6   | M2S_SP_Umax           | 18     | 4    | Real | V            | 1k    |
| 7   | M2S_SP_LIMIT_Umin     | 22     | 4    | Real | V            | 10    |
| 8   | M2S_SP_LIMIT_Umax     | 26     | 4    | Real | V            | 10    |
| 9   | M2S_SP_LIMIT_Imin     | 30     | 4    | Real | A            | 10    |
| 10  | M2S_SP_LIMIT_Imax     | 34     | 4    | Real | A            | 10    |
| 11  | M2S_SP_BATT_R1        | 38     | 4    | Real | Ohm          | 10    |
| 12  | M2S_SP_BATT_R2        | 42     | 4    | Real | Ohm          | 10    |
| 13  | M2S_SP_BATT_R3        | 46     | 4    | Real | Ohm          | 10    |
| 14  | M2S_SP_BATT_R4        | 50     | 4    | Real | Ohm          | 10    |
| 15  | M2S_SP_BATT_C1        | 54     | 4    | Real | F            | 10    |
| 16  | M2S_SP_REG_I_Filter   | 58     | 4    | Real | ms           | 10    |
| 17  | M2S_SP_REG_U0_A       | 62     | 4    | Real | V            | 10    |
| 18  | M2S_SP_REG_KP_I       | 66     | 4    | Real |              | 10    |
| 19  | M2S_SP_REG_TN_I       | 70     | 4    | Real |              | 10    |
| 20  | M2S_SP_REG_KP_U       | 74     | 4    | Real |              | 10    |
| 21  | M2S_SP_REG_TN_U       | 78     | 4    | Real |              | 10    |
| 22  | M2S_SP_REG_KP_M       | 82     | 4    | Real |              | 10    |
| 23  | M2S_SP_REG_TN_M       | 86     | 4    | Real |              | 10    |
| 24  | M2S_SP_REG_U_Ramp     | 90     | 4    | Real | FS/ms        | 10    |
| 25  | M2S_SP_REG_I_Ramp     | 94     | 4    | Real | FS/ms        | 10    |
| 26  | M2S_SP_REG_ParSet     | 98     | 2    | UINT |              | 10    |
| 27  | M2S_SP_REG_Mode       | 100    | 2    | UINT |              | 10    |
| 28  | M2S_SP_BATT_Model     | 102    | 2    | UINT |              | 10    |
| 29  | M2S_RS_CW2            | 104    | 2    | UINT |              | 1k    |
| 30  | M2S_SP_P              | 106    | 4    | Real | kW           | 1k    |
| 31  | M2S_SP_BATT_C2        | 110    | 4    | Real | F            | 10    |
| 32  | M2S_SP_BATT_L1        | 114    | 4    | Real | H            | 10    |
| 33  | M2S_SP_BATT_U0_B      | 118    | 4    | Real | A, V         | 10    |
| 34  | M2S_SP_RPL_LF_Mode    | 122    | 2    | UINT |              | 10    |
| 35  | M2S_SP_RPL_MF_Mode    | 124    | 2    | UINT |              | 10    |
| 36  | M2S_SP_RPL_LF_Hz      | 126    | 4    | Real | Hz           | 10    |
| 37  | M2S_SP_RPL_LF_U       | 130    | 4    | Real | V, A         | 10    |
| 38  | M2S_SP_RPL_MF_Hz      | 134    | 2    | UINT | Hz           | 10    |
| 39  | M2S_SP_RPL_MF_I       | 136    | 4    | Real | A            | 10    |
| 40  | M2S_SP_RPL_MF_U       | 140    | 4    | Real | V            | 10    |
| 41  | M2S_SP_SOC_C_Nom      | 144    | 4    | Real | Ah           | 10    |
| 42  | M2S_SP_SOC_0          | 148    | 4    | Real | %            | 10    |
| 43  | M2S_RS_SOC_0          | 152    | 2    | UINT |              | 10    |

## Operation Mode

The overall mode will be battery simulation *(Fahrsimulator)*. This has to be set in the main control panel's toggle switch.

The used mode will probably be 4 (current regulation) or 6 (current regulation for battery tests). In these modes, the current is set and additionally a maximum (and minimum) voltage can be configured.

Mode 4 has the disadvantage, that a quadrant change is possible if the maximum voltage is reaches (vehicle would get discharged again). In mode 6, this is not possible (although discharging is possible with a negative current setpoint) except for a very small discharge current, that can occur (up to 0.2% of the current setpoint).

As battery model, the model 0 will be used as here the setpoint values are used directly (without applying a certain battery model with resistors, capacities and inductivities).

## VCUS

P. 19: Setpoints for current, voltage, power

## VES3

I don't think the VES3 is relevant for us. It seems to be the main system, and is therefore connected via EtherCAT (between the control PC and the QNX-based controller, "Bedienrechner" vs. "Prozeddführungsrechner").