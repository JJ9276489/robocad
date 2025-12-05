# view_servo_mount.py
from robocad.parts.servo import *

def main():
    mount = ServoMountPlate()
    out_path = 'servo_mount_plate.step'
    mount.export_step(out_path)

if __name__ == "__main__":
    main()
