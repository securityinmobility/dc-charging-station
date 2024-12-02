import sys
import easy_scpi as scpi
from typing_extensions import override, List

sys.path.append("..")
from base_classes import HighVoltageSource


class ElektroAutomatikBidiPowersupply(HighVoltageSource):
    def __init__(self, ip: str, port: int, max_power: float):
        self.instrument = scpi.Instrument(read_termination='\n', write_termination='\n', timeout=5000)
        self.instrument.rid = f"TCPIP::{ip}::{port}::SOCKET"
        self.instrument.connect()
        self.instrument.syst.lock("ON")
        self._raise_if_errors()

        self.instrument.output("OFF")

        system_max_power = self._parse_float_with_unit(self.instrument.system.nominal.power(), 'W')
        if system_max_power < max_power:
            raise ValueError(f"powersupply nominal power {system_max_power} is lower than given max_power {max_power}")

        self.max_voltage = self._parse_float_with_unit(self.instrument.system.nominal.voltage(), 'V')
        self.max_power = max_power

        self.instrument.source.power.limit.high(max_power)
        self.instrument.sink.power.limit.high(max_power)

        self._raise_if_errors()

    def __del__(self):
        self.instrument.disconnect()

    def _parse_float_with_unit(self, value: str, unit: str) -> float:
        value = value.rstrip(unit).strip()
        return float(value)

    def _read_errors(self) -> List[str]:
        result = []
        while True:
            msg = self.instrument.system.error.next()
            if msg[0] == "0":
                break
            result.append(msg)
        return result

    def _raise_if_errors(self):
        errs = self._read_errors()
        if len(errs) != 0:
            raise RuntimeError(f"powersupply reported errors {errs}")

    @override
    def check_insulation(self) -> bool:
        # TODO check error status bits of EA-PSB
        return True

    @override
    def get_voltage(self) -> float:
        x = self._parse_float_with_unit(self.instrument.measure.voltage(), 'V')
        self._raise_if_errors()
        return x

    @override
    def get_current(self) -> float:
        x = self._parse_float_with_unit(self.instrument.measure.current(), 'A')
        self._raise_if_errors()
        return x

    def _is_zero_or_nan(self, x) -> bool:
        return x is None or x == 0

    @override
    def set_charging_target(
        self, current: float, min_voltage: float, max_voltage: float
    ):
        if current == 0 and min_voltage == 0 and max_voltage == 0:
            self.instrument.output("OFF")
            self._raise_if_errors()
            return

        self._raise_if_errors()

        if min_voltage > max_voltage:
            raise ValueError(f"given min voltage {min_voltage} is grater than given max voltage {max_voltage}")
        if max_voltage > self.max_voltage or min_voltage > self.max_voltage:
            raise ValueError(f"given voltage too high, a maximum of {self.max_voltage} is allowed, given {min_voltage}~{max_voltage}")
        if abs(current) * min_voltage > self.max_power:
            max_current = self.max_power / min_voltage
            current = (current / abs(current)) * max_current

        if current < 0:
            self.instrument.sink.current(-1 * current)
            self.instrument.output("ON")
        else:
            self.instrument.source.voltage(min_voltage)
            self.instrument.source.current(current)
            self.instrument.output("ON")

        self._raise_if_errors()
