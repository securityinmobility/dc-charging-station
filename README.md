# dc-charging-station

This repository contains glue code in order to create a fully working DC charging station.

In our case we use [SwitchEV/josev](https://github.com/SwitchEV/josev) for the ISO15118 stack, an [EVAcharge SE](https://chargebyte.com/products/charging-station-communication/evacharge-se) for powerline communication and a [Kratzer Automation battery tester](https://www.ni.com/de/shop/power-electronics-test-systems.html) as a HV power supply.


running Unit Test:

    from the command line, inside the test repositories from chargebyte or kratzer, run in the command line `pytest`
    in order to run only one file:

    ```
    pytest name_of_file
    ```

    to run a single test or a group of tests, use the flag k

    ```
    pytest name_of_file -k 'name_of_test'
    ```

