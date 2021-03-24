# -*- coding: utf-8 -*-

''' Checking of Von Mises stresses.'''

from postprocess import limit_state_data as lsd
from materials.astm_aisc import AISC_limit_state_checking as aisc
from postprocess.config import default_config
from actions import combinations as combs


exec(open('./xc_connection_model.py').read())
## Load combinations
combContainer= combs.CombContainer()
### Ultimate limit state.
for ULSnm in loadCaseNames:
    combContainer.ULS.perm.add(str(ULSnm),'1.0*'+str(ULSnm))

### Dump combination definition into XC.
combContainer.dumpCombinations(preprocessor)

shellSets=modelSpace.setSum('shellSets',[columnSet,baseplateSet,flangeGussetSet,webGussetSet])
plateSets=modelSpace.setSum('plateSets',[baseplateSet,flangeGussetSet,webGussetSet])
#setCalc=shellSets
for e in plateSets.elements: e.setProp('yieldStress', ASTM_materials.A36.fy)
for e in columnSet.elements: e.setProp('yieldStress', ASTM_materials.A992.fy)

setCalc=shellSets


cfg= default_config.EnvConfig(language='en',intForcPath= 'results/internalForces/',verifPath= 'results/verifications/',reportPath='./',resultsPath= 'annex/',grWidth='120mm')
cfg.projectDirTree.workingDirectory='./'
lsd.LimitStateData.envConfig= cfg
### Set combinations to compute.
loadCombinations= preprocessor.getLoadHandler.getLoadCombinations

### Limit states to calculate internal forces for.
limitState= lsd.vonMisesStressResistance
limitState.vonMisesStressId= 'avg_von_mises_stress'
limitStates= [limitState]

### Compute internal forces for each combination
for ls in limitStates:
    ls.saveAll(combContainer,setCalc)
### Check material resistance.
outCfg= lsd.VerifOutVars(setCalc=setCalc, appendToResFile='N', listFile='N', calcMeanCF='Y')
limitState.controller= aisc.VonMisesStressController(limitState.label)
average= limitState.runChecking(outCfg)

from postprocess import output_handler
oh= output_handler.OutputHandler(modelSpace)
oh.displayFEMesh()
oh.displayField(limitStateLabel= limitState.label, section= None, argument= 'CF', component= None, setToDisplay= None, fileName= None)
oh.displayLoads()
#oh.displayDispRot('uY')
#oh.displayStrains('epsilon_xx')
#oh.displayStresses('sigma_11')
#oh.displayVonMisesStresses(vMisesCode= 'max_von_mises_stress')
