# -*- coding: utf-8 -*-
''' Check the ultimate limit states of the structure and write the
    result to later use.'''

import sys
sys.path.insert(0, '/home/ebi/xc/my_models/sole_zeinali/local_modules/')
import stability
import base_plate_design as bpd

import os
import time
import csv
import math
from postprocess.config import default_config
from postprocess import limit_state_data as lsd
from postprocess.reports import export_internal_forces as eif
from materials.astm_aisc import AISC_limit_state_checking as aisc
from solution import predefined_solutions

# Setup the project working directory.
cfg= default_config.EnvConfig(language='en', fNameMark= 'xc_model.py')
wDir= cfg.projectDirTree.workingDirectory
modelFiles= ['xc_model.py','loads.py','load_combinations.py']#'load_combinations.py']

modelModificationTime= 0.0
for f in modelFiles:
    filePath= wDir+'/'+f
    exec(open(filePath).read())
    modification_time= os.path.getmtime(filePath)
    modelModificationTime= max(modification_time,modelModificationTime)
    
# Compute internal forces.
lsd.LimitStateData.envConfig= cfg

## Set combinations to compute.
loadCombinations= preprocessor.getLoadHandler.getLoadCombinations

calcSet= allMemberSet

## Create AISC Member objects.

### Find splitted beams


splittedBeamsGroups= dict()
#### Read groups.
for ln in calcSet.getLines:
    labels= ln.getProp('labels')
    for lbl in labels:
        key= str(lbl)
        if(key[0]=='G'): # group
            splittedBeamsGroups[key]= list()
            
def belongsToGroup(ln):
    ''' Return the group name if the line belong to a group.'''
    labels= ln.getProp('labels')
    for lbl in labels:
        key= str(lbl)
        if(key in splittedBeamsGroups): # beam in group.
            return key
    return None
    
beamLines= list()
for ln in calcSet.getLines:
    groupName= belongsToGroup(ln)
    if(groupName): # splitted beam
        splittedBeamsGroups[groupName].append(ln)
    else: # not splitted beam
        beamLines.append((ln.name,[ln]))
        
for key in splittedBeamsGroups.keys():
    beamLines.append((key,splittedBeamsGroups[key]))


aiscMembers= list()
for beam in beamLines:
    beamName= beam[0]
    beamLine= beam[1]

    length= 0.0
    hws = []
    for l in beamLine:
        length += l.getLength()
    for bl in beamLine:
        shape= bl.getElements[0].getProp('crossSection')
        # beamName = bl.name
        hw = shape.hHalf
        hws.append(hw)
    # size = len(hws)

    i = hws.index(max(hws))
    shape = beamLine[i].getElements[0].getProp('crossSection')
    if length <= h_col / 2:
        unbracedLengthX = length
        unbracedLengthZ = h_col
        unbracedLengthY = length
    else:
        unbracedLengthX = 2
        unbracedLengthZ = math.sqrt((span/2) ** 2 + dy ** 2)
        unbracedLengthY = 2
    member= aisc.Member(name= beamName, section= shape, 
            unbracedLengthX=unbracedLengthX,
            unbracedLengthY= unbracedLengthY,
            unbracedLengthZ=unbracedLengthZ,
            lstLines= beamLine) # , sectionClassif= aisc.SectionClassif.noncompact)
    aiscMembers.append(member)

for m in aiscMembers:
    m.installULSControlRecorder(recorderType="element_prop_recorder")

# Prepare to exporting reactions
def getPointAxes(p):
    xAxes= ['A','C','E','G']
    yAxes= ['1']
    j= '1'
    i= xAxes[int(round(p.x/25,0))]
    return (j, i)

stairTowerId= 'st'
f= open('uls_reactions.csv', 'w')
writer= csv.writer(f)
joints= list()
supportSet.fillDownwards()
for n in supportSet.getNodes:
    pos= n.getInitialPos3d
    axes= getPointAxes(pos)
    pointId= axes[0]+stairTowerId+'-'+axes[1]+stairTowerId
    joints.append([n,pointId])

    
maxValue= stability.setImperfectionsXY(xcTotalSet,slopeX=1/500,slopeY=0)
print('max. imperfection displacement: ', maxValue,'m')

# Backup stiffness
stability.backupStiffness(allMemberSet)

## Compute internal forces for each combination

### Limit states to calculate internal forces for.
limitStates= [lsd.normalStressesResistance, # Normal stresses resistance.
lsd.shearResistance, # Shear stresses resistance (IS THE SAME AS NORMAL STRESSES, THIS IS WHY IT'S COMMENTED OUT).
] 
for ls in limitStates:
    loadCombinations= preprocessor.getLoadHandler.getLoadCombinations
    #Putting combinations inside XC.
    loadCombinations= ls.dumpCombinations(combContainer,loadCombinations)
    stability.calcInternalForces(modelSpace, calcSet, allMemberSet, [], aiscMembers, loadCombinations, ls, joints, writer,mxNumIter= 15, convergenceTestTol= .01)

f.close()

outCfg= lsd.VerifOutVars(setCalc=calcSet, appendToResFile='N', listFile='N', calcMeanCF='Y')
limitState= lsd.normalStressesResistance
limitState.controller= aisc.BiaxialBendingNormalStressController(limitState.label)
average= limitState.runChecking(outCfg)

limitState=lsd.shearResistance
limitState.controller= aisc.ShearController(limitState.label)
average=limitState.runChecking(outCfg)
