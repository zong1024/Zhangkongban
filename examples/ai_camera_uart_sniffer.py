from machine import UART

from mpy_competition import board


# AI camera 4.0 is currently wired on P14/P13.
# Older Labplus smartcamera examples usually use UART2 + tx=P14 + rx=P13
# at 2_000_000 baud, so this listener starts there first.
UART_ID = 2
TX_PIN = 14
RX_PIN = 13
BAUDRATE = 2000000


def show(lines):
    board.display.status("AI Sniffer", lines[:4])


def send_legacy_handshake(uart):
    # Old smartcamera modules expose a MicroPython raw-REPL bridge.
    uart.write(bytes([13, 10, 3, 3]))
    board.sleep_ms(180)
    uart.write(bytes([2]))
    board.sleep_ms(120)
    uart.write(bytes([13, 10, 1]))


uart = UART(UART_ID, baudrate=BAUDRATE, tx=TX_PIN, rx=RX_PIN, timeout=80, timeout_char=20)
show(["tx=P14 rx=P13", "baud={}".format(BAUDRATE), "waiting..."])
print("AI sniffer ready on UART{} tx=P{} rx=P{} baud={}".format(UART_ID, TX_PIN, RX_PIN, BAUDRATE))
print("A=legacy handshake, B=AT command")

while True:
    if uart.any():
        data = uart.read()
        if data:
            hex_text = " ".join(["{:02X}".format(b) for b in data[:16]])
            try:
                ascii_text = data.decode("utf-8", "ignore").strip()
            except Exception:
                ascii_text = ""
            print("RAW:", repr(data))
            if ascii_text:
                print("ASCII:", ascii_text)
            print("HEX:", hex_text)
            show(["{} bytes".format(len(data)), ascii_text[:16], hex_text[:16]])
    if board.buttons.was_pressed("a"):
        send_legacy_handshake(uart)
        print("SEND: legacy raw-REPL handshake")
        show(["legacy probe", "baud={}".format(BAUDRATE)])
    if board.buttons.was_pressed("b"):
        uart.write(b"AT\r\n")
        print("SEND: AT")
        show(["sent AT", "baud={}".format(BAUDRATE)])
    board.sleep_ms(50)
