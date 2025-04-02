# dc-charging-station

![](Documentation/id3-charging-demo.jpg)

This repository contains glue code in order to create a fully working DC charging station.

In our case we use [open-plc-utils](https://github.com/qca/open-plc-utils) for SLAC, [EcoG-io/iso15118](https://github.com/EcoG-io/iso15118) for the ISO15118 stack, an [EVAcharge SE](https://chargebyte.com/products/charging-station-communication/evacharge-se) for powerline communication and a ~~[Kratzer Automation battery tester](https://www.ni.com/de/shop/power-electronics-test-systems.html)~~ [EA-PSB 11000-10](https://elektroautomatik.com/shop/en/products/programmable-dc-laboratory-power-supplies/bidirectional-dc-laboratory-power-supplies/series-psb-10000-2u-1-5-3kw/1147/bi-directional-power-supply) as a bidirectional HV power supply.

## Components

The idea of this repository is to have hardware abstraction interfaces which can be implemented for different hardware.
All of these interfaces (python abstract base classes) are defined in the `base_classes.py` file.

For implementing a charging station you need to implement the `ChargingStation` class as well as the `HighVoltageSource` class.
You can then give them as parameters to the ISO15118 EVSE controller based on [EcoG-io/iso15118](https://github.com/EcoG-io/iso15118).
This controller will handle vehicle detection, iso15118 communication and high voltage source parameter setting.

The SLAC process is currently not handeled by this project and needs to be performed using e.g. the `evse` tool from [open-plc-utils](https://github.com/qca/open-plc-utils).

## Running

For our current main test setup we use an [EVAcharge SE](https://chargebyte.com/products/charging-station-communication/evacharge-se), configured in network bridging mode and a [EA-PSB 11000-10](https://elektroautomatik.com/shop/en/products/programmable-dc-laboratory-power-supplies/bidirectional-dc-laboratory-power-supplies/series-psb-10000-2u-1-5-3kw/1147/bi-directional-power-supply) configured for remote control via SCPI.

First connect to the evacharge via ssh, flash the modem and run socat for forwarding the low level controls.

```bash
# ./flash-qca-temporarily.sh
# socat tcp-l:2020,reuseaddr,fork,crlf file:/dev/ttyAPP2,echo=0,b57600,raw
```

In a second terminal start the SLAC handling:
```bash
# cd open-plc-utils/slac
# sudo ./evse -i enx7cc2c61f051e
```

In a third terminal start the actual charging station code:
```bash
$ python -m venv venv
$ . venv/bin/activate
$ pip install -r requirements.txt
$ NETWORK_INTERFACE=enx7cc2c61f051e FREE_CHARGING_SERVICE=True LOG_LEVEL=INFO python3 secc-main-chargebyte-ea-psb.py
```

After plugging in the vehicle the charging process should start automatically.

## Unit Tests

This repository is using `pytest` to test the implementations of interfaces to various devices.
In the root directory use the following to run all tests:
```bash
pytest .
```
