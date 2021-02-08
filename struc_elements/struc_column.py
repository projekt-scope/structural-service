# -----------------------------------------#
# typehints
from typing import List

from OCC.Core.TopoDS import TopoDS_Face, TopoDS_Shape
from OCC.Core.gp import gp_Cylinder

# -----------------------------------------#


from OCC.Extend.TopologyUtils import TopologyExplorer
from OCC.Core.BRepAdaptor import BRepAdaptor_Surface
from OCC.Core.GeomAbs import GeomAbs_Plane, GeomAbs_Cylinder
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeEdge
import uuid


class StrucColumn:
    def __init__(self, shape_object):
        self.uuid = uuid.uuid4()
        self.shape_object = shape_object
        self.faces = self.get_faces_from_shape()
        self.planes = self.get_planes_from_shape()
        self.modified_middle_edge = None

    @property
    def radius(self) -> float:
        return self.get_cylinder_from_shape().Radius()

    @property
    def middle_edge(self) -> TopoDS_Shape:
        if len(self.planes) >= 2:
            edge = BRepBuilderAPI_MakeEdge(
                self.planes[0].Location(), self.planes[1].Location()
            )
            edge.Build()
            return edge.Shape()
        return None

    def export(self) -> dict:
        return {
            "uuid": self.uuid,
            "edge": self.middle_edge,
            "modified_middle_edge": self.modified_middle_edge,
            "radius": self.radius,
        }

    def get_faces_from_shape(self) -> List[TopoDS_Face]:
        return [i for i in TopologyExplorer(self.shape_object).faces()]

    def get_planes_from_shape(self) -> List[TopoDS_Face]:
        liste = []
        for face in self.faces:
            surf = BRepAdaptor_Surface(face, True)
            if surf.GetType() == GeomAbs_Plane:
                gp_pln = surf.Plane()
                liste.append(gp_pln)
        return liste

    def get_cylinder_from_shape(self) -> gp_Cylinder:
        for face in self.faces:
            surf = BRepAdaptor_Surface(face, True)
            surf_type = surf.GetType()
            if surf_type == GeomAbs_Cylinder:
                gp_cyl = surf.Cylinder()
                return gp_cyl

