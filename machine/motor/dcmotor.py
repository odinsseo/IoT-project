import RPi.GPIO as GPIO


class DCMotor:
    def __init__(self, pin1, pin2, enable_pin, start_speed=0):
        GPIO.setmode(GPIO.BCM)  # Broadcom pin layout
        GPIO.setup(pin1, GPIO.OUT)
        GPIO.setup(pin2, GPIO.OUT)
        GPIO.setup(enable_pin, GPIO.OUT)
        GPIO.output(pin1, GPIO.LOW)
        GPIO.output(pin2, GPIO.LOW)

        self.speed = start_speed
        self.pin1 = pin1
        self.pin2 = pin2
        self.enable_pin = GPIO.PWM(enable_pin, 1000)
        self.enable_pin.start(self.speed)

    def forward(self, speed):
        assert 0 <= speed <= 100

        self.speed = speed
        self.enable_pin.ChangeDutyCycle(speed)
        GPIO.output(self.pin1, GPIO.HIGH)
        GPIO.output(self.pin2, GPIO.LOW)

    def backwards(self, speed):
        assert 0 <= speed <= 100

        self.speed = speed
        self.enable_pin.ChangeDutyCycle(speed)
        GPIO.output(self.pin1, GPIO.LOW)
        GPIO.output(self.pin2, GPIO.HIGH)

    def stop(self):
        self.enable_pin.ChangeDutyCycle(0)
        GPIO.output(self.pin1, GPIO.LOW)
        GPIO.output(self.pin2, GPIO.LOW)
        self.speed = 0
