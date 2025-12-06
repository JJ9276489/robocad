# view_servo_mount.py
from robocad.parts.servo import *
from robocad.parts.ultrasonic import *

def main():
    mount = UltrasonicSensorMount()
    out_path = 'ultrasonic_mount.step'
    mount.export_step(out_path)

if __name__ == "__main__":
    main()
