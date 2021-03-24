# -*- coding: utf-8 -*-
''' Create the baseplate connections geometry.'''

from __future__ import division
from __future__ import print_function

import json
exec(open('./xc_model.py').read())

#supportSet.fillUpwards()
supportSet.fillDownwards()

import sys
sys.path.insert(0, './local_modules')
import connection_design as cd

columnLengthFactor= 1.5
beamLengthFactor= 1.0
gussetLengthFactor= 1.5
# Trick to get only one connection
print('Trick to get only one connection')
tmpNodBase= modelSpace.defSet('tmpNodBase')
for n in supportSet.nodes:
#    if(n.tag==63): # nodes 0, 82, 123, 41
    if n.tag == 123:
        tmpNodBase.nodes.append(n)
        break

connectionGroup= cd.BasePlateConnectionGroup('stair_tower_column_bases', columnLengthFactor, beamLengthFactor, gussetLengthFactor, tmpNodBase)
# End of the trick.

#connectionGroup= cd.BasePlateConnectionGroup('stair_tower_column_bases', columnLengthFactor, beamLengthFactor, gussetLengthFactor, supportSet)
connectionGroup.setWebGussetBottomLegSlope(0.9*math.tan(math.radians(30)))

loadData= connectionGroup.getLoadData('./intForce_ULS_normalStressesResistance.json')
with open('connectionLoadData.json', 'w') as outfile:
    json.dump(loadData, outfile)

blocks= connectionGroup.output()

