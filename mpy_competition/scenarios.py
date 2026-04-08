from machine import UART

from .board import board
from .sensors import SerialVisionCamera, ServoMotor, UltrasonicHCSR04
from .utils import normalize_board_pin, sleep_ms, ticks_ms


DEFAULT_SHARED_SCENE_CONFIG = {
    "loop_delay_ms": 50,
    "display_interval_ms": 250,
    "mode_switch_button": "b",
    "help_button": "a",
    "label_hold_ms": 1500,
    "bridge1956": {
        "uart_id": 1,
        "tx_pin": "P16",
        "rx_pin": "P15",
        "baudrate": 115200,
        "timeout": 40,
        "timeout_char": 10,
    },
    "vision": {
        "uart_id": 2,
        "tx_pin": "P14",
        "rx_pin": "P13",
        "baudrate": 2000000,
        "timeout": 40,
        "timeout_char": 10,
    },
    "trash": {
        "distance_trigger_pin": "P8",
        "distance_echo_pin": "P9",
        "fill_trigger_pin": "P1",
        "fill_echo_pin": "P2",
        "servo_pin": "P0",
        "servo_open_angle": 95,
        "servo_close_angle": 5,
        "open_threshold_cm": 15,
        "full_threshold_cm": 8,
        "open_hold_ms": 3000,
    },
    "guide": {
        "distance_trigger_pin": "P8",
        "distance_echo_pin": "P9",
        "near_cm": 15,
        "mid_cm": 30,
        "far_cm": 60,
        "help_flash_ms": 4000,
        "help_flash_interval_ms": 80,
        "beep_duration_ms": 35,
        "beep_frequency": 1600,
        "resend_ms": 1200,
    },
}


_LABEL_ALIASES = {
    "person": ("person", "\u4eba"),
    "people": ("person", "\u4eba"),
    "human": ("person", "\u4eba"),
    "body": ("person", "\u4eba"),
    "man": ("person", "\u4eba"),
    "woman": ("person", "\u4eba"),
    "ren": ("person", "\u4eba"),
    "\u4eba": ("person", "\u4eba"),
    "table": ("table", "\u684c\u5b50"),
    "desk": ("table", "\u684c\u5b50"),
    "zhuozi": ("table", "\u684c\u5b50"),
    "\u684c\u5b50": ("table", "\u684c\u5b50"),
    "chair": ("chair", "\u6905\u5b50"),
    "seat": ("chair", "\u6905\u5b50"),
    "stool": ("chair", "\u6905\u5b50"),
    "yizi": ("chair", "\u6905\u5b50"),
    "\u6905\u5b50": ("chair", "\u6905\u5b50"),
}


def _copy_config(data):
    copied = {}
    for key, value in data.items():
        if isinstance(value, dict):
            copied[key] = _copy_config(value)
        else:
            copied[key] = value
    return copied


def _merge_config(base, override):
    merged = _copy_config(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _merge_config(merged[key], value)
        else:
            merged[key] = value
    return merged


def build_shared_scene_config(overrides=None):
    if overrides is None:
        overrides = {}
    return _merge_config(DEFAULT_SHARED_SCENE_CONFIG, overrides)


class SimpleLineBridge:
    def __init__(self, config):
        self.uart = UART(
            config["uart_id"],
            baudrate=config["baudrate"],
            tx=normalize_board_pin(config["tx_pin"]),
            rx=normalize_board_pin(config["rx_pin"]),
            timeout=config.get("timeout", 40),
            timeout_char=config.get("timeout_char", 10),
        )

    def send_line(self, value):
        self.uart.write((str(value) + "\n").encode("utf-8"))

    def send_many(self, values):
        for value in values:
            self.send_line(value)


class SharedHardware:
    def __init__(self, config):
        self.config = config
        trash_cfg = config["trash"]
        guide_cfg = config["guide"]

        self.trash_sensor = UltrasonicHCSR04(
            trash_cfg["distance_trigger_pin"],
            trash_cfg["distance_echo_pin"],
        )
        if (
            guide_cfg["distance_trigger_pin"] == trash_cfg["distance_trigger_pin"]
            and guide_cfg["distance_echo_pin"] == trash_cfg["distance_echo_pin"]
        ):
            self.guide_sensor = self.trash_sensor
        else:
            self.guide_sensor = UltrasonicHCSR04(
                guide_cfg["distance_trigger_pin"],
                guide_cfg["distance_echo_pin"],
            )
        self.fill_sensor = UltrasonicHCSR04(
            trash_cfg["fill_trigger_pin"],
            trash_cfg["fill_echo_pin"],
        )
        self.servo = ServoMotor(trash_cfg["servo_pin"])
        self.camera = SerialVisionCamera(
            uart_id=config["vision"]["uart_id"],
            baudrate=config["vision"]["baudrate"],
            tx_pin=config["vision"]["tx_pin"],
            rx_pin=config["vision"]["rx_pin"],
            timeout=config["vision"].get("timeout", 40),
            timeout_char=config["vision"].get("timeout_char", 10),
        )
        self.bridge1956 = SimpleLineBridge(config["bridge1956"])
        self.close_lid()

    def read_distance(self, sensor, samples=1):
        try:
            return sensor.read_cm(samples=samples)
        except Exception:
            return None

    def open_lid(self):
        self.servo.write_angle(self.config["trash"]["servo_open_angle"])

    def close_lid(self):
        self.servo.write_angle(self.config["trash"]["servo_close_angle"])

    def send_1956(self, *values):
        self.bridge1956.send_many(values)

    def read_camera_detection(self):
        if hasattr(self.camera.uart, "any") and not self.camera.uart.any():
            return None
        payload = self.camera.read_payload()
        return normalize_detection_payload(payload)


def normalize_detection_payload(payload):
    if payload is None:
        return None

    raw_text = _extract_label_text(payload)
    if not raw_text:
        return None

    normalized = _normalize_label_text(raw_text)
    if normalized is None:
        return None

    return {
        "token": normalized[0],
        "display": normalized[1],
        "raw": raw_text,
        "payload": payload,
    }


def _extract_label_text(payload):
    if isinstance(payload, dict):
        for key in ("label", "class", "name", "target", "object", "result"):
            value = payload.get(key)
            if value:
                return str(value)
        data = payload.get("data")
        if isinstance(data, dict):
            return _extract_label_text(data)
        return None

    if isinstance(payload, (list, tuple)):
        for item in payload:
            text = _extract_label_text(item)
            if text:
                return text
        return None

    return str(payload)


def _normalize_label_text(text):
    token = str(text).strip().lower()
    for splitter in (",", ";", "|", "=", ":"):
        if splitter in token:
            pieces = [piece.strip() for piece in token.split(splitter) if piece.strip()]
            for piece in pieces:
                if piece in _LABEL_ALIASES:
                    return _LABEL_ALIASES[piece]
    if token in _LABEL_ALIASES:
        return _LABEL_ALIASES[token]
    for alias, normalized in _LABEL_ALIASES.items():
        if alias in token:
            return normalized
    return None


class TrashCanScene:
    name = "trash"

    def __init__(self, hardware, config):
        self.hardware = hardware
        self.config = config
        self.lid_close_at = 0
        self.last_display_at = 0
        self.last_presence_cm = None
        self.last_fill_cm = None

    def enter(self):
        self.hardware.close_lid()
        board.buzzer.stop()
        board.pixels.fill((0, 0, 12))
        board.display.status("trash can", ["waiting..."])

    def leave(self):
        self.hardware.close_lid()
        board.buzzer.stop()

    def tick(self, now_ms):
        self.last_presence_cm = self.hardware.read_distance(self.hardware.trash_sensor, samples=1)
        self.last_fill_cm = self.hardware.read_distance(self.hardware.fill_sensor, samples=1)

        if self.last_presence_cm is not None and self.last_presence_cm <= self.config["open_threshold_cm"]:
            self.hardware.open_lid()
            self.lid_close_at = now_ms + self.config["open_hold_ms"]

        if self.lid_close_at and now_ms >= self.lid_close_at:
            self.hardware.close_lid()
            self.lid_close_at = 0

        is_full = self.last_fill_cm is not None and self.last_fill_cm <= self.config["full_threshold_cm"]
        if is_full:
            if (now_ms // 250) % 2 == 0:
                board.pixels.fill((32, 0, 0))
            else:
                board.pixels.off()
        elif self.lid_close_at:
            board.pixels.fill((0, 0, 32))
        else:
            board.pixels.fill((0, 20, 0))

        if now_ms - self.last_display_at >= self.hardware.config["display_interval_ms"]:
            self.last_display_at = now_ms
            state = "full" if is_full else ("open" if self.lid_close_at else "idle")
            board.display.status(
                "trash can",
                [
                    "near:{}cm".format(_fmt_cm(self.last_presence_cm)),
                    "fill:{}cm".format(_fmt_cm(self.last_fill_cm)),
                    "state:{}".format(state),
                ],
            )


class GuideStickScene:
    name = "guide"

    def __init__(self, hardware, config, app_config):
        self.hardware = hardware
        self.config = config
        self.app_config = app_config
        self.last_display_at = 0
        self.last_beep_at = 0
        self.last_sent_at = 0
        self.help_until = 0
        self.last_seen_at = 0
        self.current_detection = None
        self.last_sent_token = None
        self.last_distance_cm = None

    def enter(self):
        board.buzzer.stop()
        board.pixels.fill((0, 0, 16))
        board.display.status("guide stick", ["waiting..."])

    def leave(self):
        board.buzzer.stop()

    def tick(self, now_ms):
        detection = self.hardware.read_camera_detection()
        if detection is not None:
            self.current_detection = detection
            self.last_seen_at = now_ms
            if (
                detection["token"] != self.last_sent_token
                or now_ms - self.last_sent_at >= self.config["resend_ms"]
            ):
                self.hardware.send_1956("0", detection["token"])
                self.last_sent_token = detection["token"]
                self.last_sent_at = now_ms

        if self.current_detection is not None and now_ms - self.last_seen_at >= self.app_config["label_hold_ms"]:
            self.current_detection = None

        self.last_distance_cm = self.hardware.read_distance(self.hardware.guide_sensor, samples=1)
        self._update_distance_alarm(now_ms)

        if board.buttons.was_pressed(self.app_config["help_button"]):
            token = "unknown"
            if self.current_detection is not None:
                token = self.current_detection["token"]
            self.hardware.send_1956("help", token)
            self.help_until = now_ms + self.config["help_flash_ms"]

        self._update_pixels(now_ms)

        if now_ms - self.last_display_at >= self.app_config["display_interval_ms"]:
            self.last_display_at = now_ms
            display_name = "none"
            if self.current_detection is not None:
                display_name = self.current_detection["display"]
            help_state = "help" if now_ms < self.help_until else "normal"
            board.display.status(
                "guide stick",
                [
                    "obj:{}".format(display_name),
                    "dist:{}cm".format(_fmt_cm(self.last_distance_cm)),
                    "mode:{}".format(help_state),
                ],
            )

    def _update_distance_alarm(self, now_ms):
        distance = self.last_distance_cm
        interval = None
        if distance is not None:
            if distance <= self.config["near_cm"]:
                interval = 120
            elif distance <= self.config["mid_cm"]:
                interval = 240
            elif distance <= self.config["far_cm"]:
                interval = 450

        if interval is None:
            board.buzzer.stop()
            return

        if now_ms - self.last_beep_at >= interval:
            self.last_beep_at = now_ms
            board.buzzer.beep(
                frequency=self.config["beep_frequency"],
                duration_ms=self.config["beep_duration_ms"],
                wait=False,
            )

    def _update_pixels(self, now_ms):
        if now_ms < self.help_until:
            flash_on = ((now_ms // self.config["help_flash_interval_ms"]) % 2) == 0
            if flash_on:
                board.pixels.fill((32, 0, 0))
            else:
                board.pixels.off()
            return

        if self.current_detection is not None:
            board.pixels.fill((32, 18, 0))
        else:
            board.pixels.fill((0, 0, 16))


class DualSceneCompetitionApp:
    def __init__(self, config=None):
        self.config = build_shared_scene_config(config)
        self.hardware = SharedHardware(self.config)
        self.scenes = {
            "trash": TrashCanScene(self.hardware, self.config["trash"]),
            "guide": GuideStickScene(self.hardware, self.config["guide"], self.config),
        }
        self.scene_order = ["trash", "guide"]
        self.current_scene_name = self.scene_order[0]
        self.current_scene = self.scenes[self.current_scene_name]
        self.current_scene.enter()

    def switch_scene(self):
        self.current_scene.leave()
        current_index = self.scene_order.index(self.current_scene_name)
        next_index = (current_index + 1) % len(self.scene_order)
        self.current_scene_name = self.scene_order[next_index]
        self.current_scene = self.scenes[self.current_scene_name]
        self.current_scene.enter()
        sleep_ms(180)

    def run_forever(self):
        while True:
            now_ms = ticks_ms()
            if board.buttons.was_pressed(self.config["mode_switch_button"]):
                self.switch_scene()
                now_ms = ticks_ms()
            self.current_scene.tick(now_ms)
            sleep_ms(self.config["loop_delay_ms"])


def _fmt_cm(value):
    if value is None:
        return "--"
    return str(int(value))
