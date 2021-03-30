# -*- coding: utf-8 -*-
''' Display the response of the structure for each load case.'''
from solution import predefined_solutions
import csv
exec(open('./xc_model.py').read())
exec(open('./loads.py').read())


# def getPointAxes(p):
#     yAxes= ['A','B','C']
#     xAxes= ['1','2','3']
#     j= yAxes[int(round(p.y/2.415,0))]
#     i= xAxes[int(round(p.x/5.525,0))]
#     return (j, i)

# stairTowerId= 'st'
# f= open('reactions.csv', 'w')
# writer= csv.writer(f)

# Set non-linear analysis.
modelSpace.analysis = predefined_solutions.penalty_newton_raphson(
    modelSpace.preprocessor.getProblem)

# Graphic stuff.
oh = output_handler.OutputHandler(modelSpace)
# loadCaseNames= [
#         'DL',
#         'SELF_DL',
#         'LR',
#         's_balanced',
#         's_unbalanced_left',
#         's_unbalanced_right',
#         'wx_pos',
#         'wx_neg',
#         'wy_pos',
#         'wy_neg',
#         'win_pos',
#         'win_neg',
#         ]
for l in loadCaseNames:
    modelSpace.removeAllLoadPatternsFromDomain()
    modelSpace.preprocessor.getDomain.revertToStart()
    modelSpace.addLoadCaseToDomain(l)
    result = modelSpace.analyze(calculateNodalReactions=False)
    if(result != 0):
        quit()
    result = modelSpace.analyze(calculateNodalReactions=True)
    # Rx= 0.0;
    # Ry= 0.0;
    # Rz= 0.0;
    # for p in supportSet.getPoints:
    #     axes= getPointAxes(p.getPos)
    #     pointId= axes[0]+stairTowerId+'-'+axes[1]+stairTowerId
    #     n= p.getNode()
    #     Rx= n.getReaction[0]
    #     Ry= n.getReaction[1]
    #     Rz= n.getReaction[2]
    #     writer.writerow([l, pointId, Rx/1e3, Ry/1e3, Rz/1e3])
    # oh.displayBlocks()
    # oh.displayFEMesh()
    # oh.displayLocalAxes()
    # oh.displayStrongWeakAxis()
    # oh.displayLoadVectors()
    oh.displayLoads()
    # oh.displayReactions()
    # oh.displayDispRot(itemToDisp='uX')
    # oh.displayDispRot(itemToDisp='uY')
    oh.displayDispRot(itemToDisp='uZ', defFScale=10)
# f.close()
