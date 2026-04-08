from machine import UART

from mpy_competition import board


UART_ID = 2
TX_PIN = 14
RX_PIN = 13
LEGACY_BAUDRATE = 2000000
TEXT_BAUDRATE = 115200


def read_as_text(data):
    try:
        return data.decode("utf-8", "ignore").strip()
    except Exception:
        return ""


def probe_legacy():
    board.display.status("AI Probe", ["legacy probe", "UART2 P14/P13"])
    uart = UART(
        UART_ID,
        baudrate=LEGACY_BAUDRATE,
        tx=TX_PIN,
        rx=RX_PIN,
        timeout=120,
        timeout_char=20,
        rxbuf=4096,
    )
    board.sleep_ms(100)
    try:
        uart.read()
    except Exception:
        pass
    uart.write(bytes([13, 10, 3, 3]))
    board.sleep_ms(180)
    part1 = uart.read() or b""
    if not part1:
        uart.write(bytes([2]))
        board.sleep_ms(120)
        part1 = uart.read() or b""
    uart.write(bytes([13, 10, 1]))
    board.sleep_ms(260)
    part2 = uart.read() or b""
    uart.deinit()
    return part1 + part2


def probe_text():
    board.display.status("AI Probe", ["text probe", "UART2 115200"])
    uart = UART(UART_ID, baudrate=TEXT_BAUDRATE, tx=TX_PIN, rx=RX_PIN, timeout=120, timeout_char=20)
    board.sleep_ms(80)
    try:
        pre = uart.read()
        if pre:
            uart.deinit()
            return ("pre", pre)
    except Exception:
        pass
    for payload in (b"AT\r\n", b"\r\n"):
        uart.write(payload)
        board.sleep_ms(180)
        data = uart.read()
        if data:
            uart.deinit()
            return (payload, data)
    uart.deinit()
    return None


board.display.status("AI Probe", ["P14/P13", "running..."])
board.pixels.fill((0, 0, 24))
print("Probe start on UART{} tx=P{} rx=P{}".format(UART_ID, TX_PIN, RX_PIN))

legacy_data = probe_legacy()
if legacy_data:
    ascii_text = read_as_text(legacy_data)
    print("FOUND legacy", repr(legacy_data))
    board.pixels.fill((0, 24, 0))
    board.display.status(
        "AI Found",
        ["legacy 2M", ascii_text[:16], str(len(legacy_data)) + " bytes"],
    )
else:
    print("NO_RESPONSE legacy raw-REPL on UART2 P14/P13")
    text_result = probe_text()
    if text_result:
        payload, data = text_result
        ascii_text = read_as_text(data)
        print("FOUND text", repr(payload), repr(data))
        board.pixels.fill((0, 24, 0))
        board.display.status(
            "AI Found",
            ["115200 text", ascii_text[:16], str(len(data)) + " bytes"],
        )
    else:
        board.pixels.fill((24, 0, 0))
        board.display.status("AI Probe", ["P14/P13", "no response"])
        print("No response on P14/P13 for legacy raw-REPL or 115200 text probe.")
