# mPython G4 Framework

This repo contains a small MicroPython framework for mPython, mPython board,
and Ledong controller projects.

It is designed for the Shenzhen Creative Maker G4 workflow:

- onboard display, RGB, buttons, touch, light, sound, motion, buzzer, Wi-Fi
- common G4 sensors and actuators
- local LAN / AP IoT access only
- serial bridge for external AI camera modules

## Files

- `mpy_competition/board.py`: onboard board wrapper
- `mpy_competition/ai_camera.py`: official AI camera compatibility layer
- `mpy_competition/sensors.py`: sensor and actuator wrappers
- `mpy_competition/iot.py`: local HTTP and MQTT clients
- `examples/quick_start.py`: sample project
- `examples/ai_camera_probe.py`: AI camera protocol probe

## Copy to board

1. Open mPython.
2. Connect your board and switch the target board to the correct controller.
3. Copy the whole `mpy_competition` folder to the board file system.
4. Copy `examples/quick_start.py` as a new script, then change pin mapping for
   your own hardware.

## Quick usage

```python
from mpy_competition import board, PirSensor, ServoMotor

pir = PirSensor("P0")
servo = ServoMotor("P16")

board.display.status("Boot", ["ready"])

while True:
    if pir.read():
        servo.write_angle(90)
        board.pixels.fill((0, 32, 0))
    else:
        servo.write_angle(0)
        board.pixels.off()
    board.sleep_ms(100)
```

## Onboard wrapper

```python
from mpy_competition import board

board.display.status("Hello", ["mPython ready"])
board.pixels.fill((0, 0, 24))
board.buzzer.beep(1200, 100)

print(board.motion.light())
print(board.motion.sound())
print(board.motion.acceleration())
print(board.buttons.is_pressed("a"))
print(board.touch.read("p"))
```

## G4 sensor map

The framework includes wrappers for the G4 competition categories mentioned in
the notice:

- development board / onboard resources: `board`
- network module / onboard Wi-Fi: `board.wifi`
- PIR: `PirSensor`
- ultrasonic: `UltrasonicHCSR04` and `I2CUltrasonicSensor`
- infrared obstacle sensor: `InfraredObstacleSensor`
- servo: `ServoMotor`
- temperature sensor: `Ds18b20TemperatureSensor`, `DHTSensor`,
  `AnalogTemperatureSensor`
- visual AI camera: `SerialVisionCamera`
- self-built IoT server: `LocalHttpClient`, `LocalMqttClient`

## Official AI camera support

This repo now vendors the official mPython AI camera drivers from your local
installation:

- `mpy_competition/vendor/MuVisionSensor.py`
- `mpy_competition/vendor/MuVisionSensor3AT.py`

Use the unified wrapper in `mpy_competition/ai_camera.py`.

```python
from mpy_competition import build_ai_camera

camera = build_ai_camera(protocol="auto")
target = camera.read_target("body")
print(target)
```

The probe uses the same default wiring that appears in the built-in mPython AI
camera examples:

- TX: `P16`
- RX: `P15`

If MuVision probing fails, keep one more legacy fallback in mind. The older
`AIcamera.zip` package bundled with mPython points to a REPL-style SmartCamera
setup that uses:

- TX: `P14`
- RX: `P13`
- baudrate: `2000000`

Run the probe example first if you are not sure which protocol your camera uses:

```python
from mpy_competition import probe_ai_camera

result = probe_ai_camera(tx_pin="P16", rx_pin="P15", uart_id=1)
print(result)
```

## Notes

- `InfraredObstacleSensor` defaults to `active_low=True` because many common
  obstacle modules pull low on detection. If your module behaves the opposite
  way, set `active_low=False`.
- For ultrasonic modules, use `UltrasonicHCSR04` when you have separate
  trigger / echo pins. Use `I2CUltrasonicSensor` for I2C modules and fill in
  the address / command that matches your hardware.
- `SerialVisionCamera` expects a simple serial text or JSON protocol. Keep the
  AI camera side fixed and only change the command or parser on one side.
- `probe_ai_camera()` currently probes the two official MuVision UART protocol
  families first. If it still fails, the camera may be a legacy REPL-style
  SmartCamera, or the TX/RX wiring may be reversed.
- The sample IoT clients are intended for local servers inside your local AP or
  classroom LAN, not public cloud services.
