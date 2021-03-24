# -*- coding: utf-8 -*-

''' Design for stability according to chapter C of AISC 360-16.'''

from __future__ import division
from __future__ import print_function

import math
import xc_base
import geom
from materials.astm_aisc import AISC_limit_state_checking as aisc
import base_plate_design as bpd
from postprocess.reports import export_internal_forces as eif
from solution import predefined_solutions
from colorama import Fore
from colorama import Style
from misc_utils import log_messages as lmsg

# Imperfections
def setImperfectionsXY(nodeSet, slopeX= 1.0/500.0, slopeY= 1.0/500.0):
    '''Set the initial imperfection of the model.

    :param nodeSet: set which nodes will be moved.
    :param slopeX: out of plumbness on x axis.
    :param slopeY: out of plumbness on y axis.
    '''
    if(abs(slopeX)<1.0/500.0):
        print('small imperfection on X.')
    if(abs(slopeY)<1.0/500):
        print('small imperfection on Y.')
    zMin= 1e6
    zMax= -1e6
    maxValue= 0.0
    for n in nodeSet.nodes:
        pos= n.getInitialPos3d
        zMin= min(zMin,pos.z)
        zMax= max(zMax,pos.z)
    for n in nodeSet.nodes:
        pos= n.getInitialPos3d
        h= pos.z-zMin
        deltaX= h*slopeX
        deltaY= h*slopeY
        maxValue= max(maxValue, deltaX**2+deltaY**2)
        newPos= pos+geom.Vector3d(deltaX,deltaY,0.0)
        n.setPos(newPos)
    return math.sqrt(maxValue)

def setImperfectionsX(nodeSet, slopeX= 1.0/500.0):
    '''Set the initial imperfection of the model.

    :param nodeSet: set which nodes will be moved.
    :param slopeY: out of plumbness on y axis.
    '''
    setImperfectionsXY(nodeSet, slopeX, 0.0)

def setImperfectionsY(nodeSet, slopeY= 1.0/500.0):
    '''Set the initial imperfection of the model.

    :param nodeSet: set which nodes will be moved.
    :param slopeY: out of plumbness on y axis.
    '''
    setImperfectionsXY(nodeSet, 0.0, slopeY)

# Model softening

def backupStiffness(elementSet):
    ''' Keeps the original youn modulus value in a property
        to retrieve it in subsequent calls to softenElements.

    :param elementSet: elements to process.
    '''
    for e in elementSet.elements:
        Ebackup= 0.0
        if(hasattr(e,"getMaterial")): # Trusses
            Ebackup= e.getMaterial().E
        else: # Beam elements.
            mat= e.getPhysicalProperties.getVectorMaterials[0]
            Ebackup= mat.sectionProperties.E
            e.setProp('IyBackup', mat.sectionProperties.Iy)
            e.setProp('IzBackup', mat.sectionProperties.Iz)
        e.setProp('Ebackup',Ebackup)
        
def softenElements(elementSet):
    ''' Adjust the stiffnes of the elements according to 
        clause C2.3 of AISC 360-16.

    :param elementSet: elements to soften.
    '''
    for e in elementSet.elements:
        Ebackup= e.getProp('Ebackup')
        if(e.isAlive):
            Pr= e.getN()
            if(hasattr(e,"getMaterial")): # Trusses
                mat= e.getMaterial()
                mat.E= 0.8*Ebackup
            else: # Beam elements.
                mat= e.getPhysicalProperties.getVectorMaterials[0]
 #               print('mat= ',mat.name)
                mat.sectionProperties.E= .8*Ebackup # Axial stiffness
                #print('properties: ', e.getPropNames())
                crossSection= e.getProp('crossSection')
                slenderness= crossSection.compressionSlendernessCheck()
                sClassif= aisc.SectionClassif.noncompact
                if(slenderness>=1.0):
                    sClassif= aisc.SectionClassif.slender
                # C2.3 (b) clause (flexural stiffness): 
                Pns= crossSection.getReferenceCompressiveStrength(sectionClassif= sClassif)
                ratio= abs(Pr)/Pns
                tau= 1.0
                if(ratio>0.5):
                    print('Pr= ', Pr/1e3, ' kN, Pns= ', Pns/1e3,' kN, ratio= ', ratio)
                    tau= 4*ratio*(1-ratio)
                    mat.sectionProperties.Iy= tau*e.getProp('IyBackup')
                    mat.sectionProperties.Iz= tau*e.getProp('IzBackup')

def restoreStiffness(elementSet):
    ''' Restore the original Young modulus value in a property
        to retrieve it in subsequent calls to softenElements.

    :param elementSet: elements to process.
    '''
    for e in elementSet.elements:
        Ebackup= e.getProp('Ebackup')
        if(hasattr(e,"getMaterial")): # Trusses
            e.getMaterial().E= Ebackup
        else: # Beam elements.
            mat= e.getPhysicalProperties.getVectorMaterials[0]
            mat.sectionProperties.E= Ebackup
            IyBackup= e.getProp('IyBackup')
            IzBackup= e.getProp('IzBackup')
            mat.sectionProperties.Iy= IyBackup
            mat.sectionProperties.Iz= IzBackup

def removeCompressedDiagonals(modelSpace, diagonalSet):
    ''' Remove the diagonals in compression.'''
#     if modelSpace.preprocessor.getSets.exists('compressDiag'):
#         modelSpace.preprocessor.getSets.removeSet('compressDiag') 
#     compressDiag= modelSpace.preprocessor.getSets.defSet('compressDiag')
#     for e in diagonalSet.elements:
#         if e.getN()<0:
# #                print e.getN()
#             compressDiag.getElements.append(e)
#     modelSpace.deactivateElements(compressDiag)
    pass

def resetCompressedDiagonals(modelSpace):
    ''' Put back compressed diagonals (at the end of the
        calculation loop).'''
    if modelSpace.preprocessor.getSets.exists('compressDiag'):
        compressDiag= modelSpace.preprocessor.getSets.defSet('compressDiag')
        modelSpace.activateElements(compressDiag)
        modelSpace.preprocessor.getSets.removeSet('compressDiag') 

def calcInternalForces(modelSpace, calcSet, steelMembers, diagonalSet, lstSteelBeams, loadCombinations, limitState, baseNodes, writer, mxNumIter= 10, convergenceTestTol= 1e-4):
    ''' Compute internal forces (solve).

    :param modelSpace: model space of the problem.
    :param calcSet: element set to compute internal forces on.
    :param steelMembers: steel members to be "softened" according to 
                         clause C2.3 of AISC 360-16.
    :param diagonalSet: diagonals to be deactivated when compressed.
    :param lstSteelBeams: list of members that need to update their 
                          lateral buckling reduction factors. 
    :param loadCombinations: load combinations to use.
    :param limitState: limit state to compute internal forces for.
    :param baseNodes: nodes attached to the foundation.
    :param writer: comma separated values writer to use for 
                   writing reactions.
    :ivar mxNumIter: maximum number of iterations (defauts to 10)
    :ivar convergenceTestTol: convergence tolerance (defaults to 1e-9)
    '''
    # Non linear analysis
    modelSpace.analysis= predefined_solutions.penalty_newton_raphson(modelSpace.preprocessor.getProblem,mxNumIter, convergenceTestTol)
    # Element to deal with
    elemSet= calcSet.elements
    nodSet= calcSet.nodes
    limitState.createOutputFiles()
    internalForcesDict= dict()
    failedCombinations= list()
    for key in loadCombinations.getKeys():
        comb= loadCombinations[key]
        print(comb.name)
        resetCompressedDiagonals(modelSpace)
        modelSpace.preprocessor.resetLoadCase()
        restoreStiffness(steelMembers)
        modelSpace.preprocessor.getDomain.revertToStart()
        #Solution
        print('first round A.')
        comb.addToDomain(['DL','LL']) # Add the first part of the combination.
        result= modelSpace.analyze(calculateNodalReactions= False)
        if(result!=0):
            quit()
            failedCombinations.append(comb.name)
        #Solution
        print('first round B.')
        comb.addToDomain() # Combination to analyze.
        result= modelSpace.analyze(calculateNodalReactions= False)
        if(result!=0 or not comb.isActive()):
            quit()
            failedCombinations.append(comb.name)
#        out.displayIntForcDiag('N',diagonal)
        removeCompressedDiagonals(modelSpace, diagonalSet)
        print('second round.')
        result= modelSpace.analyze(calculateNodalReactions= False)
        if(result!=0):
            quit()
            failedCombinations.append(comb.name)
        softenElements(steelMembers)
        print('third round.')
        result= modelSpace.analyze(calculateNodalReactions= True)
        if(result!=0):
            quit()
            failedCombinations.append(comb.name)
        bpd.exportULSReactions(writer, comb.name, baseNodes)
        if lstSteelBeams:
            for sb in lstSteelBeams:
                sb.updateReductionFactors()
#        out.displayIntForcDiag('N',diagonal)
        #Writing results.
        internalForcesDict.update(eif.getInternalForcesDict(comb.getName,elemSet))
        limitState.writeDisplacements(comb.getName,nodSet)
        comb.removeFromDomain() #Remove combination from the model.
    limitState.writeInternalForces(internalForcesDict)
    if(len(failedCombinations)>0):
        lmsg.error('Analysis failed in the following combinations: '+str(failedCombinations))
    else:
        print(Fore.GREEN+'Analysis for combinations for '+str(limitState.label)+': '+str(loadCombinations.getKeys())+' finished.\n'+Style.RESET_ALL)
