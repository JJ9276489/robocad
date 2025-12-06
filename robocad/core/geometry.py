from typing import Sequence, Tuple, List

Point2D = Tuple[float, float]

# ---- basic lerp ----

def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t

def lerp_point(p0: Point2D, p1: Point2D, t: float) -> Point2D:
    return(
        lerp(p0[0], p1[0], t),
        lerp(p0[1], p1[1], t),
    )

# ---- frustum polygon interpolation ----

def frustum_polygon_at_z(
        z: float,
        height: float,
        base_polygon: Sequence[Point2D],
        top_polygon: Sequence[Point2D],
) -> list[Point2D]:
    '''
    Polygon at height z between base_polygon (z=0)
    and top_polygon (z=height), assuming:
      - polygons are convex
      - same vertex count
      - corresponding vertices are paired
    '''
    if height == 0:
        raise ValueError("height must be non-zero")
    
    if len(base_polygon) != len(top_polygon):
        raise ValueError("base_polygon and top_polygon must have the same number of vertices")
    
    t = z / height
    return [lerp_point(pb, pt, t) for pb, pt in zip(base_polygon, top_polygon)]

# ---- inward offset for convex polygon ----

def _line_intersection():
    pass

def offset_polygon_inward_convex() -> List[Point2D]:
    pass


# ---- frustum inner polygon at z using offset ----
def frustum_inner_polygon_at_z() -> List[Point2D]:
    pass