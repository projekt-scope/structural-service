from struc_elements import struc_building
from struc_elements.struc_building import StrucBuilding
from OCC.Display.WebGl import threejs_renderer
from OCC.Core.BRep import BRep_Tool
from OCC.Core.gp import gp_Ax2, gp_Dir, gp_Pnt, gp_Trsf, gp_OZ
from OCC.Core.TopoDS import TopoDS_Face

from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakeCylinder
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_Transform

from OCC.Extend.ShapeFactory import rotate_shape

import struc_elements


shapes = []

height = 300
number_of_rows = 50
width = 500.0

thinkness = 10.0
plate_1 = BRepPrimAPI_MakeBox(500.0, width, -thinkness).Shape()
# shapes.append(plate_1)
for i in range(0, number_of_rows):
    move = gp_Trsf()
    wall_1 = BRepPrimAPI_MakeBox(thinkness, width, height).Shape()
    move.SetTranslation(gp_Pnt(0, 0, 0), gp_Pnt(0, 0, height * i + thinkness * i))
    wall_1 = BRepBuilderAPI_Transform(wall_1, move).Shape()

    wall_2 = rotate_shape(
        BRepPrimAPI_MakeBox(-thinkness, width, height).Shape(), gp_OZ(), -90
    )
    wall_2 = BRepBuilderAPI_Transform(wall_2, move).Shape()
    plate_2 = BRepPrimAPI_MakeBox(500.0, width, -thinkness).Shape()
    plate_2 = BRepBuilderAPI_Transform(plate_2, move).Shape()
    shapes.append(wall_1)
    shapes.append(wall_2)
    shapes.append(plate_2)
    cylinder_origin = gp_Ax2(gp_Pnt(350.0, 350.0, 0), gp_Dir(0.0, 0.0, 1.0))
    cylinder = BRepPrimAPI_MakeCylinder(cylinder_origin, 20, height).Shape()
    cylinder = BRepBuilderAPI_Transform(cylinder, move).Shape()
    shapes.append(cylinder)


import time

start = time.time()
print("struc")

struc_b = StrucBuilding(shapes)
print(len(struc_b.plates))
print(len(struc_b.walls))
end = time.time()
print(end - start)
# my_renderer = threejs_renderer.ThreejsRenderer()
# for w in struc_b.walls:
#     # print(w.modified_middleface)
#     my_renderer.DisplayShape(w.modified_middleface)
#     #  my_renderer.DisplayShape(w.shape_object)
# for p in struc_b.plates:
#     my_renderer.DisplayShape(p.middleface)
#     # my_renderer.DisplayShape(p.shape_object)

# for c in struc_b.columns:
#     # my_renderer.DisplayShape(c.shape_object)
#     # my_renderer.DisplayShape(c.middle_edge)
#     my_renderer.DisplayShape(c.modified_middle_edge)


# my_renderer.render()


# for 50 it takes about 8.2 seconds without the check in l68 (struc_building)
#  with the check it takes about 39.9 seconds

# 32.66138005256653
