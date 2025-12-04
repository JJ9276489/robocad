# view_servo_mount.py
from time import perf_counter

import cadquery as cq
from robocad.parts.servo import ServoMountPlate


def main():
    t0 = perf_counter()
    print("Step 1: building...")
    mount = ServoMountPlate()
    solid = mount.build()
    t1 = perf_counter()
    print(f"  ✔ build() finished in {t1 - t0:.2f} s")

    out_path = "servo_mount_plate.stl"
    print(f"Step 2: exporting to {out_path} ...")
    cq.exporters.export(solid, out_path)
    t2 = perf_counter()
    print(f"  ✔ export finished in {t2 - t1:.2f} s")
    print("Done.")


if __name__ == "__main__":
    main()
