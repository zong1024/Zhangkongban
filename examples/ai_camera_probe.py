from mpy_competition import board, probe_ai_camera


TX_PIN = "P16"
RX_PIN = "P15"
UART_ID = 1


board.display.status("AI Probe", ["probing...", "tx={} rx={}".format(TX_PIN, RX_PIN)])
board.pixels.fill((0, 0, 24))

result = probe_ai_camera(tx_pin=TX_PIN, rx_pin=RX_PIN, uart_id=UART_ID)

if result["camera"] is not None:
    board.pixels.fill((0, 24, 0))
    lines = [
        result["protocol"],
        "baud={}".format(result["baudrate"]),
        "tx={} rx={}".format(result["tx_pin"], result["rx_pin"]),
    ]
    board.display.status("AI Found", lines)
    print("AI camera detected:", result["protocol"], result["baudrate"])
else:
    board.pixels.fill((24, 0, 0))
    lines = [
        "check power",
        "tx={} rx={}".format(result["tx_pin"], result["rx_pin"]),
    ]
    board.display.status("AI Failed", lines)
    print("AI camera probe failed:", result.get("error"))
    print(result.get("hint"))
