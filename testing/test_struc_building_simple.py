from struc_elements.struc_building import StrucBuilding
from OCC.Core.gp import gp_Ax2, gp_Dir, gp_Pnt, gp_Trsf, gp_OZ

from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakeCylinder
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_Transform
from OCC.Core.BRepExtrema import BRepExtrema_DistShapeShape

from OCC.Extend.ShapeFactory import rotate_shape

import struc_elements

wall_1 = BRepPrimAPI_MakeBox(10.0, 500.0, 300.0).Shape()
wall_2 = rotate_shape(BRepPrimAPI_MakeBox(-10.0, 500.0, 300.0).Shape(), gp_OZ(), -90)
plate_1 = BRepPrimAPI_MakeBox(500.0, 500.0, -10.0).Shape()
plate_2 = BRepPrimAPI_MakeBox(500.0, 500.0, -10.0).Shape()
move = gp_Trsf()
move.SetTranslation(gp_Pnt(0, 0, 0), gp_Pnt(0, 0, 310))
plate_2 = BRepBuilderAPI_Transform(plate_2, move).Shape()
cylinder_origin = gp_Ax2(gp_Pnt(150.0, 150.0, 0), gp_Dir(0.0, 0.0, 1.0))
cylinder = BRepPrimAPI_MakeCylinder(cylinder_origin, 20, 300).Shape()
shapes = []
shapes.extend((wall_1, wall_2, plate_1, plate_2, cylinder))

struc_b = StrucBuilding(shapes)


def test_count():
    assert len(struc_b.plates) == 2
    assert len(struc_b.walls) == 2
    assert len(struc_b.columns) == 1


def test_thinkness():
    for w in struc_b.walls:
        assert w.thinkness == 10.0
    for p in struc_b.plates:
        assert p.thinkness == 10.0


def test_walls_orientation():
    for w in struc_b.walls:
        assert w.main_orientation != "Z"
    for p in struc_b.plates:
        assert p.main_orientation == "Z"


def test_uuid():
    assert struc_b.uuid != ""


def test_reconnection():
    # if a wall (shape) is connected to a plate the middlefaces should be connected also
    for w in struc_b.walls:
        for p in struc_b.plates:
            _distance = BRepExtrema_DistShapeShape(w.shape_object, p.shape_object).Value()
            if _distance < 0.1:
                assert w.modified_middleface is not None
                faces_distance = BRepExtrema_DistShapeShape(
                    w.modified_middleface, p.middleface
                ).Value()
                assert faces_distance == 0.0

    # if a column (shape) is connected to a plate the middleedge should be connected also
    for c in struc_b.columns:
        for p in struc_b.plates:
            _distance = BRepExtrema_DistShapeShape(c.shape_object, p.shape_object).Value()
            if _distance < 0.1:
                assert c.modified_middle_edge is not None
                faces_distance = BRepExtrema_DistShapeShape(
                    c.modified_middle_edge, p.middleface
                ).Value()
                assert faces_distance == 0.0
