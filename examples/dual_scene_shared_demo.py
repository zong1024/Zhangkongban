from mpy_competition import DualSceneCompetitionApp, build_shared_scene_config


CONFIG = build_shared_scene_config(
    {
        "trash": {
            "distance_trigger_pin": "P8",
            "distance_echo_pin": "P9",
            "fill_trigger_pin": "P1",
            "fill_echo_pin": "P2",
            "servo_pin": "P0",
            "open_threshold_cm": 15,
            "full_threshold_cm": 8,
            "open_hold_ms": 3000,
        },
        "vision": {
            "uart_id": 2,
            "tx_pin": "P14",
            "rx_pin": "P13",
            "baudrate": 2000000,
        },
        "bridge1956": {
            "uart_id": 1,
            "tx_pin": "P16",
            "rx_pin": "P15",
            "baudrate": 115200,
        },
        "guide": {
            "distance_trigger_pin": "P8",
            "distance_echo_pin": "P9",
            "help_flash_ms": 4000,
        },
    }
)


# Button A: help in guide mode
# Button B: switch between trash can and guide stick scenes
app = DualSceneCompetitionApp(CONFIG)
app.run_forever()
