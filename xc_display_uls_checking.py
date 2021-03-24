# -*- coding: utf-8 -*-
''' Show the results of the ULS checking.'''

from __future__ import division
from __future__ import print_function

__author__= "Ana Ortega (AO_O) and Luis C. Pérez Tato (LCPT)"
__copyright__= "Copyright 2020, AO_O and LCPT"
__license__= "GPL"
__version__= "3.0"
__email__= " ana.Ortega.Ort@gmail.com, l.pereztato@gmail.com"

import os
import time
from postprocess.config import default_config
from postprocess import limit_state_data as lsd
from materials.astm_aisc import AISC_limit_state_checking as aisc

# Setup the project working directory.
cfg= default_config.EnvConfig(language='en', fNameMark= 'xc_model.py')
wDir= cfg.projectDirTree.workingDirectory

modelFiles= ['xc_model.py','loads.py','load_combinations.py']

for f in modelFiles:
    filePath= wDir+'/'+f
    exec(open(filePath).read())

#Load properties to display:
lsd.LimitStateData.envConfig= cfg
exec(open(cfg.projectDirTree.getVerifNormStrFile()).read())
exec(open(cfg.projectDirTree.getVerifShearFile()).read())

#########################################################
# Graphic stuff.
oh= output_handler.OutputHandler(modelSpace)

calcSet = modelSpace.setSum('calcSet', [
                                 beam1Set,
                                 beam2Set,
                                 col_frame_a_set,
                                 col_frame_e_set,
                                 col_frame_c_set,
                                 col_frame_g_set,
                                 ])

setsToDisplay= [calcSet]
itemD= 'CF'#'My'#'Mz'#'chiLT'


for calcSet in setsToDisplay:
    oh.displayBeamResult(attributeName=lsd.normalStressesResistance.label, itemToDisp= itemD, beamSetDispRes=calcSet, setToDisplay=xcTotalSet)
    oh.displayBeamResult(attributeName=lsd.shearResistance.label, itemToDisp= itemD, beamSetDispRes=calcSet, setToDisplay=xcTotalSet)
