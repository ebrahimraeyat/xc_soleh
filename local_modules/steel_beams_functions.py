# -*- coding: utf-8 -*-
from __future__ import print_function
from materials.ec3 import EC3Beam as ec3b
from materials.ec3 import EC3_limit_state_checking as EC3lsc
from materials.astm_aisc import ASTM_materials
from materials.astm_aisc import AISC_limit_state_checking as aisc


# ** Steel beams
# Support coefficients (1==free, 0.5==prevented) (all default to 1)
# ky: lateral bending, kw: warping, k1: warping and lateral bending at left
# end, k2:  warping and lateral bending at right end
supCf_free=EC3lsc.SupportCoefficients(ky=1.0,kw=1.0,k1=1.0,k2=1.0)
supCf=EC3lsc.SupportCoefficients(ky=1.0,kw=1.0,k1=0.5,k2=1.0)

def gen_EC3beams_from_lstSets(lstSets,mat,sectClass,suppCoef,prefName):
    '''Return a list of EC3beams generated from each set in lstSet

    :param lstSets: list of sets, each set contains the lines to generate 
                    one EC3beam
    :param mat: material for all beams
    :param sectClass: section class for all beams
    :param suppCoef: support coefficients for all beams
    :param prefName: prefix for the beam names
    '''
    
    lstEC3beams=list()
    for i in range(len(lstSets)):
        lstSets[i].fillDownwards()
        lstLin=[l for l in lstSets[i].lines]
        nmBeam=prefName+str(i)
        lstEC3beams.append(ec3b.EC3Beam(nmBeam,mat,sectClass,suppCoef,lstLines=lstLin))
        lstEC3beams[-1].setControlPoints()
        lstEC3beams[-1].installULSControlRecorder("element_prop_recorder")
    return lstEC3beams

def gen_EC3beams_from_SetLines(setLines,mat,sectClass,suppCoef,prefName):
    '''Return a list of EC3beams generated from each line in setLines

    :param setLines: set of lines, each line generates one EC3beam
    :param mat: material for all beams
    :param sectClass: section class for all beams
    :param suppCoef: support coefficients for all beams
    :param prefName: prefix for the beam names
    '''
    setMng=setLines.getPreprocessor.getSets
    lstEC3beams=list()
    cont=0
    for l in setLines.lines:
        nmBeam=prefName+str(cont)
        lstEC3beams.append(ec3b.EC3Beam(nmBeam,mat,sectClass,suppCoef,lstLines=[l]))
        lstEC3beams[-1].setControlPoints()
        lstEC3beams[-1].installULSControlRecorder("element_prop_recorder")
    return lstEC3beams

def gen_AISCbeams_from_SetLines(setLines,mat,prefName):
    '''Return a list of AISCbeams generated from each line in setLines

    :param setLines: set of lines, each line generates one AISCbeam
    :param mat: material for all beams
    :param prefName: prefix for the beam names
    '''
    setMng=setLines.getPreprocessor.getSets
    lstAISCbeams=list()
    cont=0
    for l in setLines.lines:
        nmBeam=prefName+str(cont)
        beamLength=l.getLength()
        lstAISCbeams.append(aisc.Member(name=nmBeam,section=mat,unbracedLengthX=beamLength,lstLines=[l]))
        lstAISCbeams[-1].installULSControlRecorder("element_prop_recorder")
        print('Member:'+ nmBeam + ', length=' + str(beamLength))
        cont+=1
    return lstAISCbeams

def gen_AISCbeams_from_lineSet(lineSet,mat,beamName):
    '''Return a list with a single AISCbeam generated from all the lines included in lineSet

    :param lineSet: set of lines to generate one AISCbeam
    :param mat: material for all beams
    :param beamName: beam name
    '''
    lstOneBeam=list()
    lineSet.fillDownwards()
    lstLin=[l for l in lineSet.lines]
    beamLength=0
    for l in lstLin: beamLength+=l.getLength()
    print('Member:'+ beamName + ', length=' + str(beamLength))
    lstOneBeam.append(aisc.Member(name=beamName, section=mat,unbracedLengthX=beamLength, lstLines=lstLin))
    lstOneBeam[-1].installULSControlRecorder("element_prop_recorder")
    return lstOneBeam

def gen_AISCbeams_from_lstSets(lstSets,mat,prefName):
    '''Return a list of AISCbeams generated from each set in lstSet

    :param lstSets: list of sets, each set contains the lines to generate 
                    one AISCbeam
    :param mat: material for all beams
    :param prefName: prefix for the beam names
    '''
    lstAISCbeams=list()
    for i in range(len(lstSets)):
        nmBeam=prefName+str(i)
        lstAISCbeams+=gen_AISCbeams_from_lineSet(lstSets[i],mat,nmBeam)
    return lstAISCbeams

def gen_AISCbeams_from_lstRangXYZ(preprocessor,grid,lstRangXYZ,mat,prefName,startIndex=0):
    '''Return a list of AISCbeams; each AISCbeam is generated 
    from the lines included in one of the XYZ-ranges in list lstRangXYZ

    :param grid: grid model where to find lines
    :param lstRangXYZ: list of XYZ-ranges, each range contains the lines 
                       to generate one AISCbeam.
    :param mat: material for all beams
    :param prefName: prefix for the beam names
    '''
    lstAISCbeams=list()
    for i in range(len(lstRangXYZ)):
        nmBeam=prefName+str(startIndex+i)
        if preprocessor.getSets.exists('setLin') : preprocessor.getSets.removeSet('setLin') 
        setLin=grid.getSetLinOneXYZRegion(lstRangXYZ[i],'setLin')
        lstAISCbeams+=gen_AISCbeams_from_lineSet(setLin,mat,nmBeam)
    return lstAISCbeams

def  gen_AISCbeams_from_sets_based_on_lstRangXYZ(preprocessor,grid,lstSets,mat,prefName):       
    '''For each set in lstSets defined from a list of XYZranges:
    Return a list of AISCbeams; each AISCbeam is generated
    from the lines included in one of the XYZ-ranges in list lstRangXYZ

    :param grid: grid model where to find lines
    :param lstSets: list of sets generated from XYZ-ranges, each range 
                    contains the lines 
                    to generate one AISCbeam.
    :param mat: material for all beams
    :param prefName: prefix for the beam names
    '''
    lstAISCbeams=list()
    startIndex=0
    for stlin in lstSets:
        lstRangXYZ=stlin.lstRangXYZ
        lstAISCbeams+=gen_AISCbeams_from_lstRangXYZ(preprocessor,grid,lstRangXYZ,mat,prefName,startIndex)
        startIndex+=len(lstRangXYZ)
        
