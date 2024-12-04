# dc-charging-station

This repository contains glue code in order to create a fully working DC charging station.

In our case we use [open-plc-utils](https://github.com/qca/open-plc-utils) for SLAC, [EcoG/iso15118](https://github.com/EcoG/iso15118) for the ISO15118 stack, an [EVAcharge SE](https://chargebyte.com/products/charging-station-communication/evacharge-se) for powerline communication and a ~~[Kratzer Automation battery tester](https://www.ni.com/de/shop/power-electronics-test-systems.html)~~ [EA-PSB 11000-10](https://elektroautomatik.com/shop/en/products/programmable-dc-laboratory-power-supplies/bidirectional-dc-laboratory-power-supplies/series-psb-10000-2u-1-5-3kw/1147/bi-directional-power-supply) as a bidirectional HV power supply.

## Unit Tests

This repository is using `pytest` to test the implementations of interfaces to various devices.
In the root directory use the following to run all tests:
```bash
pytest .
```