# -*- coding: utf-8 -*-
''' Base plate connection finite element model.'''

from __future__ import division
from __future__ import print_function

import sys
import math
import xc_base
import geom
import xc

from model import predefined_spaces
from postprocess import output_handler
from postprocess.config import default_config
from materials.astm_aisc import ASTM_materials
from materials import typical_materials

sys.path.insert(0, '../local_modules')
import import_connection
import connection_meshing
import  steel_connection
limeSiloBasePlate= xc.FEProblem()
limeSiloBasePlate.title= 'Connection model'
preprocessor= limeSiloBasePlate.getPreprocessor
exec(open('../stair_tower_column_bases_blocks.py').read())

# Problem type
nodes= preprocessor.getNodeHandler
modelSpace= predefined_spaces.StructuralMechanics3D(nodes) 

xcTotalSet= modelSpace.getTotalSet()

# Import CAD information
columnSet= preprocessor.getSets.defSet('columnSet')
flangeGussetSet= preprocessor.getSets.defSet('flangeGussetSet')
webGussetSet= preprocessor.getSets.defSet('webGussetSet')
boltedPlateSet= preprocessor.getSets.defSet('boltedPlateSet')
baseplateSet= preprocessor.getSets.defSet('baseplateSet')

setsFromLabels= {'column':columnSet, 'flange_gusset':flangeGussetSet, 'web_gusset':webGussetSet, 'bolted_plate':boltedPlateSet, 'baseplate':baseplateSet}

## Colors
columnSet.color= default_config.setBasicColors['blue01']
flangeGussetSet.color= default_config.setBasicColors['green01']
webGussetSet.color= default_config.setBasicColors['yellow01']
boltedPlateSet.color= default_config.setBasicColors['red01']
baseplateSet.color= default_config.setBasicColors['green02']

setsToDisplay= [columnSet, flangeGussetSet, webGussetSet, boltedPlateSet, baseplateSet]

## Build sets from labels
holes= import_connection.populateSets(setsFromLabels, xcTotalSet)
matchedBolts= import_connection.matchHoleCenters(xcTotalSet,xcBlocksDict)

# Put the holes in its place (in its polygonal face).
import_connection.matchHoles(holes, xcBlocksDict)

# Welds
welds= import_connection.extractWelds(xcTotalSet, xcBlocksDict)

## Material definition
xc_materials= connection_meshing.getMembranePlateMaterials(preprocessor)

## Meshing
modelSpace.conciliaNDivs()
seedElemHandler= modelSpace.getSeedElementHandler()
connection_meshing.genConnectionMesh([columnSet], [baseplateSet, webGussetSet, flangeGussetSet, boltedPlateSet], xc_materials, seedElemHandler)

#Generation of bolts and bearing elements (radii) and welds
weldSzFactor=0.6  # factor to choose weld size for each weld
                     # seam (0 corresponds to minimum weld size and
                     # 1 to maximum weld size)
#avlbWeldSz=[14e-3,16e-3,18e-3]  #available weld sizes
weldMetal= steel_connection.E7018

# ****   Change weld sizes:
welds2change= {'w1':{'name': 'baseplate', 'oldSize': 0.018, 't1': 0.0335, 'newSize':0.022}}
steel_connection.change_weld_size(welds,welds2change)
# ****   End change weld sizes:

boltSets2Check, welds2Check= steel_connection.gen_bolts_and_weld_elements(modelSpace, matchedBolts, weldMetal, welds)#,weldSzFactor, avlbWeldSz)

## Loading
loadCaseNames= connection_meshing.createLoadsFromFile(modelSpace, './connectionLoadData.json')

# Graphic stuff.
allotherSet=preprocessor.getSets.defSet('allotherSet')
allotherSet=modelSpace.setSum('allotherSet',[xcTotalSet,allotherSet])
columnSet.fillDownwards() ; flangeGussetSet.fillDownwards() ; webGussetSet.fillDownwards() ; baseplateSet.fillDownwards() ; boltedPlateSet.fillDownwards()
allotherSet-=columnSet

allotherSet-=flangeGussetSet
allotherSet-=webGussetSet
allotherSet-=baseplateSet
allotherSet.color=default_config.setBasicColors['brown04']
sets2Disp=[columnSet,flangeGussetSet,webGussetSet,baseplateSet,allotherSet]
oh= output_handler.OutputHandler(modelSpace)
oh.displayFEMesh(sets2Disp)
#oh.displayBlocks()#setToDisplay= )
#oh.displayFEMesh(setsToDisplay= setsToDisplay)#setsToDisplay=[])
#oh.displayLocalAxes()
# for name in loadCaseNames:
#     modelSpace.addLoadCaseToDomain(str(name))
#     oh.displayLoads()
#     modelSpace.removeLoadCaseFromDomain(str(name))
#oh.displayReactions()
#oh.displayDispRot(itemToDisp='uX')
#oh.displayDispRot(itemToDisp='uY')
#oh.displayDispRot(itemToDisp='uZ')

#Calculation and checking of bolts and welds
#remove anchor bolts from checking

not_checked = []
for k in boltSets2Check.keys():
    if 'F1554' in boltSets2Check[k]['boltCheckTyp'].steelType.name:
        not_checked.append(k)

for k in not_checked:
    boltSets2Check.pop(k) 

lstBoltSets2Check=[[boltSets2Check[key]['boltSet'],boltSets2Check[key]['boltCheckTyp']] for key in boltSets2Check.keys()]


#steel_connection.aisc_check_bolts_welds(modelSpace, ULSs=loadCaseNames, boltSets2Check=lstBoltSets2Check, welds2Check=welds2Check, baseMetal=connection_meshing.steel_dict['A36'],meanShearProc=True)#foundSprings=None)#found.springs)

