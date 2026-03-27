from machine import UART

from .utils import machine_pin, sleep_ms
from .vendor import MuVisionSensor as _muvs_binary
from .vendor import MuVisionSensor3AT as _muvs_at


DEFAULT_AI_CAMERA_TX_PIN = "P16"
DEFAULT_AI_CAMERA_RX_PIN = "P15"
DEFAULT_AI_CAMERA_UART_ID = 1
DEFAULT_PROBE_VISION = "color_detect"
COMMON_BAUDRATES = (115200, 9600, 57600, 230400, 460800, 921600)
LEGACY_SMART_CAMERA_TX_PIN = "P14"
LEGACY_SMART_CAMERA_RX_PIN = "P13"
LEGACY_SMART_CAMERA_BAUDRATE = 2000000


_VISION_MAP = {
    "color": _muvs_binary.VISION_COLOR_DETECT,
    "color_detect": _muvs_binary.VISION_COLOR_DETECT,
    "color_recognition": _muvs_binary.VISION_COLOR_RECOGNITION,
    "ball": _muvs_binary.VISION_BALL_DETECT,
    "body": _muvs_binary.VISION_BODY_DETECT,
    "shape": _muvs_binary.VISION_SHAPE_CARD_DETECT,
    "traffic": _muvs_binary.VISION_TRAFFIC_CARD_DETECT,
    "number": _muvs_binary.VISION_NUM_CARD_DETECT,
}


class AICameraError(Exception):
    pass


def _is_ok(err):
    return err in (None, False, 0)


def _camera_uart(uart_id, tx_pin, rx_pin, baudrate, timeout=1000, timeout_char=10):
    return UART(
        uart_id,
        baudrate=baudrate,
        tx=machine_pin(tx_pin),
        rx=machine_pin(rx_pin),
        timeout=timeout,
        timeout_char=timeout_char,
    )


class _MuVisionCameraBase:
    protocol = "unknown"
    module = None

    def __init__(
        self,
        uart_id=DEFAULT_AI_CAMERA_UART_ID,
        tx_pin=DEFAULT_AI_CAMERA_TX_PIN,
        rx_pin=DEFAULT_AI_CAMERA_RX_PIN,
        baudrate=115200,
        debug=False,
    ):
        self.uart_id = uart_id
        self.tx_pin = tx_pin
        self.rx_pin = rx_pin
        self.baudrate = baudrate
        self.debug = debug
        self.uart = _camera_uart(uart_id, tx_pin, rx_pin, baudrate)
        self.driver = self._create_driver(debug)
        self._enabled = {}

    def _create_driver(self, debug):
        raise NotImplementedError

    def begin(self):
        raise NotImplementedError

    def _vision(self, vision):
        if isinstance(vision, int):
            return vision
        key = str(vision).strip().lower()
        if key not in _VISION_MAP:
            raise ValueError("Unsupported AI vision mode: {}".format(vision))
        return _VISION_MAP[key]

    def _field(self, name):
        table = {
            "status": self.module.Status,
            "x": self.module.XValue,
            "y": self.module.YValue,
            "width": self.module.WidthValue,
            "height": self.module.HeightValue,
            "label": self.module.Label,
            "r": self.module.RValue,
            "g": self.module.GValue,
            "b": self.module.BValue,
        }
        key = str(name).strip().lower()
        if key not in table:
            raise ValueError("Unsupported AI field: {}".format(name))
        return table[key]

    def _ensure_ok(self, err, action):
        if not _is_ok(err):
            raise AICameraError("{} failed: {}".format(action, err))

    def _mark_enabled(self, vision, enabled):
        key = self._vision(vision)
        if enabled:
            self._enabled[key] = True
        elif key in self._enabled:
            del self._enabled[key]

    def enable(self, vision):
        vision_const = self._vision(vision)
        if vision_const in self._enabled:
            return
        err = self.driver.VisionBegin(vision_const)
        self._ensure_ok(err, "VisionBegin")
        sleep_ms(30)
        self._mark_enabled(vision_const, True)

    def disable(self, vision):
        vision_const = self._vision(vision)
        if vision_const not in self._enabled:
            return
        err = self.driver.VisionEnd(vision_const)
        self._ensure_ok(err, "VisionEnd")
        self._mark_enabled(vision_const, False)

    def update(self, vision, wait_all_result=True):
        vision_const = self._vision(vision)
        self.enable(vision_const)
        return self.driver.UpdateResult(vision_const, wait_all_result)

    def read_value(self, vision, field):
        vision_const = self._vision(vision)
        self.enable(vision_const)
        return self.driver.GetValue(vision_const, self._field(field))

    def read_target(self, vision, refresh=True):
        vision_const = self._vision(vision)
        self.enable(vision_const)
        if refresh:
            self.driver.UpdateResult(vision_const)
        count = self.driver.GetValue(vision_const, self.module.Status)
        if not count:
            return None
        return {
            "count": count,
            "x": self.driver.GetValue(vision_const, self.module.XValue),
            "y": self.driver.GetValue(vision_const, self.module.YValue),
            "width": self.driver.GetValue(vision_const, self.module.WidthValue),
            "height": self.driver.GetValue(vision_const, self.module.HeightValue),
            "label": self.driver.GetValue(vision_const, self.module.Label),
        }

    def probe(self, vision=DEFAULT_PROBE_VISION):
        self.enable(vision)
        self.update(vision)
        return True

    def close(self):
        for vision_const in list(self._enabled.keys()):
            try:
                self.driver.VisionEnd(vision_const)
            except Exception:
                pass
        try:
            self.uart.read()
        except Exception:
            pass


class MuVisionBinaryCamera(_MuVisionCameraBase):
    protocol = "muvs-binary"
    module = _muvs_binary

    def _create_driver(self, debug):
        return self.module.MuVisionSensor(debug=debug)

    def begin(self):
        self.driver.begin(self.uart)
        return self


class MuVisionATCamera(_MuVisionCameraBase):
    protocol = "muvs-at"
    module = _muvs_at

    def _create_driver(self, debug):
        return self.module.MuVisionSensor3AT(debug=debug)

    def begin(self):
        err = self.driver.begin(self.uart)
        self._ensure_ok(err, "Sensor begin")
        return self


def probe_ai_camera(
    uart_id=DEFAULT_AI_CAMERA_UART_ID,
    tx_pin=DEFAULT_AI_CAMERA_TX_PIN,
    rx_pin=DEFAULT_AI_CAMERA_RX_PIN,
    baudrates=COMMON_BAUDRATES,
    protocols=("at", "binary"),
    probe_vision=DEFAULT_PROBE_VISION,
    debug=False,
):
    last_error = None
    for protocol in protocols:
        for baudrate in baudrates:
            camera = None
            try:
                if protocol == "at":
                    camera = MuVisionATCamera(
                        uart_id=uart_id,
                        tx_pin=tx_pin,
                        rx_pin=rx_pin,
                        baudrate=baudrate,
                        debug=debug,
                    )
                elif protocol == "binary":
                    camera = MuVisionBinaryCamera(
                        uart_id=uart_id,
                        tx_pin=tx_pin,
                        rx_pin=rx_pin,
                        baudrate=baudrate,
                        debug=debug,
                    )
                else:
                    raise ValueError("Unknown protocol: {}".format(protocol))

                camera.begin()
                camera.probe(probe_vision)
                return {
                    "protocol": camera.protocol,
                    "baudrate": baudrate,
                    "camera": camera,
                    "tx_pin": tx_pin,
                    "rx_pin": rx_pin,
                    "uart_id": uart_id,
                }
            except Exception as exc:
                last_error = exc
                if camera is not None:
                    try:
                        camera.close()
                    except Exception:
                        pass

    return {
        "protocol": None,
        "baudrate": None,
        "camera": None,
        "tx_pin": tx_pin,
        "rx_pin": rx_pin,
        "uart_id": uart_id,
        "error": last_error,
        "hint": "No MuVision UART protocol detected. Check wiring/power, then try legacy SmartCamera defaults: tx={}, rx={}, baud={}.".format(
            LEGACY_SMART_CAMERA_TX_PIN,
            LEGACY_SMART_CAMERA_RX_PIN,
            LEGACY_SMART_CAMERA_BAUDRATE,
        ),
    }


def build_ai_camera(
    protocol="auto",
    uart_id=DEFAULT_AI_CAMERA_UART_ID,
    tx_pin=DEFAULT_AI_CAMERA_TX_PIN,
    rx_pin=DEFAULT_AI_CAMERA_RX_PIN,
    baudrate=115200,
    debug=False,
):
    protocol = str(protocol).strip().lower()
    if protocol == "auto":
        result = probe_ai_camera(
            uart_id=uart_id,
            tx_pin=tx_pin,
            rx_pin=rx_pin,
            debug=debug,
        )
        camera = result.get("camera")
        if camera is None:
            raise AICameraError(result.get("hint"))
        return camera

    if protocol == "at":
        camera = MuVisionATCamera(
            uart_id=uart_id,
            tx_pin=tx_pin,
            rx_pin=rx_pin,
            baudrate=baudrate,
            debug=debug,
        )
        return camera.begin()

    if protocol == "binary":
        camera = MuVisionBinaryCamera(
            uart_id=uart_id,
            tx_pin=tx_pin,
            rx_pin=rx_pin,
            baudrate=baudrate,
            debug=debug,
        )
        return camera.begin()

    raise ValueError("Unsupported AI camera protocol: {}".format(protocol))
