# -*- coding: utf-8 -*-
''' Compute the natural frequencies of the structure.'''

from solution import predefined_solutions

exec(open('./xc_model.py').read())
# Loads
loadCaseManager= lcm.LoadCaseManager(preprocessor)
loadCaseNames= ['hLoadX','vLoadZ']
loadCaseManager.defineSimpleLoadCases(loadCaseNames)

## Set non-linear analysis.
modelSpace.analysis= predefined_solutions.penalty_newton_raphson(modelSpace.preprocessor.getProblem)

## Horizontal x load (to estimate structure stiffness).
cLC= loadCaseManager.setCurrentLoadCase('hLoadX')

### Horizontal load in structure
massFactor= 1.0
hLoadXVector= xc.Vector([-massFactor,0.0,0.00])
modelSpace.createSelfWeightLoad(allMemberSet,hLoadXVector)


# Natural frequency x-direction.

modelSpace.removeAllLoadPatternsFromDomain()
modelSpace.addLoadCaseToDomain('hLoadX')
result= modelSpace.analyze(calculateNodalReactions= True)

oh = output_handler.OutputHandler(modelSpace)
oh.displayDispRot(itemToDisp='uX', defFScale=50)

# Max displacement.
maxz = h_col + dy
topPoint = modelSpace.getNearestPoint(geom.Pos3d(0.0, 0.0, maxz))
uX = topPoint.getNode().getDisp[0]


# Total force.
Rx = 0.0
for p in supportSet.getPoints:
    n = p.getNode()
    Rx -= n.getReaction[0]

# Mass.
M = Rx/massFactor

# x-stiffness.
Kx = Rx/uX

# natural frequency
wx = math.sqrt(Kx/M)
Tx = 2.0*math.pi/wx
fx = 1/Tx


# vertical z load (to estimate structure stiffness).
cLC = loadCaseManager.setCurrentLoadCase('vLoadZ')

# Horizontal load in structure
# modelSpace.removeAllLoadPatternsFromDomain()
massFactor = 9.81
vLoadXVector = xc.Vector([0, 0.0, massFactor])
modelSpace.createSelfWeightLoad(allMemberSet, vLoadXVector)


# Natural frequency x-direction.
modelSpace.removeAllLoadPatternsFromDomain()
modelSpace.addLoadCaseToDomain('vLoadZ')
result = modelSpace.analyze(calculateNodalReactions=True)

oh.displayDispRot(itemToDisp='uZ', defFScale=50)


def designResponseSpectrum(T):
    retval = 9.81  # g (m/s2)
    if(T < 0.12):
        retval *= 0.0907*(0.4+0.6*T/0.12)
    elif(T < 0.6):
        retval *= 0.0907
    else:
        retval *= 0.0544/T
    return retval


quakeAccelX = designResponseSpectrum(Tx)
# quakeAccelY = designResponseSpectrum(Ty)

print('uX= ', uX*1e3, 'mm')
print('Rx= ', Rx/1e3, 'kN')
print('M= ', M, 'kg')
print('Kx= ', Kx/1e3, 'kN/m')
print('w_x= ', wx, 'rad/s')
print('T_x= ', Tx, 's')
print('f_x= ', fx, 'Hz')
print('quakeAccelX= ', quakeAccelX, 'm/s2')