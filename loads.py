# -*- coding: utf-8 -*-

G = 9.81

# Loads
loadCaseManager= lcm.LoadCaseManager(preprocessor)
loadCaseNames= [
        'DL',
        'SELF_DL',
        # 'LR',
        's_balanced',
        's_unbalanced_left',
        's_unbalanced_right',
        'wx_pos',
        'wx_neg',
        # 'wy',
        'win_pos',
        'win_neg',
        ]
loadCaseManager.defineSimpleLoadCases(loadCaseNames) 

def applyAccelerationOnPermanentWeights(elementSet, accelVector):
    modelSpace.createSelfWeightLoad(elementSet,accelVector)


## Dead load.
### Self weight
cLC= loadCaseManager.setCurrentLoadCase('SELF_DL')
gravityVector= xc.Vector([0.0,0.0,G])
applyAccelerationOnPermanentWeights(allMemberSet, gravityVector)
### Dead load.
cLC= loadCaseManager.setCurrentLoadCase('DL')
dead_load= (180 + 50)  * G #  N/m roof + z perlin
for e in (beam1Set.elements + beam2Set.elements):
    e.vector3dUniformLoadGlobal(xc.Vector([0,0,-dead_load]))

## snow load.
### snow balanced load
cLC= loadCaseManager.setCurrentLoadCase('s_balanced')
snow_load= 480 * G #N/m

for e in (beam1Set.elements + beam2Set.elements):
    e.vector3dUniformLoadGlobal(xc.Vector([0,0,-snow_load]))

### snow unbalanced load left to right
cLC = loadCaseManager.setCurrentLoadCase('s_unbalanced_left')
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
cLC = loadCaseManager.setCurrentLoadCase('s_unbalanced_right')
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
### wind load in x+
loadCaseManager.setCurrentLoadCase('wx_pos')
wind_load = 210 * G
for e in col_frame_a_set.elements:
    e.vector3dUniformLoadGlobal(xc.Vector([wind_load, 0, 0]))

wind_load = 150 * G
for e in col_frame_g_set.elements:
    e.vector3dUniformLoadGlobal(xc.Vector([wind_load, 0, 0]))

for e in (beam1Set.elements + beam2Set.elements):
    x = e.getPosCentroid(True).x
    if any([
        x1 < x < x3,
        x5 < x < x7,
        x9 < x < x11,
        ]):
        wind_load = 360 * G
    else:
        wind_load = 190 * G
    e.vector3dUniformLoadLocal(xc.Vector([0, -wind_load, 0]))

### wind load in x-
loadCaseManager.setCurrentLoadCase('wx_neg')
wind_load = 150 * G
for e in col_frame_a_set.elements:
    e.vector3dUniformLoadGlobal(xc.Vector([-wind_load, 0, 0]))

wind_load = 210 * G
for e in col_frame_g_set.elements:
    e.vector3dUniformLoadGlobal(xc.Vector([-wind_load, 0, 0]))

for e in (beam1Set.elements + beam2Set.elements):
    x = e.getPosCentroid(True).x
    if any([
        x1 < x < x3,
        x5 < x < x7,
        x9 < x < x11,
        ]):
        wind_load = 190 * G
    else:
        wind_load = 360 * G
    e.vector3dUniformLoadLocal(xc.Vector([0, -wind_load, 0]))

### positive interior wind load
loadCaseManager.setCurrentLoadCase('win_pos')
wind_load = 195 * G
for e in col_frame_a_set.elements:
    e.vector3dUniformLoadGlobal(xc.Vector([wind_load, 0, 0]))

for e in col_frame_g_set.elements:
    e.vector3dUniformLoadGlobal(xc.Vector([-wind_load, 0, 0]))

wind_load = 200 * G
for e in (beam1Set.elements + beam2Set.elements):
    e.vector3dUniformLoadLocal(xc.Vector([0, wind_load, 0]))

### negative interior wind load
loadCaseManager.setCurrentLoadCase('win_neg')
wind_load = 85 * G
for e in col_frame_a_set.elements:
    e.vector3dUniformLoadGlobal(xc.Vector([-wind_load, 0, 0]))
wind_load = 130 * G
for e in col_frame_g_set.elements:
    e.vector3dUniformLoadGlobal(xc.Vector([wind_load, 0, 0]))

wind_load = 130 * G
for e in (beam1Set.elements + beam2Set.elements):
    e.vector3dUniformLoadLocal(xc.Vector([0, -wind_load, 0]))

