try:
    import ujson as json
except ImportError:
    import json

try:
    import neopixel
except ImportError:
    neopixel = None

from mpy_competition import LocalHttpClient, PirSensor, UltrasonicHCSR04, board
from mpy_competition.utils import machine_pin, sleep_ms, ticks_ms


WIFI_SSID = "zr"
WIFI_PASSWORD = "zongrui2"

# For the Windows hotspot on this laptop, the host is usually 192.168.137.1.
SERVER_BASE_URL = "http://192.168.137.1:8765"

# If you use an external RGB strip, set RGB_PIN to the strip pin.
# Leave it as None to fall back to the onboard RGB driver.
RGB_PIN = None
RGB_COUNT = 8

PIR_PIN = "P2"
ULTRASONIC_TRIGGER_PIN = "P1"
ULTRASONIC_ECHO_PIN = "P0"

BUTTON_LOCAL_SIGNAL = "split"
BUTTON_EXTRA_SIGNAL = "sensor"
POLL_INTERVAL_MS = 700
SENSOR_INTERVAL_MS = 350
UPLOAD_INTERVAL_MS = 1200
NEAR_THRESHOLD_CM = 20


class RgbController:
    def __init__(self, pin=None, count=8):
        self.count = count
        self.external = None
        self.onboard = board.pixels.raw

        if pin is not None and neopixel is not None:
            self.external = neopixel.NeoPixel(machine_pin(pin), count)
        elif hasattr(self.onboard, "n"):
            self.count = min(count, int(self.onboard.n))
        else:
            self.count = min(count, 3)

    def _set_pixel(self, index, color):
        if self.external is not None:
            self.external[index] = color
            return
        self.onboard[index] = color

    def _write(self):
        if self.external is not None:
            self.external.write()
        else:
            self.onboard.write()

    def fill(self, color):
        if self.external is not None:
            for i in range(self.count):
                self.external[i] = color
            self.external.write()
            return
        board.pixels.fill(color)

    def off(self):
        self.fill((0, 0, 0))

    def split_rgb(self):
        groups = self._split_groups(self.count)
        colors = (
            (255, 0, 0),
            (0, 255, 0),
            (0, 0, 255),
        )
        idx = 0
        for group_size, color in zip(groups, colors):
            for _ in range(group_size):
                if idx < self.count:
                    self._set_pixel(idx, color)
                idx += 1
        self._write()

    def show_signal(self, signal):
        token = str(signal).strip().lower()
        if token in ("clear", "off", "0"):
            self.off()
            return
        if token in ("1", "split", "rgb"):
            self.split_rgb()
            return
        if token in ("2", "red"):
            self.fill((255, 0, 0))
            return
        if token in ("3", "green"):
            self.fill((0, 255, 0))
            return
        if token in ("4", "blue"):
            self.fill((0, 0, 255))
            return
        if token in ("sensor", "motion"):
            self.fill((255, 180, 0))
            return
        self.fill((80, 80, 80))

    @staticmethod
    def _split_groups(count):
        base = count // 3
        remainder = count % 3
        groups = [base, base, base]
        for i in range(remainder):
            groups[i] += 1
        return groups


class Topic3HotspotClient:
    def __init__(self):
        self.http = LocalHttpClient(SERVER_BASE_URL)
        self.rgb = RgbController(RGB_PIN, RGB_COUNT)
        self.pir = PirSensor(PIR_PIN)
        self.ultrasonic = UltrasonicHCSR04(ULTRASONIC_TRIGGER_PIN, ULTRASONIC_ECHO_PIN)
        self.last_command_id = None
        self.last_poll_at = 0
        self.last_sensor_at = 0
        self.last_upload_at = 0
        self.last_sensor_state = {"pir": 0, "distance_cm": None, "near": False}

    def connect_wifi(self):
        board.display.status("WiFi", ["connecting...", WIFI_SSID])
        try:
            config = board.wifi.connect(WIFI_SSID, WIFI_PASSWORD, timeout=10)
            ip = config[0]
            board.display.status("WiFi", ["ok", ip])
            return ip
        except Exception as exc:
            board.display.status("WiFi", ["failed", str(exc)[:16]])
            raise

    def run(self):
        self.connect_wifi()
        self.report_event("boot", {"status": "ready"})
        while True:
            now = ticks_ms()
            self._handle_buttons()
            if now - self.last_poll_at >= POLL_INTERVAL_MS:
                self.last_poll_at = now
                self.pull_command()
            if now - self.last_sensor_at >= SENSOR_INTERVAL_MS:
                self.last_sensor_at = now
                self.update_sensor_state()
            sleep_ms(50)

    def _handle_buttons(self):
        if board.buttons.was_pressed("a"):
            self.apply_signal(BUTTON_LOCAL_SIGNAL, source="button")
        if board.buttons.was_pressed("b"):
            self.apply_signal(BUTTON_EXTRA_SIGNAL, source="button")

    def pull_command(self):
        try:
            payload = self.http.get_json("/api/state")
        except Exception as exc:
            board.display.status("Server", ["poll failed", str(exc)[:16]])
            return

        command_id = payload.get("command_id")
        if command_id is None or command_id == self.last_command_id:
            return

        self.last_command_id = command_id
        signal = payload.get("signal", "")
        self.apply_signal(signal, source="web")

    def update_sensor_state(self):
        pir_value = 1 if self.pir.read() else 0
        distance_cm = None
        near = False
        try:
            distance_cm = self.ultrasonic.read_cm(samples=1)
            near = distance_cm <= NEAR_THRESHOLD_CM
        except Exception:
            distance_cm = None

        state = {
            "pir": pir_value,
            "distance_cm": distance_cm,
            "near": near,
        }
        changed = (
            state["pir"] != self.last_sensor_state["pir"]
            or state["near"] != self.last_sensor_state["near"]
        )
        self.last_sensor_state = state

        if changed or ticks_ms() - self.last_upload_at >= UPLOAD_INTERVAL_MS:
            self.last_upload_at = ticks_ms()
            self.report_event("sensor", state)

    def apply_signal(self, signal, source="web"):
        self.rgb.show_signal(signal)
        self.present_signal(signal, source=source)
        payload = {
            "signal": str(signal),
            "source": source,
            "sensor": self.last_sensor_state,
        }
        self.report_event("signal", payload)

    def present_signal(self, signal, source="web"):
        token = str(signal).strip().lower()
        if token in ("1", "split", "rgb"):
            board.display.status("Signal", [source, "3/3/2 rgb"])
            return
        if token in ("2", "red"):
            board.display.status("Signal", [source, "all red"])
            return
        if token in ("3", "green"):
            board.display.status("Signal", [source, "all green"])
            return
        if token in ("4", "blue"):
            board.display.status("Signal", [source, "all blue"])
            return
        if token in ("sensor", "motion"):
            rows = [
                "pir={}".format(self.last_sensor_state["pir"]),
                "dist={}".format(self._format_distance(self.last_sensor_state["distance_cm"])),
            ]
            board.display.status("Sensor", rows)
            return
        if token in ("clear", "off", "0"):
            board.display.status("Signal", [source, "cleared"])
            return
        board.display.status("Signal", [source, str(signal)[:16]])

    def report_event(self, event_type, payload):
        body = {
            "event": event_type,
            "payload": payload,
        }
        try:
            self.http.post_json("/api/report", body)
        except Exception:
            pass

    @staticmethod
    def _format_distance(value):
        if value is None:
            return "--"
        return "{}cm".format(int(value))


client = Topic3HotspotClient()
client.run()
