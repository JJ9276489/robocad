import cadquery as cq
from robocad.parts.servo import ServoFrustumMount

def main():
    mount = ServoFrustumMount()
    solid = mount.build()

    out_path = "servo_frustum_mount.stl"
    cq.exporters.export(solid, out_path)
    print(f"Exported {out_path}")



if __name__ == "__main__":
    main()