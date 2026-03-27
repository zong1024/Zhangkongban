from mpy_competition import (
    DHTSensor,
    InfraredObstacleSensor,
    LocalHttpClient,
    PirSensor,
    SerialVisionCamera,
    ServoMotor,
    UltrasonicHCSR04,
    board,
)


board.display.status("G4 Ready", ["board init ok"])
board.pixels.status(ok=True)
board.buzzer.beep(1200, 80)

pir = PirSensor("P0")
ir_obstacle = InfraredObstacleSensor("P1", active_low=True)
ultrasonic = UltrasonicHCSR04("P13", "P14")
temp_humi = DHTSensor("P15", model="dht11")
servo = ServoMotor("P16")

# Update these pins and baudrate for your own AI camera wiring.
camera = SerialVisionCamera(uart_id=1, baudrate=115200, tx_pin="P8", rx_pin="P9")

# Use a local AP or LAN server only.
server = LocalHttpClient("http://192.168.4.1:8000")


def show_status():
    distance_cm = ultrasonic.read_cm(samples=3)
    env = temp_humi.read()
    body = [
        "pir={}".format(int(pir.read())),
        "obs={}".format(int(ir_obstacle.read())),
        "dis={:.1f}cm".format(distance_cm),
        "tmp={}C hum={}pct".format(env["temperature"], env["humidity"]),
    ]
    board.display.status("G4 Runtime", body)


while True:
    show_status()

    if pir.read():
        servo.write_angle(90)
        board.pixels.fill((0, 16, 32))
    elif ir_obstacle.read():
        servo.write_angle(20)
        board.pixels.fill((32, 16, 0))
    else:
        servo.write_angle(0)
        board.pixels.fill((0, 16, 0))

    if board.buttons.was_pressed("a"):
        try:
            payload = server.post_json(
                "/telemetry",
                {
                    "distance_cm": ultrasonic.read_cm(samples=2),
                    "pir": pir.read(),
                    "obstacle": ir_obstacle.read(),
                },
            )
            board.display.status("HTTP OK", [str(payload)])
        except Exception as exc:
            board.display.status("HTTP ERR", [str(exc)])

    if board.buttons.was_pressed("b"):
        try:
            result = camera.request_json("detect")
            board.display.status("AI Camera", [str(result)])
        except Exception as exc:
            board.display.status("AI ERR", [str(exc)])

    board.sleep_ms(150)
