# -*- coding: utf-8 -*-
''' Displays the eigenvectors corresponding to the lowest eigenvalues.'''

exec(open('./xc_model.py').read())

# Graphic stuff.
oh = output_handler.OutputHandler(modelSpace)

# oh.displayBlocks()
# oh.displayFEMesh()
# oh.displayLocalAxes()

# Zero energy modes.
numEigenModes = 4
analOk = modelSpace.illConditioningAnalysis(numEigenModes)
computedModes = modelSpace.preprocessor.getDomain.numModes
for i in range(1, computedModes):
    oh.displayEigenvectors(mode=i)
    # oh.displayEigenResult(i, defFScale=2)