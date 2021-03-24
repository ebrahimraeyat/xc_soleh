# -*- coding: utf-8 -*-
from postprocess import limit_state_data as lsd
from materials.astm_aisc import AISC_limit_state_checking as aisc
from postprocess.control_vars import VonMisesControlVars

exec(open("./xc_connection_model.py").read()) #FE model generation

argument= 'CF'       #Possible arguments: 'CF', 'vm_stress', 'combName'
'''
mainFlangeGusset=modelSpace.setSum('mainFlangeGusset',[flangeGussetSet])
mainFlangeGusset-=boltedPlateSet
mainFlangeGusset.fillDownwards()

mainWebGusset=modelSpace.setSum('mainWebGusset',[webGussetSet])
mainWebGusset-=boltedPlateSet
mainWebGusset.fillDownwards()
'''
limitState= lsd.vonMisesStressResistance

#Load properties to display:
exec(open('./results/verifications/verifRsl_VonMisesStressULS.py').read())
from postprocess import output_handler
oh= output_handler.OutputHandler(modelSpace)
allSet = modelSpace.setSum('allSet', [columnSet, baseplateSet])
sets2disp=[allSet, columnSet, baseplateSet]
for st in sets2disp:
    oh.displayField(limitStateLabel= limitState.label, section= None, argument=argument, component= None, setToDisplay= st, fileName= None)
