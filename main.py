import logging

from typing import Optional
from fastapi import FastAPI, File, UploadFile
from pydantic import BaseModel

import jsonpickle

from OCC.Extend.DataExchange import read_step_file, read_step_file_with_names_colors
from struc_elements import StrucBuilding, StrucColumn, StrucPlane


# ----------- for Upload files---------------------------#
import shutil
from pathlib import Path
from tempfile import NamedTemporaryFile

# ----------- for Upload files---------------------------#

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger("structural-service")

log.info(
    """

░██████╗░█████╗░░█████╗░██████╗░███████╗
██╔════╝██╔══██╗██╔══██╗██╔══██╗██╔════╝
╚█████╗░██║░░╚═╝██║░░██║██████╔╝█████╗░░
░╚═══██╗██║░░██╗██║░░██║██╔═══╝░██╔══╝░░
██████╔╝╚█████╔╝╚█████╔╝██║░░░░░███████╗
╚═════╝░░╚════╝░░╚════╝░╚═╝░░░░░╚══════╝
█                                       █
█  https://www.projekt-scope.de/        █
█        structual-service              █
    """
)


app = FastAPI(
    title="Structural Service",
    description="This API create geometry objects for structural software.",
    version="0.1",
)


class Shape(BaseModel):
    shape_json: str
    format: Optional[str] = None


class Building(BaseModel):
    shapes_json: str
    format: Optional[str] = None


def save_upload_file_tmp(upload_file: UploadFile) -> Path:
    try:
        suffix = Path(upload_file.filename).suffix
        with NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            shutil.copyfileobj(upload_file.file, tmp)
            tmp_path = Path(tmp.name)
    finally:
        upload_file.file.close()
    return tmp_path


@app.post("/simplification/building/")
async def simplification_building(building: Building):
    if building.format == "jsonpickle":
        encoded_shapes = jsonpickle.decode(building.shapes_json)
        struc = StrucBuilding(encoded_shapes)
        return jsonpickle.encode(struc.export_dict())


@app.post("/simplification/building/stp")
async def simplification_building_stp(file: Optional[UploadFile] = File(None)):
    tmp_path = save_upload_file_tmp(file)
    _shapes = read_step_file_with_names_colors(str(tmp_path))
    shapes = []
    for n in _shapes:
        shapes.append(n)
    shapes = shapes[1:]  # skip first Compound object
    struc = StrucBuilding(shapes)
    return struc.export_dict()


@app.post("/simplification/column/")
async def simplification_column(shape: Shape):
    if shape.format == "jsonpickle":
        encoded_shape = jsonpickle.decode(shape.shape_json)
        struc = StrucColumn(encoded_shape)

        return struc.radius


@app.post("/simplification/column/file")
async def simplification_column_file(shape_file: Optional[UploadFile] = File(None)):
    tmp_path = save_upload_file_tmp(shape_file)
    try:
        encoded_shape = read_step_file(str(tmp_path))
        struc = StrucColumn(encoded_shape)
    finally:
        tmp_path.unlink()  # Delete the temp file
    return struc.radius


@app.post("/simplification/plane/")
async def simplification_plane(shape: Shape):
    if shape.format == "jsonpickle":
        encoded_shape = jsonpickle.decode(shape.shape_json)
        struc = StrucPlane(encoded_shape)
        log.debug(struc.middleface)


@app.post("/extraction/")
async def extraction(shape: Shape):
    # TODO
    return {"item_id": shape.name, "pickle": shape.jsonpickle}
