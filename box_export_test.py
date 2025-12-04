import cadquery as cq

box = cq.Workplane("XY").box(10, 10, 10)
cq.exporters.export(box, "test_box.stl")
print("Exported test_box.stl")