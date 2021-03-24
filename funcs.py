import xc_base
import geom
import xc

from materials.sections import section_properties
from materials import typical_materials as tm
from materials.astm_aisc import ASTM_materials


def create_lines(
    p1,
    p2,
    n: int,
    points,
    lines,
    point_id,
    )-> list:
    x1, y1, z1 = p1.getPos.x, p1.getPos.y, p1.getPos.z
    x2, y2, z2 = p2.getPos.x, p2.getPos.y, p2.getPos.z
    dx = (x2 - x1) / n
    dy = (y2 - y1) / n
    dz = (z2 - z1) / n
    
    first_point = p1
    last_point = p1
    new_lines = []
    for i in range(n):
        x = first_point.getPos.x + dx
        y = first_point.getPos.y + dy
        z = first_point.getPos.z + dz
        if all([
            f"{x:.1f}" == f"{x2:.1f}",
            f"{y:.1f}" == f"{y2:.1f}",
            f"{z:.1f}" == f"{z2:.1f}",
            ]):
            last_point = p2
        else:
            last_point = points.newPntIDPos3d(point_id, geom.Pos3d(x, y, z))
            point_id += 1
        l = lines.newLine(first_point.tag, last_point.tag)
        new_lines.append(l)
        first_point = last_point
    return new_lines, point_id


def apply_nonPrismatic_section(sets, bf, tf, tw, hw_min, hw_max, \
                               material, prep, element_handler):
    # dia_bounds = {
    #     'x': ['dia_bound.x', 'l_center.x', 'bnd.getZMin'],
    #     'y': ['dia_bound.y', 'l_center.y', 'bnd.getZMin'],
    #     'z': ['dia_bound.z', 'l_center.z', 'bnd.getZMin'],
    # }
    dhw = hw_max - hw_min
    for Set in sets:
        bnd = Set.lines.getBnd()
        dz = bnd.diagonal.z
        zmin = bnd.getZMin
        for line in Set.getLines:
            z_line = line.getCentroid().z
            percent = abs(z_line - zmin) / dz

            average_hw = hw_min + percent * dhw
            assert average_hw > 0
            # lines_len += l
            isection = ASTM_materials.IShape(bf, tf, tw, average_hw, material, f"Wisection{line.tag}")
            xc_material= isection.defElasticShearSection3d(prep)
            element_handler.defaultMaterial = xc_material.name
            element_handler.newElement('ElasticBeam3d', xc.ID([0,0]))
            line.genMesh(xc.meshDir.I)
            for e in line.getElements:
                e.setProp('crossSection',isection)
        Set.fillDownwards()

