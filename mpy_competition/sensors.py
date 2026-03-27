import dht
import machine
import mpython as _mpy
import onewire
import servo
try:
    import ujson as json
except ImportError:
    import json

from machine import Pin, UART

from .utils import board_pin_name, clamp, machine_pin, normalize_board_pin, sleep_ms, sleep_us


class DigitalInputSensor:
    def __init__(self, pin, active_low=False, pull=None):
        self.pin = normalize_board_pin(pin)
        self.active_low = active_low
        self._io = _mpy.MPythonPin(self.pin, _mpy.PinMode.IN, pull=pull)

    def read_raw(self):
        return self._io.read_digital()

    def read(self):
        value = self.read_raw()
        return (not value) if self.active_low else bool(value)

    def on_change(self, callback, trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING):
        def _handler(_):
            callback(self.read())

        return self._io.irq(handler=_handler, trigger=trigger)


class AnalogInputSensor:
    def __init__(self, pin):
        self.pin = normalize_board_pin(pin)
        self._io = _mpy.MPythonPin(self.pin, _mpy.PinMode.ANALOG)

    def read(self):
        return self._io.read_analog()

    def read_scaled(self, out_min=0, out_max=100):
        raw = self.read()
        return _mpy.numberMap(raw, 0, 4095, out_min, out_max)


class PirSensor(DigitalInputSensor):
    pass


class InfraredObstacleSensor(DigitalInputSensor):
    def __init__(self, pin, active_low=True, pull=None):
        super().__init__(pin, active_low=active_low, pull=pull)


class UltrasonicHCSR04:
    def __init__(self, trigger_pin, echo_pin, timeout_us=30000):
        self.trigger_pin = normalize_board_pin(trigger_pin)
        self.echo_pin = normalize_board_pin(echo_pin)
        self.timeout_us = timeout_us
        self._trigger = machine_pin(self.trigger_pin, Pin.OUT)
        self._echo = machine_pin(self.echo_pin, Pin.IN)
        self._trigger.value(0)

    def read_cm(self, samples=1, sample_gap_ms=60):
        total = 0.0
        valid = 0
        for _ in range(samples):
            self._trigger.value(0)
            sleep_us(2)
            self._trigger.value(1)
            sleep_us(10)
            self._trigger.value(0)
            pulse = machine.time_pulse_us(self._echo, 1, self.timeout_us)
            if pulse > 0:
                total += pulse / 58.0
                valid += 1
            sleep_ms(sample_gap_ms)
        if valid == 0:
            raise OSError("ultrasonic timeout")
        return total / valid


class I2CUltrasonicSensor:
    def __init__(
        self,
        address,
        bus=None,
        command=None,
        command_delay_ms=70,
        read_size=2,
        register=None,
        big_endian=True,
        scale=1.0,
    ):
        self.address = address
        self.bus = bus or _mpy.i2c
        self.command = command
        self.command_delay_ms = command_delay_ms
        self.read_size = read_size
        self.register = register
        self.big_endian = big_endian
        self.scale = scale

    def read_cm(self):
        if self.command is not None:
            payload = bytes([self.command]) if isinstance(self.command, int) else bytes(self.command)
            self.bus.writeto(self.address, payload)
            sleep_ms(self.command_delay_ms)
        if self.register is None:
            data = self.bus.readfrom(self.address, self.read_size)
        else:
            data = self.bus.readfrom_mem(self.address, self.register, self.read_size)
        if self.big_endian:
            value = 0
            for byte in data:
                value = (value << 8) | byte
        else:
            value = 0
            shift = 0
            for byte in data:
                value |= byte << shift
                shift += 8
        return value * self.scale


class Ds18b20TemperatureSensor:
    def __init__(self, pin):
        import ds18x20

        self.pin = normalize_board_pin(pin)
        self._onewire = onewire.OneWire(machine_pin(self.pin))
        self._sensor = ds18x20.DS18X20(self._onewire)

    def scan(self):
        return self._sensor.scan()

    def read(self, index=0):
        roms = self.scan()
        if not roms:
            raise OSError("No DS18B20 on {}".format(board_pin_name(self.pin)))
        self._sensor.convert_temp()
        sleep_ms(750)
        return self._sensor.read_temp(roms[index])


class DHTSensor:
    def __init__(self, pin, model="dht11"):
        self.pin = normalize_board_pin(pin)
        mpin = machine_pin(self.pin)
        model = model.lower()
        if model == "dht22":
            self._sensor = dht.DHT22(mpin)
        else:
            self._sensor = dht.DHT11(mpin)
        self.model = model

    def read(self):
        self._sensor.measure()
        return {
            "temperature": self._sensor.temperature(),
            "humidity": self._sensor.humidity(),
        }


class AnalogTemperatureSensor(AnalogInputSensor):
    def __init__(self, pin, converter=None):
        super().__init__(pin)
        self.converter = converter

    def temperature(self):
        raw = self.read()
        if self.converter is None:
            return raw
        return self.converter(raw)


class ServoMotor:
    def __init__(self, pin, min_us=750, max_us=2250, actuation_range=180):
        self.pin = normalize_board_pin(pin)
        self._servo = servo.Servo(
            self.pin,
            min_us=min_us,
            max_us=max_us,
            actuation_range=actuation_range,
        )
        self.actuation_range = actuation_range

    def write_angle(self, angle):
        angle = clamp(int(angle), 0, int(self.actuation_range))
        self._servo.write_angle(angle)

    def write_us(self, width_us):
        self._servo.write_us(int(width_us))

    def sweep(self, start=0, stop=180, step=1, delay_ms=20):
        if step == 0:
            raise ValueError("step must not be 0")
        if start <= stop:
            current = start
            while current <= stop:
                self.write_angle(current)
                sleep_ms(delay_ms)
                current += abs(step)
            return
        current = start
        while current >= stop:
            self.write_angle(current)
            sleep_ms(delay_ms)
            current -= abs(step)


class RelayOutput:
    def __init__(self, pin, active_high=True):
        self.pin = normalize_board_pin(pin)
        self.active_high = active_high
        self._io = _mpy.MPythonPin(self.pin, _mpy.PinMode.OUT)
        self.off()

    def on(self):
        self._io.write_digital(1 if self.active_high else 0)

    def off(self):
        self._io.write_digital(0 if self.active_high else 1)

    def write(self, value):
        if value:
            self.on()
        else:
            self.off()


class SerialVisionCamera:
    def __init__(
        self,
        uart_id=1,
        baudrate=115200,
        tx_pin=None,
        rx_pin=None,
        timeout=1000,
        timeout_char=100,
    ):
        kwargs = {
            "baudrate": baudrate,
            "timeout": timeout,
            "timeout_char": timeout_char,
        }
        if tx_pin is not None:
            kwargs["tx"] = machine_pin(tx_pin)
        if rx_pin is not None:
            kwargs["rx"] = machine_pin(rx_pin)
        self.uart = UART(uart_id, **kwargs)

    def send_line(self, text):
        self.uart.write((str(text) + "\n").encode("utf-8"))

    def read_line(self):
        line = self.uart.readline()
        if not line:
            return None
        try:
            return line.decode("utf-8").strip()
        except AttributeError:
            return str(line).strip()

    def read_json(self):
        line = self.read_line()
        if not line:
            return None
        return json.loads(line)

    def read_payload(self):
        line = self.read_line()
        if not line:
            return None
        try:
            return json.loads(line)
        except Exception:
            return line

    def request_json(self, command, wait_ms=150):
        self.send_line(command)
        sleep_ms(wait_ms)
        return self.read_json()

    def request_label(self, command="detect"):
        payload = self.request_json(command)
        if payload is None:
            return None
        return payload.get("label")
