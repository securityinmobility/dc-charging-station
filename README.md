# dc-charging-station

![](Documentation/id3-charging-demo.jpg)

This repository contains glue code in order to create a fully working DC charging station.

In our case we use ~~[open-plc-utils](https://github.com/qca/open-plc-utils)~~ [EcoG-io/pyslac](https://github.com/EcoG-io/pyslac) for SLAC, [EcoG-io/iso15118](https://github.com/EcoG-io/iso15118) for the ISO15118 stack, an [EVAcharge SE](https://chargebyte.com/controllers-and-modules/evse-controllers/evacharge-se) for powerline communication and a ~~[Kratzer Automation battery tester](https://www.ni.com/de/shop/power-electronics-test-systems.html)~~ [EA-PSB 11000-10](https://elektroautomatik.com/shop/en/products/programmable-dc-laboratory-power-supplies/bidirectional-dc-laboratory-power-supplies/series-psb-10000-2u-1-5-3kw/1147/bi-directional-power-supply) as a bidirectional HV power supply.

## Components

The idea of this repository is to have hardware abstraction interfaces which can be implemented for different hardware.
All of these interfaces (python abstract base classes) are defined in the `base_classes.py` file.

For implementing a charging station you need to implement the `ChargingStation` class as well as the `HighVoltageSource` class.
You can then give them as parameters to the ISO15118 EVSE controller based on [EcoG-io/iso15118](https://github.com/EcoG-io/iso15118).
This controller will handle vehicle detection, iso15118 communication and high voltage source parameter setting.

## Running

First connect your PC via ethernet to both the EVAcharge and the EA-PSB.
In our setup both have static IP addresses configured in a /24 network.
`192.168.188.100` for the EA-PSB and `192.168.188.250` for the evacharge.

Connect to the evacharge via ssh, flash the modem and run socat for forwarding the low level controls.

```bash
# ./flash-qca-temporarily.sh
# socat tcp-l:2020,reuseaddr,fork,crlf file:/dev/ttyAPP2,echo=0,b57600,raw
```

In a second terminal start the actual charging station code:
```bash
$ python -m venv venv
$ . venv/bin/activate
$ pip install -r requirements.txt
$ NETWORK_INTERFACE=enx7cc2c61f051e FREE_CHARGING_SERVICE=True LOG_LEVEL=INFO python3 secc-main.py
```

After plugging in the vehicle the charging process should start automatically.

## Environment Variables

### **dc-charging-station**

These variables control the main application logic and the selection of hardware interface implementations.

| ENV | Default Value | Description |
|---|---|---|
| `LOG_LEVEL` | `INFO` | The logging level for the Python log service. Applies to the entire application. |
| `NETWORK_INTERFACE` | `eth0` | The network interface name (e.g., `enx7cc2c61f051e`) used for the communication. |
| `HIGH_VOLTAGE_CONTROLLER_IMPL` | `mock` | Specifies which implementation of the `HighVoltageSource` abstract base class to use. |
| `DIN_61851_IMPL` | `mock` | Specifies which implementation to use for the basic PWM signaling according to IEC 61851-1. |
| `FREE_CHARGING_SERVICE` | `False` | If set to `True`, the charging service is provided without requiring authorization. |

### **pyslac (SLAC Protocol)**

These variables are used to configure the SLAC (Signal Level Attenuation Characterization) process, which is managed by a `pyslac` adaptation.

| ENV | Default Value | Description |
|---|---|---|
| `SLAC_INIT_TIMEOUT` | `50` | Timeout in seconds for the reception of the first SLAC message after Control Pilot state B is detected. |
| `ATTEN_RESULTS_TIMEOUT` | `None` | Timeout in milliseconds for the reception of all MNBC (Mid-Network Beaconing and Communication) sounds. If not set, the system uses the timeout defined by the EV. |
| `EVSE_ID` | `DE*THI*H007000000` | The unique identifier of the charging point. |
| `NID` | `None` | The 56-bit Network Identifier (NID) for the SLAC protocol, used to identify the logical network. |
| `NMK` | `None` | The 128-bit Network Membership Key (NMK) for the SLAC protocol, used to secure the communication on the logical network. |

### **SECC (ISO 15118 Communication)**

These variables configure the SECC (Supply Equipment Communication Controller) and the high-level communication based on the ISO 15118 standard.

| ENV | Default Value | Description |
|---|---|---|
| `SECC_ENFORCE_TLS` | `False` | If set to `True`, the SECC will enforce a TLS-secured connection for all communication. |
| `PKI_PATH` | `<CWD>/iso15118/shared/pki/` | Path to the Public Key Infrastructure (PKI) directory containing the necessary certificates. |
| `MESSAGE_LOG_JSON` | `True` | Set to `True` to log the EXI messages as JSON. This requires the `LOG_LEVEL` to be set to `DEBUG`. |
| `MESSAGE_LOG_EXI` | `False` | Set to `True` to log the raw EXI bytestream messages. This requires the `LOG_LEVEL` to be set to `DEBUG`. |
| `PROTOCOLS` | `DIN_SPEC_70121,ISO_15118_2,...` | A comma-separated list of enabled communication protocols on the SECC. |
| `AUTH_MODES` | `EIM,PNC` | A comma-separated list of selected authentication modes for the SECC (e.g., EIM for External Identification Means, PNC for Plug and Charge). |
| `USE_CPO_BACKEND` | `False` | Set to `True` to indicate that a CPO (Charge Point Operator) backend is available to fetch certificates or authorization data. |
| `ENABLE_TLS_1_3` | `False` | Set to `True` to enable the use of TLS version 1.3 for the communication link between the SECC and the EVCC. |

## Unit Tests

This repository is using `pytest` to test the implementations of interfaces to various devices.
In the root directory use the following to run all tests:
```bash
pytest .
```
