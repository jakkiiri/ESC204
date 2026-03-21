"""CircuitPython Code for the Servo-Based Deployment Actuator"""

import time
import board
import pwmio
import digitalio
from adafruit_motor import servo


class ServoMotor:
    # ROTATE_CW: str = "CW"
    # ROTATE_CCW: str = "CCW"
    # ROTATION_DIRECTIONS: list[str] = [ROTATE_CW, ROTATE_CCW]

    def __init__(
        self,
        gpio_pin: Pin,
        duty_cycle: int,
        frequency: int,
        angle_change: int = 20,
        clip: bool = False,
        continuous: bool = True,
    ) -> None:
        self.continuous: bool = continuous
        pwm = pwmio.PWMOut(gpio_pin, duty_cycle=duty_cycle, frequency=frequency)
        self.servo = (
            servo.Servo(pwm) if not self.continuous else servo.ContinuousServo(pwm)
        )
        self.angle = 0
        self.direction_ccw: bool = True
        self.clip: bool = clip
        self.angle_change: int = angle_change
        self.throttle: int = 0
        # self.rotation_index: int = 0

    def set_angle(self, angle):
        self.angle = angle
        try:
            self.servo.angle = angle
        except Exception as e:
            print(e)

        if self.clip:
            self.angle = max(0, min(180, angle))
            self.servo.angle = self.angle

    def set_throttle(self, throttle):
        self.throttle = throttle
        self.servo.throttle = throttle


def init() -> None:
    # Initiate Objects for the Servos and the Buttons

    # Buttons
    global rotator_button
    rotator_button = digitalio.DigitalInOut(board.GP22)
    rotator_button.direction = digitalio.Direction.INPUT
    rotator_button.pull = digitalio.Pull.UP

    global actuator_button
    actuator_button = digitalio.DigitalInOut(board.GP19)
    actuator_button.direction = digitalio.Direction.INPUT
    actuator_button.pull = digitalio.Pull.UP

    # Servos
    global rotator
    rotator = ServoMotor(board.GP28, duty_cycle=2**15, frequency=50, angle_change=20)

    global actuator
    actuator = ServoMotor(board.GP11, duty_cycle=2**15, frequency=50, angle_change=5)


def await_button_release(button: digitalInOut) -> None:
    while True:
        if button.value:
            return


def rotate_servo(servo: ServoMotor, button: digitalInOut) -> None:
    while True:
        print(servo.angle)
        if not servo.continuous:
            servo.set_angle(
                servo.angle + servo.angle_change * (1 if servo.direction_ccw else -1)
            )
        else:
            servo.set_throttle((0.1 if servo.direction_ccw else -0.1))
        # time.sleep(0.05)

        # button pressed again
        if not button.value:
            await_button_release(button)
            servo.direction_ccw = not servo.direction_ccw
            if servo.continuous:
                servo.set_throttle(0)
            return


def main() -> None:
    global rotator_button, actuator_button
    global rotator, actuator

    while True:
        if not rotator_button.value:
            await_button_release(rotator_button)
            rotate_servo(rotator, rotator_button)

        if not actuator_button.value:
            await_button_release(actuator_button)
            rotate_servo(actuator, actuator_button)

            # rotator.rotation_index = (rotator.rotation_index + 1) % len(ServoMotor.ROTATION_DIRECTIONS)
            # rotator.direction = ServoMotor.ROTATION_DIRECTIONS[rotator.rotation_index]


if __name__ == "__main__":
    init()
    main()
