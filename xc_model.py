''' Create the finite element mesh and element sets.'''
import math

import xc_base
import geom
import xc
from actions import combinations as combs
from actions import load_cases as lcm
from materials import typical_materials
from materials.aci import ACI_materials
from materials.astm_aisc import ASTM_materials
from materials.sections import section_properties
from model import predefined_spaces
from postprocess import output_handler
from postprocess.config import default_config

from funcs import apply_nonPrismatic_section, create_lines

FEcase = xc.FEProblem()
FEcase.title = 'Industrial structure zeinali'

preprocessor = FEcase.getPreprocessor
nodes = preprocessor.getNodeHandler
elements = preprocessor.getElementHandler
points = preprocessor.getMultiBlockTopology.getPoints
lines = preprocessor.getMultiBlockTopology.getLines


# groups= preprocessor.getSets
h_col = 7.6
dy = 2.5
slop = .2
span = 24
n = 0
rafter_percent = 1 / 6

dx = rafter_percent * span
x1 = 0
x2 = dx
x3 = .5 * span
x4 = span - dx
x5 = span
x6 = span + dx
x7 = 1.5 * span
x8 = 2 * span - dx
x9 = 2 * span
x10 = 2 * span + dx
x11 = 2.5 * span
x12 = 3 * span - dx
x13= 3 * span

z1 = 0
z2 = h_col
z3 = h_col + dx * slop
z4 = h_col + .5 * span * slop


ndiv_col = 10  # number of diviation for column
ndiv_beam1 = 6
ndiv_beam2 = 2 * ndiv_beam1
# dimentions for section of columns and beams
bf = .20
tf_col = .012
tf_rafter = .01
tw_col = .008
hw_col_bot = .20
hw_col_top = .8

pt0 = points.newPntIDPos3d(n, geom.Pos3d(x1, 0, z1))
n += 1
pt1 = points.newPntIDPos3d(n, geom.Pos3d(x5, 0, z1))
n += 1
pt2 = points.newPntIDPos3d(n, geom.Pos3d(x9, 0, z1))
n += 1
pt31 = points.newPntIDPos3d(n, geom.Pos3d(x13, 0, z1))
n += 1
for pt in (pt0, pt1, pt2, pt31):
    pt.setProp("labels", ['xc_supports'])
pt3 = points.newPntIDPos3d(n, geom.Pos3d(x1, 0, z2))
n += 1
pt4 = points.newPntIDPos3d(n, geom.Pos3d(x2, 0, z3))
n += 1
pt5 = points.newPntIDPos3d(n, geom.Pos3d(x3, 0, z4))
n += 1
pt6 = points.newPntIDPos3d(n, geom.Pos3d(x4, 0, z3))
n += 1
pt7 = points.newPntIDPos3d(n, geom.Pos3d(x5, 0, z2))
n += 1
pt8 = points.newPntIDPos3d(n, geom.Pos3d(x6, 0, z3))
n += 1
pt9 = points.newPntIDPos3d(n, geom.Pos3d(x7, 0, z4))
n += 1
pt10 = points.newPntIDPos3d(n, geom.Pos3d(x8, 0, z3))
n += 1
pt11 = points.newPntIDPos3d(n, geom.Pos3d(x9, 0, z2))
n += 1
pt12 = points.newPntIDPos3d(n, geom.Pos3d(x10, 0, z3))
n += 1
pt13 = points.newPntIDPos3d(n, geom.Pos3d(x11, 0, z4))
n += 1
pt14 = points.newPntIDPos3d(n, geom.Pos3d(x12, 0, z3))
n += 1
pt15 = points.newPntIDPos3d(n, geom.Pos3d(x13, 0, z2))

col_frame_a, n = create_lines(pt0, pt3, ndiv_col, points, lines, n+1)
col_frame_c, n = create_lines(pt1, pt7, ndiv_col, points, lines, n)
col_frame_e, n = create_lines(pt2, pt11, ndiv_col, points, lines, n)
col_frame_g, n = create_lines(pt31, pt15, ndiv_col, points, lines, n)

beam1_frame_a, n = create_lines(pt3, pt4, ndiv_beam1, points, lines, n)
beam1_frame_c1, n = create_lines(pt6, pt7, ndiv_beam1, points, lines, n)
beam1_frame_c2, n = create_lines(pt7, pt8, ndiv_beam1, points, lines, n)
beam1_frame_e1, n = create_lines(pt10, pt11, ndiv_beam1, points, lines, n)
beam1_frame_e2, n = create_lines(pt11, pt12, ndiv_beam1, points, lines, n)
beam1_frame_g, n = create_lines(pt14, pt15, ndiv_beam1, points, lines, n)


def set_beam_prop(lines, props, n, first=z3, last=z4):
    dz = (last - first) / n
    for b in lines:
        z = b.getPosCentroid().z
        i = int((z - first) / dz)
        b.setProp("labels", [props[0], f"{props[1]}{i}"])


def set_col_prop(lines, prop1, prop2, prop3):
    dz_torsional_support = h_col / 2
    for b in lines:
        z = b.getPosCentroid().z
        if z < dz_torsional_support:
            b.setProp("labels", prop1)
        elif  dz_torsional_support < z < 2 * dz_torsional_support:
            b.setProp("labels", prop2)
        else:
            b.setProp("labels", prop3)

dz_torsional_support = dy / 3

beam2_frame_b1, n = create_lines(pt4, pt5, ndiv_beam2, points, lines, n)
set_beam_prop(beam2_frame_b1, ['beam2', 'GBB1'], 4, first=z3, last=z4)

beam2_frame_b2, n = create_lines(pt5, pt6, ndiv_beam2, points, lines, n)
set_beam_prop(beam2_frame_b2, ['beam2', 'GBB2'], 4, first=z3, last=z4)

beam2_frame_d1, n = create_lines(pt8, pt9, ndiv_beam2, points, lines, n)
set_beam_prop(beam2_frame_d1, ['beam2', 'GBD1'], 4, first=z3, last=z4)

beam2_frame_d2, n = create_lines(pt9, pt10, ndiv_beam2, points, lines, n)
set_beam_prop(beam2_frame_d2, ['beam2', 'GBD2'], 4, first=z3, last=z4)

beam2_frame_f1, n = create_lines(pt12, pt13, ndiv_beam2, points, lines, n)
set_beam_prop(beam2_frame_f1, ['beam2', 'GBF1'], 4, first=z3, last=z4)

beam2_frame_f2, n = create_lines(pt13, pt14, ndiv_beam2, points, lines, n)
set_beam_prop(beam2_frame_f2, ['beam2', 'GBF2'], 4, first=z3, last=z4)

# set properties to beam 1
set_beam_prop(beam1_frame_a, ['beam1', 'GBA'], 2, first=z2, last=z3)
set_beam_prop(beam1_frame_c1, ['beam1', 'GBC1'], 2, first=z2, last=z3)
set_beam_prop(beam1_frame_c2, ['beam1', 'GBC2'], 2, first=z2, last=z3)
set_beam_prop(beam1_frame_e1, ['beam1', 'GBE1'], 2, first=z2, last=z3)
set_beam_prop(beam1_frame_e2, ['beam1', 'GBE2'], 2, first=z2, last=z3)
set_beam_prop(beam1_frame_g, ['beam1', 'GBG'], 2, first=z2, last=z3)


set_col_prop(col_frame_a, ['xc_col_a', 'GCA1'], ['xc_col_a', 'GCA2'], ['xc_col_a', 'GCA3'])
set_col_prop(col_frame_c, ['xc_col_c', 'GCC1'], ['xc_col_c', 'GCC2'], ['xc_col_c', 'GCC3'])
set_col_prop(col_frame_e, ['xc_col_e', 'GCE1'], ['xc_col_e', 'GCE2'], ['xc_col_e', 'GCE3'])
set_col_prop(col_frame_g, ['xc_col_g', 'GCG1'], ['xc_col_g', 'GCG2'], ['xc_col_g', 'GCG3'])



xcTotalSet = preprocessor.getSets.getSet('total')

preprocessor = FEcase.getPreprocessor
nodes = preprocessor.getNodeHandler
modelSpace = predefined_spaces.StructuralMechanics3D(nodes)

columnSet = preprocessor.getSets.defSet('columnSet')
beam1Set = preprocessor.getSets.defSet('beam1Set')
beam2Set = preprocessor.getSets.defSet('beam2Set')
supportSet = preprocessor.getSets.defSet('supportSet')
col_frame_a_set = preprocessor.getSets.defSet('colFrameASet')
col_frame_c_set = preprocessor.getSets.defSet('colFrameCSet')
col_frame_e_set = preprocessor.getSets.defSet('colFrameESet')
col_frame_g_set = preprocessor.getSets.defSet('colFrameGSet')

setsFromLabels = {
    'xc_columns': columnSet,
    'xc_col_a': col_frame_a_set,
    'xc_col_c': col_frame_c_set,
    'xc_col_e': col_frame_e_set,
    'xc_col_g': col_frame_g_set,
    'xc_supports': supportSet,
    'beam1': beam1Set,
    'beam2': beam2Set,
}

for l in xcTotalSet.getLines:
    if(l.hasProp('labels')):
        labels = l.getProp('labels')
        for key in setsFromLabels:
            if(labels.count(key) > 0):
                xcSet = setsFromLabels[key]
                xcSet.getLines.append(l)


# Supports
for p in xcTotalSet.getPoints:
    if(p.hasProp('labels')):
        labels = p.getProp('labels')
        if(labels.count('xc_supports') > 0):
            supportSet.getPoints.append(p)


# Materials
# Steel material
steel_W = ASTM_materials.A36 # steel support W shapes
steel_W.fy = 240e6
steel_W.gammaM = 1.00
# Profile geometry
inner_column_profile = ASTM_materials.IShape(bf, tf_col, tw_col, hw_col_bot, steel_W, f"W18X35")
beam2_profile = ASTM_materials.IShape(bf, tf_rafter, tw_col, hw_col_bot+.1, steel_W, f"isectionbeam2")

# Mesh generation.
coordTransf = preprocessor.getTransfCooHandler.newCorotCrdTransf3d(
    'coordTransf')
coordTransf.xzVector = xc.Vector([0, 1, 0])

seedElemHandler = preprocessor.getElementHandler.seedElemHandler
seedElemHandler.defaultTransformation = 'coordTransf'

# Columns.
apply_nonPrismatic_section([
                            col_frame_a_set, 
                            col_frame_g_set,
                            ], bf,
                           tf_col, tw_col, hw_col_bot, hw_col_top,
                           steel_W, preprocessor, seedElemHandler)
modelSpace.createElasticBeams(
    col_frame_c_set, inner_column_profile, coordTransf, xc.Vector([0, 1, 0])
    )
modelSpace.createElasticBeams(
    col_frame_e_set, inner_column_profile, coordTransf, xc.Vector([0, 1, 0])
    )

# Main beams.
apply_nonPrismatic_section([beam1Set], bf, tf_rafter, tw_col, hw_col_top,
    hw_col_bot+.1, steel_W, preprocessor, seedElemHandler)
modelSpace.createElasticBeams(
    beam2Set, beam2_profile, coordTransf, xc.Vector([0, 1.0, 0]), nDiv=6)

# Constraints
# Columns
support_points_tag = []
for p in supportSet.getPoints:
    if(not p.hasNode):
        lmsg.warning('point: '+str(p)+' not meshed.')
    n = p.getNode()
    support_points_tag.append(n.tag)
    modelSpace.fixNode('000_0F0', n.tag)


allMemberSet = modelSpace.setSum('allMemberSet', [
                                 beam1Set,
                                 beam2Set,
                                 col_frame_a_set,
                                 col_frame_e_set,
                                 col_frame_c_set,
                                 col_frame_g_set,
                                 ])

# columnSet.description= 'Columns'

# Graphic stuff.
oh = output_handler.OutputHandler(modelSpace)
oh.getCameraParameters().viewName = "YNeg"
# oh.displayFEMesh()
# oh.displayBlocks()
# oh.displayLocalAxes()
# oh.displayLoads()
# oh.displayReactions()
# oh.displayDispRot(itemToDisp='uX')
# oh.displayDispRot(itemToDisp='uY')
# oh.displayDispRot(itemToDisp='uZ')
