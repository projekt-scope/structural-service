# -----------------------------------------#
# typehints
from typing import List

from OCC.Core.TopoDS import (
    TopoDS_Edge,
    TopoDS_Face,
    TopoDS_Solid,
    TopoDS_Vertex,
    TopoDS_Wire,
)

# -----------------------------------------#
import uuid

from copy import copy
from OCC.Extend.TopologyUtils import TopologyExplorer
from OCC.Core.GProp import GProp_GProps
from OCC.Core.BRepGProp import brepgprop_SurfaceProperties
from OCC.Core.BRepExtrema import BRepExtrema_DistShapeShape
from OCC.Core.BRepAdaptor import BRepAdaptor_Surface
from OCC.Core.GeomAbs import GeomAbs_Plane
from OCC.Core.TopLoc import TopLoc_Location
from OCC.Core.gp import gp_Pnt, gp_Trsf, gp_Vec
from OCC.Core.BRep import BRep_Tool


class StrucPlane:
    def __init__(self, shape_object):
        self.uuid = uuid.uuid4()
        self.shape_object = shape_object
        self.faces = self.get_faces_from_shape()
        self.biggest_face = self.calculate_biggest_face()
        self.thinkness = self.calculate_thinkness()
        self.middleface = self.calculate_middleface()
        self.modified_middleface = None
        self.main_orientation = self.calculate_main_orientation()
        self.vertices_of_middleface = self.calculate_vertices_of_middleface()

    def export(self) -> dict:
        return {
            "uuid": self.uuid,
            "middleface": self.middleface,
            "modified_middleface": self.modified_middleface,
            "thinkness": self.thinkness,
        }

    def calculate_thinkness(self) -> float:
        thinkness = None
        for face in self.faces:
            _thinkness = self.calculate_distance_face2face(self.biggest_face, face)
            if thinkness is None or _thinkness > thinkness:
                thinkness = _thinkness
        return thinkness

    def calculate_main_orientation(self) -> str:
        _surf = BRepAdaptor_Surface(self.biggest_face, True)
        _normal = _surf.Plane().Axis().Direction()
        _dict = {"X": abs(_normal.X()), "Y": abs(_normal.Y()), "Z": abs(_normal.Z())}
        return max(_dict, key=_dict.get)

    def calculate_middleface(self) -> TopoDS_Face:
        normal_vector = self.get_normal_vector_of_face(self.biggest_face)
        _half_thinkness = self.thinkness / 2
        trsf = gp_Trsf()
        trsf.SetTranslation(
            gp_Vec(
                -normal_vector.X() * _half_thinkness,
                -normal_vector.Y() * _half_thinkness,
                -normal_vector.Z() * _half_thinkness,
            )
        )
        middleface = self.move_biggest_face(trsf)
        if self.check_if_face_inside_shape(middleface) is False:
            trsf = gp_Trsf()
            trsf.SetTranslation(
                gp_Vec(
                    normal_vector.X() * _half_thinkness,
                    normal_vector.Y() * _half_thinkness,
                    normal_vector.Z() * _half_thinkness,
                )
            )
        middleface = self.move_biggest_face(trsf)

        return middleface

    def check_if_face_inside_shape(self, face) -> bool:
        solid = self.get_solid_from_shape(self.shape_object)
        _wire = [i for i in TopologyExplorer(face).wires()]
        ordered_vertices = TopologyExplorer(self.shape_object).ordered_vertices_from_wire(
            _wire[0]
        )
        vert = None
        for v in ordered_vertices:
            vert = v
            break
        inside = self.point_in_solid(
            solid,
            gp_Pnt(
                BRep_Tool.Pnt(vert).X(), BRep_Tool.Pnt(vert).Y(), BRep_Tool.Pnt(vert).Z()
            ),
        )
        return inside

    def move_biggest_face(self, trsf: gp_Trsf) -> TopoDS_Face:
        _face = copy(self.biggest_face)
        _face.Move(TopLoc_Location(trsf))
        return _face

    @staticmethod
    def get_solid_from_shape(shape) -> TopoDS_Solid:
        return [i for i in TopologyExplorer(shape).solids()][0]

    @staticmethod
    def point_in_solid(solid, pnt, tolerance=1e-5) -> bool:
        """returns True if *pnt* lies in *solid*, False if not
        Args:
            solid   TopoDS_Solid
            pnt:    gp_Pnt
        Returns: bool
        """
        from OCC.Core.BRepClass3d import BRepClass3d_SolidClassifier
        from OCC.Core.TopAbs import TopAbs_ON, TopAbs_OUT, TopAbs_IN

        _in_solid = BRepClass3d_SolidClassifier(solid, pnt, tolerance)
        if _in_solid.State() == TopAbs_ON:
            return True
        if _in_solid.State() == TopAbs_OUT:
            return False
        if _in_solid.State() == TopAbs_IN:
            return True

    def calculate_vertices_of_middleface(self) -> List[TopoDS_Vertex]:
        _wire = [i for i in TopologyExplorer(self.middleface).wires()]
        ordered_vertices = TopologyExplorer(self.shape_object).ordered_vertices_from_wire(
            _wire[0]
        )
        _list = []
        for v in ordered_vertices:
            _list.append(v)
        return _list

    def calculate_edges_middleface(self) -> List[TopoDS_Edge]:
        _edges = TopologyExplorer(self.shape_object).edges_from_face(self.middleface)
        _list = []
        for v in _edges:
            _list.append(v)
        return _list

    def calculate_biggest_face(self) -> TopoDS_Face:
        return max(self.faces, key=lambda f: self.get_area_of_face(f))

    def get_faces_from_shape(self):
        return [i for i in TopologyExplorer(self.shape_object).faces()]

    def get_vertices_from_face(self, face: TopoDS_Face):
        wires = self.get_wires_from_face(face)[0]
        return [i for i in TopologyExplorer(face).ordered_vertices_from_wire(wires)]

    @staticmethod
    def calculate_distance_face2face(face_1: TopoDS_Face, face_2: TopoDS_Face) -> float:
        return BRepExtrema_DistShapeShape(face_1, face_2).Value()

    @staticmethod
    def get_wires_from_face(face: TopoDS_Face) -> List[TopoDS_Wire]:
        # TODO check return type, it should be ->  TopoDS_Wire
        return [i for i in TopologyExplorer(face).wires()]

    @staticmethod
    def get_area_of_face(face) -> float:
        prop = GProp_GProps()
        brepgprop_SurfaceProperties(face, prop)
        return prop.Mass()

    @staticmethod
    def get_normal_vector_of_face(face: TopoDS_Face) -> gp_Vec:
        surf = BRepAdaptor_Surface(face, True)
        surf_type = surf.GetType()
        if surf_type == GeomAbs_Plane:
            gp_pln = surf.Plane()
            normal = gp_pln.Axis().Direction()
            return normal

