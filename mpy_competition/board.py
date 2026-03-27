import music
import mpython as _mpy

from machine import Pin

from .utils import clamp, normalize_board_pin, sleep_ms, ticks_ms


def _touch_attr(primary_name, alias_name):
    if hasattr(_mpy, primary_name):
        return getattr(_mpy, primary_name)
    return getattr(_mpy, alias_name)


class BoardDisplay:
    def __init__(self, driver):
        self._driver = driver

    def clear(self, show=True):
        self._driver.fill(0)
        if show:
            self._driver.show()

    def text(self, value, x=0, y=0, show=True):
        self._driver.DispChar(str(value), x, y)
        if show:
            self._driver.show()

    def lines(self, values, x=0, y=0, step=16, clear=True, show=True):
        if clear:
            self._driver.fill(0)
        current_y = y
        for value in values:
            self._driver.DispChar(str(value), x, current_y)
            current_y += step
        if show:
            self._driver.show()

    def status(self, title, rows=None, show=True):
        if rows is None:
            rows = []
        lines = [title]
        lines.extend(rows)
        self.lines(lines, clear=True, show=show)

    def contrast(self, value):
        self._driver.contrast(clamp(int(value), 0, 255))

    def power(self, enabled):
        if enabled:
            self._driver.poweron()
        else:
            self._driver.poweroff()

    @property
    def raw(self):
        return self._driver


class BoardPixels:
    def __init__(self, driver):
        self._driver = driver

    def set(self, index, color, show=True):
        self._driver[index] = self._normalize_color(color)
        if show:
            self._driver.write()

    def fill(self, color, show=True):
        self._driver.fill(self._normalize_color(color))
        if show:
            self._driver.write()

    def off(self, show=True):
        self.fill((0, 0, 0), show=show)

    def brightness(self, value):
        self._driver.brightness(clamp(float(value), 0.0, 1.0))

    def blink(self, color, times=1, on_ms=120, off_ms=120):
        for _ in range(times):
            self.fill(color, show=True)
            sleep_ms(on_ms)
            self.off(show=True)
            sleep_ms(off_ms)

    def status(self, ok=True):
        if ok:
            self.fill((0, 32, 0))
        else:
            self.fill((32, 0, 0))

    @staticmethod
    def _normalize_color(color):
        return (
            clamp(int(color[0]), 0, 255),
            clamp(int(color[1]), 0, 255),
            clamp(int(color[2]), 0, 255),
        )

    @property
    def raw(self):
        return self._driver


class BoardButtons:
    def __init__(self, button_a, button_b):
        self._buttons = {
            "a": button_a,
            "b": button_b,
        }

    def is_pressed(self, name):
        return self._buttons[name.lower()].is_pressed()

    def was_pressed(self, name):
        return self._buttons[name.lower()].was_pressed()

    def presses(self, name):
        return self._buttons[name.lower()].get_presses()

    def on(self, name, pressed=None, released=None):
        button = self._buttons[name.lower()]
        if pressed is not None:
            button.event_pressed = pressed
        if released is not None:
            button.event_released = released

    def wait_any(self, timeout_ms=None):
        start = ticks_ms()
        while True:
            if self.is_pressed("a"):
                return "a"
            if self.is_pressed("b"):
                return "b"
            if timeout_ms is not None and ticks_ms() - start >= timeout_ms:
                return None
            sleep_ms(10)


class BoardTouchPads:
    def __init__(self):
        self._pads = {
            "p": _touch_attr("touchpad_p", "touchPad_P"),
            "y": _touch_attr("touchpad_y", "touchPad_Y"),
            "t": _touch_attr("touchpad_t", "touchPad_T"),
            "h": _touch_attr("touchpad_h", "touchPad_H"),
            "o": _touch_attr("touchpad_o", "touchPad_O"),
            "n": _touch_attr("touchpad_n", "touchPad_N"),
        }

    def read(self, name):
        return self._pads[name.lower()].read()

    def is_pressed(self, name):
        return self._pads[name.lower()].is_pressed()

    def was_pressed(self, name):
        return self._pads[name.lower()].was_pressed()

    def on(self, name, pressed=None, released=None):
        pad = self._pads[name.lower()]
        if pressed is not None:
            pad.event_pressed = pressed
        if released is not None:
            pad.event_released = released

    def config(self, name, threshold):
        pad = self._pads[name.lower()]
        if hasattr(pad, "config"):
            pad.config(threshold)


class BoardMotion:
    def light(self):
        return _mpy.light.read()

    def sound(self):
        return _mpy.sound.read()

    def acceleration(self):
        return {
            "x": _mpy.accelerometer.get_x(),
            "y": _mpy.accelerometer.get_y(),
            "z": _mpy.accelerometer.get_z(),
        }

    def roll_pitch(self):
        if hasattr(_mpy.accelerometer, "roll_pitch_angle"):
            roll, pitch = _mpy.accelerometer.roll_pitch_angle()
            return {"roll": roll, "pitch": pitch}
        return None

    def compass_heading(self):
        if hasattr(_mpy, "magnetic"):
            return _mpy.magnetic.get_heading()
        return None

    def environment(self):
        if hasattr(_mpy, "bme280"):
            return {
                "temperature": _mpy.bme280.temperature(),
                "humidity": _mpy.bme280.humidity(),
                "pressure": _mpy.bme280.pressure(),
            }
        return None


class BoardBuzzer:
    def beep(self, frequency=880, duration_ms=120, wait=True):
        music.pitch(int(frequency), int(duration_ms), wait=wait)

    def tone(self, frequency, duration_ms=-1, wait=True):
        music.pitch(int(frequency), int(duration_ms), wait=wait)

    def melody(self, notes, wait=True, loop=False):
        music.play(notes, wait=wait, loop=loop)

    def stop(self):
        music.stop()


class BoardWiFi:
    def __init__(self):
        self._client = None

    def _ensure(self):
        if self._client is None:
            self._client = _mpy.wifi()
        return self._client

    def connect(self, ssid, password, timeout=10):
        client = self._ensure()
        client.connectWiFi(ssid, password, timeout=timeout)
        return client.sta.ifconfig()

    def disconnect(self):
        if self._client is not None:
            self._client.disconnectWiFi()

    def is_connected(self):
        return self._client is not None and self._client.sta.isconnected()

    def ifconfig(self):
        if self._client is None:
            return None
        return self._client.sta.ifconfig()

    def start_ap(self, essid, password, channel=10):
        client = self._ensure()
        client.enable_APWiFi(essid, password, channel=channel)
        return client.ap.ifconfig()

    def stop_ap(self):
        if self._client is not None:
            self._client.disable_APWiFi()

    @property
    def raw(self):
        return self._ensure()


class BoardIO:
    def __init__(self):
        self.i2c = _mpy.i2c

    def digital_in(self, pin, pull=None):
        return _mpy.MPythonPin(normalize_board_pin(pin), _mpy.PinMode.IN, pull=pull)

    def digital_out(self, pin):
        return _mpy.MPythonPin(normalize_board_pin(pin), _mpy.PinMode.OUT)

    def analog_in(self, pin):
        return _mpy.MPythonPin(normalize_board_pin(pin), _mpy.PinMode.ANALOG)

    def pwm_out(self, pin):
        return _mpy.MPythonPin(normalize_board_pin(pin), _mpy.PinMode.PWM)

    def read_digital(self, pin, pull=None):
        return self.digital_in(pin, pull=pull).read_digital()

    def write_digital(self, pin, value):
        io = self.digital_out(pin)
        io.write_digital(1 if value else 0)
        return io

    def read_analog(self, pin):
        return self.analog_in(pin).read_analog()

    def write_pwm(self, pin, duty, freq=1000):
        io = self.pwm_out(pin)
        io.write_analog(int(duty), freq=int(freq))
        return io

    def irq(self, pin, handler, trigger=Pin.IRQ_RISING, pull=None):
        io = self.digital_in(pin, pull=pull)
        return io.irq(handler=handler, trigger=trigger)


class CompetitionBoard:
    def __init__(self):
        self.display = BoardDisplay(_mpy.oled)
        self.pixels = BoardPixels(_mpy.rgb)
        self.buttons = BoardButtons(_mpy.button_a, _mpy.button_b)
        self.touch = BoardTouchPads()
        self.motion = BoardMotion()
        self.buzzer = BoardBuzzer()
        self.wifi = BoardWiFi()
        self.io = BoardIO()
        self.sleep_ms = sleep_ms
        self.map_value = getattr(_mpy, "numberMap", None)


board = CompetitionBoard()
