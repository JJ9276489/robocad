# view_servo_mount.py
from robocad.parts.servo import *

def main():
    mount = ServoFrustumMount()
    out_path = 'servo_frustum_mount.step'
    mount.export_step(out_path)

if __name__ == "__main__":
    main()
