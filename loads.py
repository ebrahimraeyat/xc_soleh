# -*- coding: utf-8 -*-

G = 9.81

# Loads
loadCaseManager= lcm.LoadCaseManager(preprocessor)
loadCaseNames= [
        'DL',
        # 'SELF-DL',
        # 'LR',
        'SBalanced',
        'SUnbalancedLeft',
        'SUnbalancedRight',
        'wxPos',
        'wxNeg',
        'wyPos',
        'wyNeg',
        'winPos',
        'winNeg',
        ]
loadCaseManager.defineSimpleLoadCases(loadCaseNames) 

def applyAccelerationOnPermanentWeights(elementSet, accelVector):
    modelSpace.createSelfWeightLoad(elementSet,accelVector)


## Dead load.
### Self weight
# cLC= loadCaseManager.setCurrentLoadCase('SELF-DL')
cLC= loadCaseManager.setCurrentLoadCase('DL')
gravityVector= xc.Vector([0.0,0.0,G])
applyAccelerationOnPermanentWeights(allMemberSet, gravityVector)
### Dead load.
dead_load= (180 + 50)  * G #  N/m roof + z perlin
for e in (beam1Set.elements + beam2Set.elements):
    e.vector3dUniformLoadGlobal(xc.Vector([0,0,-dead_load]))

## snow load.
### snow balanced load
cLC= loadCaseManager.setCurrentLoadCase('SBalanced')
snow_load= 480 * G #N/m

for e in (beam1Set.elements + beam2Set.elements):
    e.vector3dUniformLoadGlobal(xc.Vector([0,0,-snow_load]))

### snow unbalanced load left to right
cLC = loadCaseManager.setCurrentLoadCase('SUnbalancedLeft')
snow_load = 80 * 6 * G
for e in (beam1Set.elements + beam2Set.elements):
    x = e.getPosCentroid(True).x
    z = e.getPosCentroid(True).z - h_col
    if x1 < x < x3:
        i = 0.5        
    elif x3 < x < x11:
        i = -1.5 / dy * z + 2
    elif x11 < x < x13:
        i = -0.5 / dy * z + 1
    e.vector3dUniformLoadGlobal(xc.Vector([0, 0, -i * snow_load]))

### snow unbalanced load right to left
cLC = loadCaseManager.setCurrentLoadCase('SUnbalancedRight')
snow_load = 80 * 6 * G
for e in (beam1Set.elements + beam2Set.elements):
    x = e.getPosCentroid(True).x
    z = e.getPosCentroid(True).z - h_col
    if x11 < x < x13:
        i = 0.5        
    elif x3 < x < x11:
        i = -1.5 / dy * z + 2
    elif x1 < x < x3:
        i = -0.5 / dy * z + 1
    e.vector3dUniformLoadGlobal(xc.Vector([0, 0, -i * snow_load]))

## wind load
Iw = 1
q = .47
ct = 1
cd = .85
z = h_col + .5 * dy
ce = max((z / 10) ** .2, .9)
dist_between_frames = 6
p = f"Iw * q * ct * cd * ce * cgXcp * {dist_between_frames} * 100"

### wind load in x+
loadCaseManager.setCurrentLoadCase('wxPos')
cgXcp = (1 + 1.5) / 2
wind_load = eval(p) * G
for e in col_frame_a_set.elements:
    e.vector3dUniformLoadGlobal(xc.Vector([wind_load, 0, 0]))

cgXcp = (.8 + 1.2) / 2
wind_load = eval(p) * G
for e in col_frame_g_set.elements:
    e.vector3dUniformLoadGlobal(xc.Vector([wind_load, 0, 0]))

for e in (beam1Set.elements + beam2Set.elements):
    x = e.getPosCentroid(True).x
    if any([
        x1 < x < x3,
        x5 < x < x7,
        x9 < x < x11,
        ]):
        cgXcp = (1.3 + 2) / 2
        wind_load = eval(p) * G
    else:
        cgXcp = (1.3 + .9) / 2
        wind_load = eval(p) * G
    e.vector3dUniformLoadLocal(xc.Vector([0, -wind_load, 0]))

### wind load in x-
loadCaseManager.setCurrentLoadCase('wxNeg')
cgXcp = (.8 + 1.2) / 2
wind_load = eval(p) * G
for e in col_frame_a_set.elements:
    e.vector3dUniformLoadGlobal(xc.Vector([-wind_load, 0, 0]))

cgXcp = (1 + 1.5) / 2
wind_load = eval(p) * G
for e in col_frame_g_set.elements:
    e.vector3dUniformLoadGlobal(xc.Vector([-wind_load, 0, 0]))

for e in (beam1Set.elements + beam2Set.elements):
    x = e.getPosCentroid(True).x
    if any([
        x1 < x < x3,
        x5 < x < x7,
        x9 < x < x11,
        ]):
        cgXcp = (1.3 + .9) / 2
        wind_load = eval(p) * G
    else:
        cgXcp = (1.3 + 2) / 2
        wind_load = eval(p) * G
    e.vector3dUniformLoadLocal(xc.Vector([0, -wind_load, 0]))

### wind load in +y direction
loadCaseManager.setCurrentLoadCase('wyPos')
cgXcp = (.85 + .9) / 2
wind_load = eval(p) * G
for e in col_frame_a_set.elements:
    e.vector3dUniformLoadGlobal(xc.Vector([-wind_load, 0, 0]))

for e in col_frame_g_set.elements:
    e.vector3dUniformLoadGlobal(xc.Vector([wind_load, 0, 0]))

for e in (beam1Set.elements + beam2Set.elements):
    x = e.getPosCentroid(True).x
    if any([
        x1 < x < x3,
        x5 < x < x7,
        x9 < x < x11,
        ]):
        cgXcp = (1 + .7) / 2
        wind_load = eval(p) * G
    else:
        cgXcp = (1.3 + 2) / 2
        wind_load = eval(p) * G
    e.vector3dUniformLoadLocal(xc.Vector([0, -wind_load, 0]))

### wind load in -y direction
loadCaseManager.setCurrentLoadCase('wyNeg')
cgXcp = (.85 + .9) / 2
wind_load = eval(p) * G
for e in col_frame_a_set.elements:
    e.vector3dUniformLoadGlobal(xc.Vector([-wind_load, 0, 0]))

for e in col_frame_g_set.elements:
    e.vector3dUniformLoadGlobal(xc.Vector([wind_load, 0, 0]))

for e in (beam1Set.elements + beam2Set.elements):
    x = e.getPosCentroid(True).x
    if any([
        x1 < x < x3,
        x5 < x < x7,
        x9 < x < x11,
        ]):
        cgXcp = (1.3 + 2) / 2
        wind_load = eval(p) * G
    else:
        cgXcp = (1 + .7) / 2
        wind_load = eval(p) * G
    e.vector3dUniformLoadLocal(xc.Vector([0, -wind_load, 0]))

### positive interior wind load
loadCaseManager.setCurrentLoadCase('winPos')
wind_load = 195 * G
for e in col_frame_a_set.elements:
    e.vector3dUniformLoadGlobal(xc.Vector([wind_load, 0, 0]))

for e in col_frame_g_set.elements:
    e.vector3dUniformLoadGlobal(xc.Vector([-wind_load, 0, 0]))

wind_load = 200 * G
for e in (beam1Set.elements + beam2Set.elements):
    e.vector3dUniformLoadLocal(xc.Vector([0, wind_load, 0]))

### negative interior wind load
loadCaseManager.setCurrentLoadCase('winNeg')
wind_load = 85 * G
for e in col_frame_a_set.elements:
    e.vector3dUniformLoadGlobal(xc.Vector([-wind_load, 0, 0]))
wind_load = 130 * G
for e in col_frame_g_set.elements:
    e.vector3dUniformLoadGlobal(xc.Vector([wind_load, 0, 0]))

wind_load = 130 * G
for e in (beam1Set.elements + beam2Set.elements):
    e.vector3dUniformLoadLocal(xc.Vector([0, -wind_load, 0]))

