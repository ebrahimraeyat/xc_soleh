# -*- coding: utf-8 -*-
''' Make a rough check of a diagonal fastener design defined by the user.'''

from __future__ import division
from __future__ import print_function

import json
from postprocess import limit_state_data
#from materials.ec3 import EC3_limit_state_checking as EC3lscheck
from postprocess.config import default_config
import sys
sys.path.insert(0, './local_modules')
import connection_design as cd

#Verification of normal-stresses ULS for structural steel

workingDirectory= default_config.findWorkingDirectory()+'/'
exec(open(workingDirectory+'xc_model.py').read()) #FE model generation
#exec(open(workingDirectory+'limit_states_def.py').read())
limit_state_data.LimitStateData.envConfig= default_config.EnvConfig(language='en', fNameMark= 'xc_model.py')

#Steel beams definition
#exec(open(workingDirectory+'steel_beams_def.py').read())

# Bolted plate
bolt= ASTM_materials.M22
bolt.steelType= ASTM_materials.A325
boltArray= ASTM_materials.BoltArray(bolt, nRows= 2, nCols= 3)
boltedPlate= ASTM_materials.BoltedPlate(boltArray, thickness= 20e-3, steelType= ASTM_materials.A36)

#setCalc=suppFrame
setCalc= diagonalSet

# variables that control the output of the checking (setCalc,
# appendToResFile .py [defaults to 'N'], listFile .tex [defaults to 'N']
outCfg= limit_state_data.VerifOutVars(setCalc=setCalc,appendToResFile='N',listFile='N',calcMeanCF='Y')

limitState= limit_state_data.normalStressesResistance
intForcesFileName= limitState.getInternalForcesFileName()
controller= cd.BoltedPlateController(boltedPlate)
worstCase= controller.predimConnection(intForcesFileName, setCalc)
print('bolted plate: ', boltedPlate)
print('worst case: ', worstCase)
outputFileName= 'base_plates/diagonal_fastener.json'
with open(outputFileName, 'w') as outfile:
    json.dump(boltedPlate.getDict(), outfile)
outfile.close()



