import time

from machine import Pin


def clamp(value, low, high):
    if value < low:
        return low
    if value > high:
        return high
    return value


def normalize_board_pin(pin):
    if isinstance(pin, int):
        return pin
    if isinstance(pin, str):
        token = pin.strip().upper()
        if token.startswith("PIN."):
            token = token.split(".")[-1]
        if token.startswith("P"):
            return int(token[1:])
        return int(token)
    raise TypeError("Unsupported pin: {}".format(pin))


def board_pin_name(pin):
    return "P{}".format(normalize_board_pin(pin))


def machine_pin(pin, mode=None, pull=None):
    board_pin = normalize_board_pin(pin)
    pin_const = getattr(Pin, "P{}".format(board_pin))
    if mode is None and pull is None:
        return Pin(pin_const)
    if pull is None:
        return Pin(pin_const, mode)
    return Pin(pin_const, mode, pull)


def sleep_ms(ms):
    if hasattr(time, "sleep_ms"):
        time.sleep_ms(ms)
    else:
        time.sleep(float(ms) / 1000.0)


def sleep_us(us):
    if hasattr(time, "sleep_us"):
        time.sleep_us(us)
    else:
        time.sleep(float(us) / 1000000.0)


def ticks_ms():
    if hasattr(time, "ticks_ms"):
        return time.ticks_ms()
    return int(time.time() * 1000)
