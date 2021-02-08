# -----------------------------------------#
# typehints
from typing import List, Tuple
import uuid
from OCC.Core.BRep import BRep_Tool
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeWire, BRepBuilderAPI_Transform
from OCC.Core.BRepExtrema import BRepExtrema_DistShapeShape
from OCC.Core.TopExp import topexp
from OCC.Core.TopoDS import TopoDS_Compound, TopoDS_Edge, TopoDS_Face, TopoDS_Shape
from OCC.Core.gp import gp_Trsf
from OCC.Extend.ShapeFactory import make_edge, make_face

# -----------------------------------------#

from OCC.Extend.TopologyUtils import TopologyExplorer
from OCC.Core.BRepAdaptor import BRepAdaptor_Surface
from OCC.Core.GeomAbs import GeomAbs_Plane, GeomAbs_Cylinder
from .struc_column import StrucColumn
from .struc_plane import StrucPlane
import logging
import uuid
import jsonpickle

log = logging.getLogger("structural-service")


class StrucBuilding:
    def __init__(self, shapes=None, shape=None):
        self.uuid = uuid.uuid4()
        if not isinstance(shapes, list) and shapes is not None:
            shapes = [shapes]
        if shapes is None and shape is not None:
            shapes = [shape]
        self.columns, self.planes = self.extract_col_pls(shapes)
        self.walls, self.plates = self.seperate_walls_plates()
        self.reconnect_walls_with_plates()
        self.reconnect_columns_with_plates()

    def extract_col_pls(self, shapes) -> Tuple[List[StrucColumn], List[StrucPlane]]:
        col = []
        pls = []
        for shape in shapes:
            if type(shape) is not TopoDS_Compound:
                faces = self.get_faces_from_shape(shape)
                _type = "None"
                for face in faces:
                    surf = BRepAdaptor_Surface(face, True)
                    if surf.GetType() == GeomAbs_Cylinder:
                        _type = "Cylinder"
                        break
                    if surf.GetType() == GeomAbs_Plane:
                        _type = "Plane"
                if _type == "Cylinder":
                    col.append(StrucColumn(shape))
                elif _type == "Plane":
                    pls.append(StrucPlane(shape))
        return col, pls

    def reconnect_walls_with_plates(self) -> None:
        move = gp_Trsf()
        for w in self.walls:
            vertices = w.vertices_of_middleface
            connected = False
            for p in self.plates:
                # TODO check if shapes are close or connected before checking each vertice
                # but this take much longer than just checking all vertices
                # Need investigation
                # -------------------------------#
                # _distance = BRepExtrema_DistShapeShape(
                #     w.shape_object, p.shape_object
                # ).Value()
                # _distance = 0
                # if _distance < 0.1:
                # -------------------------------#
                for index, v in enumerate(vertices):
                    _distance = BRepExtrema_DistShapeShape(v, p.shape_object).Value()
                    if _distance < 0.1:
                        connected = True
                        _distance = BRepExtrema_DistShapeShape(v, p.middleface)
                        p_shape1 = _distance.PointOnShape1(1)
                        p_shape2 = _distance.PointOnShape2(1)
                        _distance = _distance.Value()
                        move.SetTranslation(p_shape1, p_shape2)
                        vertices[index] = BRepBuilderAPI_Transform(v, move).Shape()

            if connected:
                # recreate edges of middelface
                edges = self.recreate_edges_from_vertices(vertices)
                # create wire with edges
                wire = self.create_wire_from_edges(edges)
                try:
                    face = make_face(wire)
                    # set modified face in orgin element
                    w.modified_middleface = face
                except Exception as e:
                    log.error(f"error: {e}")

    def reconnect_columns_with_plates(self) -> None:
        for column in self.columns:
            first_vertex = topexp.FirstVertex(column.middle_edge)
            last_vertex = topexp.LastVertex(column.middle_edge)
            m_first_vertex = None
            l_first_vertex = None
            for p in self.plates:
                if m_first_vertex is None:
                    m_first_vertex = self.reconect_vertex_to_plate(first_vertex, p)
                if l_first_vertex is None:
                    l_first_vertex = self.reconect_vertex_to_plate(last_vertex, p)
                # recreate middle_edge
            try:
                if not m_first_vertex:
                    m_first_vertex = first_vertex
                if not l_first_vertex:
                    l_first_vertex = first_vertex
                modified_middle_edge = make_edge(m_first_vertex, l_first_vertex)
                # set modified edge in orgin element
                column.modified_middle_edge = modified_middle_edge
            except Exception as e:
                log.error(f"error: {e}")

    def seperate_walls_plates(self) -> Tuple[List, List]:
        _walls = []
        _plates = []
        for p in self.planes:
            if p.main_orientation == "Z":
                _plates.append(p)
            else:
                _walls.append(p)
        return _walls, _plates

    def export_dict(self) -> dict:
        _dict = dict()
        column_list = []
        plane_list = []
        for column in self.columns:
            column_list.append(column.export())
        for plane in self.planes:
            plane_list.append(plane.export())
        _dict = {
            "uuid": self.uuid,
            "columns": jsonpickle.encode(column_list),
            "planes": jsonpickle.encode(plane_list),
            "unit": "m",
        }
        return _dict

    @staticmethod
    def get_faces_from_shape(shape) -> List[TopoDS_Face]:
        return [i for i in TopologyExplorer(shape).faces()]

    @staticmethod
    def create_wire_from_edges(edges) -> TopoDS_Shape:
        wire = BRepBuilderAPI_MakeWire()
        for edge in edges:
            wire.Add(edge)
        return wire.Shape()

    @staticmethod
    def recreate_edges_from_vertices(vs) -> List[TopoDS_Edge]:
        _edges = []
        for i in range(len(vs)):
            if i == len(vs) - 1:
                edge = make_edge(vs[i], vs[0])
            else:
                edge = make_edge(vs[i], vs[i + 1])
            _edges.append(edge)
        return _edges

    @staticmethod
    def reconect_vertex_to_plate(vertex, p) -> TopoDS_Shape:
        move = gp_Trsf()
        _distance = BRepExtrema_DistShapeShape(vertex, p.shape_object).Value()
        if _distance < 0.1:
            _distance = BRepExtrema_DistShapeShape(vertex, p.middleface)
            p_shape1 = _distance.PointOnShape1(1)
            p_shape2 = _distance.PointOnShape2(1)
            _distance = _distance.Value()
            move.SetTranslation(p_shape1, p_shape2)
            return BRepBuilderAPI_Transform(vertex, move).Shape()
