"""CircuitPython Code for the Servo-Based Deployment Actuator"""

import board
import pwmio
import digitalio
from adafruit_motor import servo
from microcontroller import Pin


class ServoMotor:
    ROTATE_CW: str = "CW"
    ROTATE_CCW: str = "CCW"
    ROTATE_STOP: str = "STOP"
    ROTATION_DIRECTIONS: list[str] = [ROTATE_CW, ROTATE_STOP, ROTATE_CCW, ROTATE_STOP]

    def __init__(
        self,
        gpio_pin: Pin,
        duty_cycle: int,
        frequency: int,
        angle_change: int = 20,
        clip: bool = False,
        continuous: bool = True,
        max_throttle: float = 0.1,
        calibrated_stop_throttle: float = 0.0
    ) -> None:
        self.continuous: bool = continuous

        pwm = pwmio.PWMOut(gpio_pin, duty_cycle=duty_cycle, frequency=frequency)
        self.servo = (
            servo.Servo(pwm) if not self.continuous else servo.ContinuousServo(pwm)
        )

        self.angle = 0
        self.angle_change: int = angle_change
        self.clip: bool = clip

        self.throttle: float = 0.0
        self.max_throttle: float = max_throttle

        self.rotation_index: int = 0
        self.direction = ServoMotor.ROTATE_STOP

        self.calibrated_stop_throttle = calibrated_stop_throttle

    def set_angle(self, angle: int):
        self.angle = max(0, min(180, angle)) if self.clip else angle

        try:
            self.servo.angle = self.angle
        except Exception as e:
            print(f"Error: {e}. Angle exceeded but no one cares")

    def set_throttle(self, throttle: float):
        self.throttle = throttle
        self.servo.throttle = throttle

    def rotate_servo(self) -> None:
        if not self.continuous:
            self.set_angle(
                self.angle
                + self.angle_change
                * (1 if self.direction == ServoMotor.ROTATE_CCW else -1)
            )
        else:
            self.set_throttle(
                (
                    self.max_throttle
                    if self.direction == ServoMotor.ROTATE_CCW
                    else -self.max_throttle
                )
            )

    def stop_servo(self):
        if self.continuous:
            self.set_throttle(self.calibrated_stop_throttle)
        else:
            self.set_angle(self.angle)


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
    rotator = ServoMotor(board.GP28, duty_cycle=2**15, frequency=50)

    global actuator
    actuator = ServoMotor(board.GP11, duty_cycle=2**15, frequency=50, max_throttle=0.9, calibrated_stop_throttle=0.09)


def await_button_release(button: digitalInOut) -> None:
    while True:
        if button.value:
            return


def main() -> None:
    global rotator_button, actuator_button
    global rotator, actuator

    while True:
        if not rotator_button.value:
            await_button_release(rotator_button)
            rotator.rotation_index = (rotator.rotation_index + 1) % len(
                ServoMotor.ROTATION_DIRECTIONS
            )
            rotator.direction = ServoMotor.ROTATION_DIRECTIONS[rotator.rotation_index]

        if not actuator_button.value:
            await_button_release(actuator_button)
            actuator.rotation_index = (actuator.rotation_index + 1) % len(
                ServoMotor.ROTATION_DIRECTIONS
            )
            actuator.direction = ServoMotor.ROTATION_DIRECTIONS[actuator.rotation_index]

        if rotator.direction != ServoMotor.ROTATE_STOP:
            rotator.rotate_servo()
        else:
            rotator.stop_servo()

        if actuator.direction != ServoMotor.ROTATE_STOP:
            actuator.rotate_servo()
        else:
            actuator.stop_servo()
        
        # trigger deploy please!!!!


if __name__ == "__main__":
    init()
    main()
