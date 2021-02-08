from OCC.Extend.TopologyUtils import TopologyExplorer

from OCC.Core.gp import gp_Ax2, gp_Pnt, gp_Dir

from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeCylinder
from OCC.Core.gp import gp_Pnt, gp_Ax2, gp_Dir

from OCC.Core.BRep import BRep_Tool

import struc_elements


cylinder_origin = gp_Ax2(gp_Pnt(0.0, 0.0, 0.0), gp_Dir(0.0, 0.0, 1.0))
cylinder = BRepPrimAPI_MakeCylinder(cylinder_origin, 2, 10).Shape()
struc = struc_elements.StrucColumn(cylinder)


def test_radius():
    assert struc.radius == 2.0


def test_uuid():
    assert struc.uuid != ""


def test_vertices_of_middle_edge():
    assert struc.middle_edge.IsNull() is False
    edge = struc.middle_edge
    real_v1 = gp_Pnt(0, 0, 10)
    real_v2 = gp_Pnt(0, 0, 0)
    vertices = []
    for i in TopologyExplorer(edge).vertices_from_edge(edge):
        vertices.append(i)
    v1 = BRep_Tool.Pnt(vertices[0])
    v2 = BRep_Tool.Pnt(vertices[1])

    assert v1.IsEqual(real_v1, 0.001) is True
    assert v2.IsEqual(real_v2, 0.001) is True
