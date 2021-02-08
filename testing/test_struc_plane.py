from OCC.Display.WebGl import threejs_renderer
from OCC.Core.BRep import BRep_Tool
from OCC.Core.gp import gp_Pnt, gp_Trsf, gp_OZ
from OCC.Core.TopoDS import TopoDS_Face
from OCC.Extend.TopologyUtils import TopologyExplorer

from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeBox
from OCC.Core.BRepAlgoAPI import BRepAlgoAPI_Cut
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_Transform


from OCC.Extend.ShapeFactory import rotate_shape

import struc_elements

# example wall with dx, dy,dz
# 10 cm thinkness, 500cm length, 300 cm height
wall_1 = BRepPrimAPI_MakeBox(10.0, 500.0, 300.0).Shape()
wall_2 = rotate_shape(BRepPrimAPI_MakeBox(10.0, 500.0, 300.0).Shape(), gp_OZ(), 90)


# example wall with dx, dy,dz and hole
wall_3_with_hole = BRepPrimAPI_MakeBox(10.0, 500.0, 300.0).Shape()
_hole = BRepPrimAPI_MakeBox(100.0, 100.0, 100.0)
_move = gp_Trsf()
_move.SetTranslation(gp_Pnt(0, 0, 0), gp_Pnt(0, 200, 100))
_outline = BRepBuilderAPI_Transform(_hole.Shape(), _move, False).Shape()

wall_3_with_hole = BRepAlgoAPI_Cut(wall_3_with_hole, _outline).Shape()

struc_1 = struc_elements.StrucPlane(wall_1)
struc_2 = struc_elements.StrucPlane(wall_2)
struc_3 = struc_elements.StrucPlane(wall_3_with_hole)


def test_walls_thinkness():
    assert struc_1.thinkness == 10.0
    assert struc_2.thinkness == 10.0
    assert struc_3.thinkness == 10.0


def test_walls_orientation():
    assert struc_1.main_orientation != "Z"
    assert struc_2.main_orientation != "Z"
    assert struc_2.main_orientation != "Z"


def test_uuid():
    assert struc_1.uuid != ""
    assert struc_2.uuid != ""
    assert struc_3.uuid != ""


def test_walls_middleface():
    # wall 1
    vertices = []
    for i in TopologyExplorer(struc_1.middleface).vertices_from_face(struc_1.middleface):
        vertices.append(i)
        # print(
        #     str(BRep_Tool.Pnt(i).X())
        #     + ","
        #     + str(BRep_Tool.Pnt(i).Y())
        #     + ","
        #     + str(BRep_Tool.Pnt(i).Z())
        # )

    p1 = gp_Pnt(5, 0, 300)
    p2 = gp_Pnt(5, 0, 0)
    p3 = gp_Pnt(5, 500, 300)
    p4 = gp_Pnt(5, 500, 0)
    pnt_array = []
    pnt_array.extend((p1, p2, p3, p4))

    for i in range(len(vertices)):
        assert BRep_Tool.Pnt(vertices[i]).IsEqual(pnt_array[i], 0.001) is True
    # wall 2
    vertices = []
    for i in TopologyExplorer(struc_2.middleface).vertices_from_face(struc_2.middleface):
        vertices.append(i)

    p1 = gp_Pnt(0, 5.0, 300)
    p2 = gp_Pnt(0, 5, 0.0)
    p3 = gp_Pnt(-500, 5.0, 300)
    p4 = gp_Pnt(-500, 5, 0)
    pnt_array = []
    pnt_array.extend((p1, p2, p3, p4))

    for i in range(len(vertices)):
        assert BRep_Tool.Pnt(vertices[i]).IsEqual(pnt_array[i], 0.001) is True

    assert isinstance(struc_1.middleface, TopoDS_Face), (
        "need a TopoDS_Face, got a %s" % struc_1.middleface.__class__
    )
    assert isinstance(struc_2.middleface, TopoDS_Face), (
        "need a TopoDS_Face, got a %s" % struc_2.middleface.__class__
    )
    assert not struc_1.middleface.IsNull()
    assert not struc_2.middleface.IsNull()


#   wall_3_with_hole
#   (x,y,z)
#   (5,0,300)                                                        (5,500,300)
#   ////////////////////////////////////////////////////////////////////////////
#   ////////////////////////////////////////////////////////////////////////////
#   ////////////////////////////////////////////////////////////////////////////
#   ////////////////////////////////////////////////////////////////////////////
#   ////////////////////////////////////////////////////////////////////////////
#   //////////////////////////////.(5,200,200)//?%(5,300,200)///////////////////
#   //////////////////////////////.              %//////////////////////////////
#   //////////////////////////////.              %//////////////////////////////
#   //////////////////////////////.              %//////////////////////////////
#   //////////////////////////////.              %//////////////////////////////
#   //////////////////////////////.              %//////////////////////////////
#   //////////////////////////////.              %//////////////////////////////
#   //////////////////////////////.(5,200,100)///%(5,300,100)///////////////////
#   ////////////////////////////////////////////////////////////////////////////
#   ////////////////////////////////////////////////////////////////////////////
#   ////////////////////////////////////////////////////////////////////////////
#   ////////////////////////////////////////////////////////////////////////////
#   ////////////////////////////////////////////////////////////////////////////
#   (5,0,0)                                                            (5,500,0)
def test_wall_middleface_with_hole():

    vertices = []
    for i in TopologyExplorer(struc_3.middleface).vertices_from_face(struc_3.middleface):
        vertices.append(i)
        # print(
        #     str(BRep_Tool.Pnt(i).X())
        #     + ","
        #     + str(BRep_Tool.Pnt(i).Y())
        #     + ","
        #     + str(BRep_Tool.Pnt(i).Z())
        # )

    p1 = gp_Pnt(5.0, 0.0, 300.0)
    p2 = gp_Pnt(5.0, 0.0, 0.0)
    p3 = gp_Pnt(5.0, 500.0, 300.0)
    p4 = gp_Pnt(5.0, 500.0, 0.0)
    p5 = gp_Pnt(5.0, 200.0, 200.0)
    p6 = gp_Pnt(5.0, 200.0, 100.0)
    p7 = gp_Pnt(5.0, 300.0, 100.0)
    p8 = gp_Pnt(5.0, 300.0, 200.0)
    pnt_array = []
    pnt_array.extend((p1, p2, p3, p4, p5, p6, p7, p8))

    for i in range(len(vertices)):
        assert BRep_Tool.Pnt(vertices[i]).IsEqual(pnt_array[i], 0.001) is True

    assert isinstance(struc_3.middleface, TopoDS_Face), (
        "need a TopoDS_Face, got a %s" % struc_3.middleface.__class__
    )

    assert not struc_3.middleface.IsNull()


# -------------------------------------plates---------------------------------------------#

plate_1 = BRepPrimAPI_MakeBox(300.0, 300.0, 10.0).Shape()

struc_plate_1 = struc_elements.StrucPlane(plate_1)


def test_plates_thinkness():
    assert struc_plate_1.thinkness == 10.0


def test_plates_orientation():
    assert struc_plate_1.main_orientation == "Z"


def test_plates_middleface():
    vertices = []
    for i in TopologyExplorer(struc_plate_1.middleface).vertices_from_face(
        struc_plate_1.middleface
    ):
        vertices.append(i)

    p1 = gp_Pnt(0.0, 300.0, 5.0)
    p2 = gp_Pnt(0.0, 0.0, 5.0)
    p3 = gp_Pnt(300.0, 300.0, 5.0)
    p4 = gp_Pnt(300.0, 0.0, 5.0)
    pnt_array = []
    pnt_array.extend((p1, p2, p3, p4))

    for i in range(len(vertices)):
        assert BRep_Tool.Pnt(vertices[i]).IsEqual(pnt_array[i], 0.001) is True

    assert isinstance(struc_plate_1.middleface, TopoDS_Face), (
        "need a TopoDS_Face, got a %s" % struc_plate_1.middleface.__class__
    )

    assert not struc_3.middleface.IsNull()

    # my_renderer = threejs_renderer.ThreejsRenderer()
    # my_renderer.DisplayShape(wall_3_with_hole)
    # my_renderer.DisplayShape(struc_3.middleface)
    # # then call the renderer
    # my_renderer.render()
