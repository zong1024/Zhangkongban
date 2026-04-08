from machine import UART

from mpy_competition import board


PROBES = (
    (2, 14, 13, 1152000),
    (2, 13, 14, 1152000),
    (1, 14, 13, 1152000),
    (1, 13, 14, 1152000),
    (2, 14, 13, 115200),
    (2, 13, 14, 115200),
)


def send_k210_ping(uart):
    pkt = [0xAA, 0xBB, 0x01, 0x01, 0xFF] + [0] * 8
    pkt.append(sum(pkt) & 0xFF)
    for _ in range(4):
        uart.write(bytes(pkt))
        board.sleep_ms(120)


def show_result(lines):
    board.display.status("AI V4 Probe", lines[:4])


board.pixels.fill((0, 0, 16))
show_result(["running..."])
print("AI_V4_PROBE_START")

found = False
for uart_id, tx_pin, rx_pin, baudrate in PROBES:
    label = "u{} tx{} rx{} {}".format(uart_id, tx_pin, rx_pin, baudrate)
    try:
        uart = UART(
            uart_id,
            baudrate=baudrate,
            tx=tx_pin,
            rx=rx_pin,
            timeout=120,
            timeout_char=20,
            rxbuf=1024,
        )
        try:
            uart.read()
        except Exception:
            pass
        send_k210_ping(uart)
        resp = uart.read()
        print(label, repr(resp))
        if resp:
            found = True
            hex_text = " ".join(["%02X" % b for b in resp[:16]])
            print("HEX", hex_text)
            board.pixels.fill((0, 24, 0))
            show_result([label[:16], "{} bytes".format(len(resp)), hex_text[:16]])
            break
        uart.deinit()
    except Exception as exc:
        print("ERR", label, repr(exc))

if not found:
    board.pixels.fill((24, 0, 0))
    show_result(["no response", "check power", "check tx/rx"])
    print("AI_V4_PROBE_NONE")
