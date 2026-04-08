try:
    import ujson as json
except ImportError:
    import json

import gc
import music
import time
import urequests

from bluebit import Ultrasonic
from mpython import *
import smartcamera_k230 as smartcamera


WIFI_SSID = "zr"
WIFI_PASSWORD = "zongrui2"
SERVER_BASE_URL = "http://192.168.137.1:8766"

TEAM_ID = "G4-01"
LOCATION = TEAM_ID

AI_MODE = 2
AI_TX = Pin.P16
AI_RX = Pin.P15

AI_INTERVAL_MS = 450
DIST_INTERVAL_MS = 150
STATE_INTERVAL_MS = 700
UPLOAD_INTERVAL_MS = 1500
HELP_INTERVAL_MS = 1000
BLINK_INTERVAL_MS = 500
ONLINE_INTERVAL_MS = 5000

DIST_FAR = 80
DIST_MID = 45
DIST_NEAR = 20
WIFI_RETRY_MS = 1500

OBSTACLES = {
    "person": ("person", "person ahead"),
    "chair": ("chair", "chair ahead"),
    "dining table": ("table", "table ahead"),
    "table": ("table", "table ahead"),
}

wifi_client = None


def ticks_ms():
    if hasattr(time, "ticks_ms"):
        return time.ticks_ms()
    return int(time.time() * 1000)


def sleep_ms(value):
    if hasattr(time, "sleep_ms"):
        time.sleep_ms(value)
    else:
        time.sleep(value / 1000.0)


def oled_lines(lines):
    oled.fill(0)
    y = 0
    for item in lines:
        oled.DispChar(str(item), 0, y)
        y += 16
    oled.show()


def rgb_fill(color):
    rgb.fill(color)
    rgb.write()


def rgb_off():
    rgb_fill((0, 0, 0))


def http_post(path, payload):
    ensure_wifi()
    gc.collect()
    body = json.dumps(payload)
    res = urequests.post(
        SERVER_BASE_URL + path,
        data=body,
        headers={"Content-Type": "application/json"},
    )
    try:
        try:
            return res.json()
        except Exception:
            return None
    finally:
        res.close()


def http_get(path):
    ensure_wifi()
    gc.collect()
    res = urequests.get(SERVER_BASE_URL + path)
    try:
        return res.json()
    finally:
        res.close()


def distance_text(value):
    if value is None:
        return "--"
    try:
        return "%dcm" % int(value)
    except Exception:
        return str(value)


def beep_interval(distance):
    if distance <= DIST_NEAR:
        return 120
    if distance <= DIST_MID:
        return 260
    return 520


def connect_wifi():
    sta = wifi()
    while True:
        if sta.sta.isconnected():
            ip = sta.sta.ifconfig()[0]
            oled_lines(["WiFi OK", ip])
            return sta
        oled_lines(["WiFi", "connecting", WIFI_SSID])
        try:
            sta.connectWiFi(WIFI_SSID, WIFI_PASSWORD, timeout=10)
            if sta.sta.isconnected():
                ip = sta.sta.ifconfig()[0]
                oled_lines(["WiFi OK", ip])
                return sta
        except Exception as exc:
            print("WIFI_ERR", exc)
            oled_lines(["WiFi retry", WIFI_SSID, "retrying"])
        sleep_ms(WIFI_RETRY_MS)


def ensure_wifi():
    global wifi_client
    if wifi_client is not None and wifi_client.sta.isconnected():
        return wifi_client
    wifi_client = connect_wifi()
    return wifi_client


def init_camera():
    cam = smartcamera.SmartCameraK230(tx=AI_TX, rx=AI_RX)
    cam.model_init(AI_MODE)
    gc.collect()
    return cam


def detect_obstacle(cam):
    try:
        cam.yolo_detect.recognize()
        category = str(getattr(cam.yolo_detect, "category_name", "")).strip().lower()
        if category not in OBSTACLES:
            return None
        item = OBSTACLES[category]
        return {
            "category": item[0],
            "message": item[1],
            "score": getattr(cam.yolo_detect, "max_score", None),
        }
    except Exception as exc:
        print("AI_ERR", exc)
        return None


def post_online(distance_value):
    try:
        http_post(
            "/api/recognition",
            {
                "category": "status",
                "message": "device online",
                "score": 1,
                "distance_cm": distance_text(distance_value),
            },
        )
    except Exception as exc:
        print("POST_ONLINE_ERR", exc)


wifi_client = connect_wifi()
sonic = Ultrasonic()
camera = init_camera()

last_ai_ms = 0
last_dist_ms = 0
last_state_ms = 0
last_upload_ms = 0
last_help_ms = 0
last_blink_ms = 0
last_online_ms = 0
next_beep_ms = 0

last_distance = None
last_detection = None
last_detection_key = ""
help_active = False
help_led_on = False
last_button_a_down = False

rgb_off()
oled_lines(["Blind Cane", "camera ok"])
print("BOOT_OK")
post_online(last_distance)

while True:
    now = ticks_ms()

    button_a_down = button_a.is_pressed()
    if not help_active and (button_a.was_pressed() or (button_a_down and not last_button_a_down)):
        help_active = True
        help_led_on = False
        last_help_ms = 0
        last_blink_ms = 0
    last_button_a_down = button_a_down

    if now - last_dist_ms >= DIST_INTERVAL_MS:
        last_dist_ms = now
        try:
            last_distance = sonic.distance()
        except Exception:
            last_distance = None

    if now - last_ai_ms >= AI_INTERVAL_MS:
        last_ai_ms = now
        result = detect_obstacle(camera)
        if result is not None:
            last_detection = result
            detection_key = result["category"]
            oled_lines(
                [
                    result["message"],
                    "dist=" + distance_text(last_distance),
                    "help=" + ("on" if help_active else "off"),
                ]
            )
            if detection_key != last_detection_key or now - last_upload_ms >= UPLOAD_INTERVAL_MS:
                last_detection_key = detection_key
                last_upload_ms = now
                try:
                    http_post(
                        "/api/recognition",
                        {
                            "category": result["category"],
                            "message": result["message"],
                            "score": result["score"],
                            "distance_cm": distance_text(last_distance),
                        },
                    )
                except Exception as exc:
                    print("POST_RECOG_ERR", exc)
        elif last_detection is None:
            oled_lines(
                [
                    "waiting detect",
                    "dist=" + distance_text(last_distance),
                    "help=" + ("on" if help_active else "off"),
                ]
            )

    if now - last_online_ms >= ONLINE_INTERVAL_MS:
        last_online_ms = now
        post_online(last_distance)

    if last_distance is not None and last_distance <= DIST_FAR and now >= next_beep_ms:
        next_beep_ms = now + beep_interval(last_distance)
        try:
            music.pitch(1600, 40)
        except Exception:
            pass

    if help_active:
        if now - last_blink_ms >= BLINK_INTERVAL_MS:
            last_blink_ms = now
            help_led_on = not help_led_on
            if help_led_on:
                rgb_fill((255, 0, 0))
            else:
                rgb_off()

        if now - last_help_ms >= HELP_INTERVAL_MS:
            last_help_ms = now
            obstacle_name = last_detection["category"] if last_detection else "unknown"
            try:
                reply = http_post(
                    "/api/help",
                    {
                        "message": "Help",
                        "team_id": TEAM_ID,
                        "location": LOCATION,
                        "obstacle": obstacle_name,
                        "distance_cm": distance_text(last_distance),
                    },
                )
                if isinstance(reply, dict) and reply.get("reply") == "0":
                    help_active = False
                    help_led_on = False
                    rgb_off()
                    oled_lines(["Help", "acked", "server=0"])
            except Exception as exc:
                print("POST_HELP_ERR", exc)

    if now - last_state_ms >= STATE_INTERVAL_MS:
        last_state_ms = now
        try:
            state = http_get("/api/state")
            if help_active and state.get("help_reply") == "0":
                help_active = False
                help_led_on = False
                rgb_off()
                oled_lines(["Help", "acked", "server=0"])
        except Exception:
            pass

    gc.collect()
    sleep_ms(40)
