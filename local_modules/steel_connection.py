# -*- coding: utf-8 -*-

from __future__ import print_function
from __future__ import division

#import xc_base
import geom
import uuid
import xc
import math
from model.geometry import grid_model as gm
from materials import typical_materials as tm
from model.mesh import finit_el_model as fem
from model.sets import sets_mng as sets
from misc_utils import data_struct_utils as dsu
from materials.sections import section_properties as sectpr
import gen_functions as gf
from misc_utils import log_messages as lmsg
from materials.astm_aisc import ASTM_materials
from postprocess import output_handler
from solution import predefined_solutions
import steel_connection_reports as scr
import von_mises_nl_solution as nls

'''References:
[1] Steel connection analysis, by Paolo Rugarli
[2] Specification for Structural Steel Buildings,July 7, 2016
    American Institute of Steel Construction
'''
__author__= "Ana Ortega (AO_O) and Luis C. Pérez Tato (LCPT)"
__copyright__= "Copyright 2020, AO_O and LCPT"
__license__= "GPL"
__version__= "3.0"
__email__= "ana.ortega@ciccp.es l.pereztato@gmail.com"



class Bolt(object):
    '''Class intended to define a bolt by its diameter and material and 
    generate sets of bolts of this type and their radii elements (ref. [1]).
    These radii elements represent the bearing area between the bolt shaft and 
    the plate connected.

    :ivar diam: diameter of the bolt in meters
    :ivar mat: steel material
    '''
    def __init__(self,diam,mat):
        self.diam=diam
        self.R=round(self.diam/2,5)
        self.mat=mat
        self.sectMat=None
        
    def getBearStiff(self,tPlate):
        '''Return the bearing stiffness (k_be) due to the deformability of 
        the plate in the region near the contact area between bolt shaft and 
        plate connected (according to reference [1], page 245

        :param tPlate: plate thickness in meters.
        '''
        D_M16=16e-3 #16 mm
        k_be=22.5*tPlate/D_M16*self.diam*self.mat.fu
        return k_be

    def createBoltSectMat(self,prep):
        '''Creates the section-material to model bolt
        '''
        gsect=sectpr.CircularSection('gsect',self.diam)
        mName=str(uuid.uuid1())
        self.sectMat=tm.BeamMaterialData(mName+'_mat',gsect,self.mat)
        self.sectMat.setupElasticShear3DSection(prep)

    def createBolt(self,pntLst,setName):
        '''Creates the bolt elements and appends them to a set which 
        name is given as parameter.

        :param prep: preprocessor
        :param pntLst: list of ordered points that define the bolt 
        :param setName: name of the set to which append the bolt elements
                        (set must be created previously)

        '''
        prep=pntLst[0].getPreprocessor
        nodes=prep.getNodeHandler
        elements=prep.getElementHandler
        # if not prep.getSets.exists(setName):
        #     retSet=prep.getSets.defSet(setName)
        # else:
        #     retSet=prep.getSets.getSet(setName)
        retSet=prep.getSets.getSet(setName)
        if not self.sectMat:
            self.createBoltSectMat(prep)
#        nodLst=[nodes.newNodeXYZ(p.getPos.x,p.getPos.y,p.getPos.z) for p in pntLst]
        for p in pntLst: p.genMesh(xc.meshDir.I)
        nodLst=[p.getNode() for p in pntLst]
        linname= str(uuid.uuid1())
        lin=prep.getTransfCooHandler.newLinearCrdTransf3d(linname)
        lin.xzVector=gf.getSuitableXZVector(nodLst[0],nodLst[1])
        elements.defaultTransformation= lin.name
        elements.defaultMaterial=self.sectMat.name
        for i in range(len(nodLst)-1):
            e=elements.newElement("ElasticBeam3d",xc.ID([nodLst[i].tag,nodLst[i+1].tag]))
            retSet.elements.append(e)
        retSet.fillDownwards()
#        return retSet

    def getRadiusSectMat(self,prep,tPlate):
        '''Return the material-section to generate the radii elements.
        A square section is generated so that its stiffness is 
        equivalent to 0.25 times the bearing stiffness (k_be) (page 466 ref. [1])

        :param tPlate: thickness of the plate.
        '''
        k_be=self.getBearStiff(tPlate)
        A=0.25*k_be/self.mat.E
        l=math.sqrt(A)
        gsectR=sectpr.RectangularSection('gsectR',l,l)
        mRname=str(uuid.uuid1())
        radMat=tm.BeamMaterialData(mRname+'_Rmat',gsectR,self.mat)
        radMat.setupElasticShear3DSection(prep)
        return radMat

    def getMatsRelease(self,prep,tPlate):
        '''Return the six materials of the zero-length elements that 
        define the releases in the radii bearing elements.
        The in-plane stiffness is set as 0.25*k_be, the out-of-plane
        stiffness is set as 25*k_be. The bending stiffness is near null
        '''
        KX=0.25*self.getBearStiff(tPlate)
        KY=KX/10
        KZ=10*KX
        KrotX=KX*10
        KrotY=KX*10
        KrotZ=KX/10
        matKX=tm.defElasticMaterial(prep,'matKX',KX)
        matKY=tm.defElasticMaterial(prep,'matKY',KY)
        matKZ=tm.defElasticMaterial(prep,'matKZ',KZ)
        matKrotX=tm.defElasticMaterial(prep,'matKrotX',KrotX)
        matKrotY=tm.defElasticMaterial(prep,'matKropY',KrotY)
        matKrotZ=tm.defElasticMaterial(prep,'matKrotZ',KrotZ)
        return [matKX,matKY,matKZ,matKrotX,matKrotY,matKrotZ]
         
    def generateRadii(self,tPlate,pntBolt,pntHoleLst,setRadii=None):
        '''Return the eight bearing elements (radii) to model the bolt hole 

        :param tPlate: plate thickness
        :param pntBolt: point of the bolt
        :param pntHoleLst: list of points of the hole
        :param radiiSet: set where to append the radii 
                         (defaults to None, radii are created but not
                          appended to any set)
        '''
        prep=pntBolt.getPreprocessor
        nodes=prep.getNodeHandler
        elements=prep.getElementHandler
        pb=pntBolt.getPos
#        boltNode=boltSet.getNodes.getNearestNode(pb)
        boltNode=pntBolt.getNode()
#        holeNodes=[plateSet.getNodes.getNearestNode(p.getPos) for p in pntHoleLst]
        holeNodes=[p.getNode() for p in pntHoleLst]
        radMat=self.getRadiusSectMat(prep,tPlate)
        releaseMats=self.getMatsRelease(prep,tPlate)
        releaseMatsNames=[mat.name for mat in releaseMats]
        # first bearing element only end release
        hnod=holeNodes[0]  #hole node
        ph=hnod.getInitialPos3d
        vx=xc.Vector([ph.x-pb.x,ph.y-pb.y,ph.z-pb.z])
        vx=vx.Normalized()
        phaux=holeNodes[1].getInitialPos3d
        vaux=xc.Vector([phaux.x-pb.x,phaux.y-pb.y,phaux.z-pb.z])
        vz=gf.cross(vx,vaux)
        vz=vz.Normalized()
        vy=gf.cross(vx,vz)
        linname= str(uuid.uuid1())
        lin=prep.getTransfCooHandler.newLinearCrdTransf3d(linname)
        lin.xzVector=vz
        elements.defaultTransformation= lin.name
        elements.defaultMaterial=radMat.name
        n2=nodes.newNodeXYZ(ph.x,ph.y,ph.z)
        e=elements.newElement("ElasticBeam3d",xc.ID([boltNode.tag,hnod.tag]))
        gf.setBearingBetweenNodes(prep,n2.tag,hnod.tag,releaseMatsNames,[vx,vy])
        if setRadii:  setRadii.elements.append(e)
        # seven radii released at both extremities
        for i in range(1,8):
            hnod=holeNodes[i]
            ph=hnod.getInitialPos3d
            vx=xc.Vector([ph.x-pb.x,ph.y-pb.y,ph.z-pb.z])
            vx=vx.Normalized()
            vy=gf.cross(vx,vz)
            n1=nodes.newNodeXYZ(pb.x,pb.y,pb.z)
            n2=nodes.newNodeXYZ(ph.x,ph.y,ph.z)
            gf.setBearingBetweenNodes(prep,boltNode.tag,n1.tag,releaseMatsNames,[vx,vy])
            elements.defaultTransformation= lin.name
            elements.defaultMaterial=radMat.name
            e=elements.newElement("ElasticBeam3d",xc.ID([n1.tag,n2.tag]))
            gf.setBearingBetweenNodes(prep,n2.tag,hnod.tag,releaseMatsNames,[vx,vy])
            if setRadii:  setRadii.elements.append(e)

    
#Welding classes
AISI_304L=ASTM_materials.ASTMSteel(name='AISI-304L', fy= 216e6, fu= 546e6, gammaM= 1.0)  # not an ASTM steel, it's a stainless steel 
AISI_304L.E=200e9
E7018=ASTM_materials.ASTMSteel(name='E7018', fy= 400e6, fu= 490e6, gammaM= 1.0) #filler metal used for weldings (see properties in AWS D1.1/D1, (It's not an ASTM steel, change the definition in a next revision)
AWS_E308L_15=ASTM_materials.ASTMSteel(name='AWS-E308L-15',fy=430e6,fu=520e6, gammaM=1.0)  # filler metal used for weldings in stainless steel
AWS_E308L_15.E=200e9
AWS_E308L_15.nu=0.3

class WeldTyp(object):
    '''Define the basic parameters of a weld, that will be used to
    generate fillet or penetration seam welds, by using classes 
    FilletWeld, MultiFilletWeld or PenetrationWeld.

    :param weldSz: weld size (leg dimension or actual throat) (t)
    :param weldMetal: weld metal
    :param weldThroat: weld throat thickness (a) (defaults to None, in
                       which case it's calculated for 90º)
    '''
    def __init__(self,weldSz,weldMetal,weldThroat=None):
        self.weldSz=weldSz
        self.weldMetal=weldMetal
        if not weldThroat:
            self.weldThroat=self.weldSz/math.sqrt(2)
        else:
            self.weldThroat=weldThroat
    
    
class BaseWeld(object):
    '''Generation and verifications of a straight weld
    :param weldTyp: instance of class WeldTyp that defines the generic
                    parameters:

                    - weldSz: weld size (leg dimension or actual throat) (t)
                    - weldMetal: weld metal
                    - weldThroat: weld throat thickness (a)

    :param setWS1: set with the elements of the welding surface 1
    :param setWS2: set with the elements of the welding surface 2
    :param setName: name of the set of weld elements
    :param descr: description (defaults to '')
    :param weldExtrPoints: [P1, P2] XC-points or Pos3d at the extremities of the 
                           weld bead in the intersection of the two welding surfaces.
                            If not given, the geometric definition will be given by 
                           a line using attribute weldLine. (defaults to [])
    :param weldLine: XC-line or Segment3d along the weld bead (defaults to None)
    '''
    
    def __init__(self,weldTyp,setWS1,setWS2,setName=None,descr='',weldExtrPoints=[],weldLine=None):
        self.weldSz=weldTyp.weldSz
        self.weldMetal=weldTyp.weldMetal
        self.weldThroat=weldTyp.weldThroat
        self.setWS1=setWS1
        self.setWS2=setWS2
        self.setName=setName
        self.descr=descr
        self.weldExtrPoints=weldExtrPoints
        self.weldLine=weldLine
        self.weldSet=None
 
    def generateWeld(self,weldElSz,distWeldEl_WS1,nDiv=None,WS1sign=1,WS2sign=1):
        '''Generates nDiv+1 points of welding along the weld seam. At each point 
        creates two rigid offset elements and a weld element according to page 
        455 of reference [1].
        The welding elements are included in a set for further verification.

        :param weldElSz: size of the elements «weld» (=weldSz/2 for 
                         fillet welds,  =weldSz for penetration welds)
        :param distWeldEl_WS1: distance between the weld element and 
                        the middle surface of WS1
                        (=tWS1/2+weldSz/2 for fillet welds,
                         =tWS1/4 for penetration welds)
        :param fictE: fictitious Young's modulus for calculating tension stiffness
                      of weld elements (pages 457 and 460 of reference [1])
                      (=546.fu for fillet welds, =E for penetration welds)
        :param fictG: fictitious shear modulus for calculating shear stiffness of
                      weld elements (pages 457 and 460 of reference [1]).
                      (=546.fu for fillet welds, =G for penetration welds)

        :param nDiv: number of divisions in the weld bead to insert elements.
                     If None, elements are placed at a distance of weldSz
                     (defaults to None)
        :param WS1sign: face of welding surface 1 to place the weld 
                        1 for positive face, -1 for negative face (defaults to 1)
        :param WS2sign: face of welding surface 2 to place the weld 
                        1 for positive face, -1 for negative face (defaults to 1)
        '''
        prep= self.setWS1.getPreprocessor
        pnts=prep.getMultiBlockTopology.getPoints
        nodes= prep.getNodeHandler
        elements= prep.getElementHandler
        if len(self.weldExtrPoints)>1:
            if self.weldExtrPoints[0].type()=='XC::Pnt': 
                self.weldP1=self.weldExtrPoints[0].getPos
            else:
                self.weldP1=self.weldExtrPoints[0]
            if self.weldExtrPoints[1].type()=='XC::Pnt': 
                self.weldP2=self.weldExtrPoints[1].getPos
            else:
                self.weldP2=self.weldExtrPoints[1]
        elif self.weldLine:
            if self.weldLine.type()=='XC::Line':
                self.weldP1=pnts.get(self.weldLine.getKPoints()[0]).getPos
                self.weldP2=pnts.get(self.weldLine.getKPoints()[1]).getPos
            else:
                self.weldP1=self.weldLine.getFromPoint()
                self.weldP2=self.weldLine.getToPoint()
        else:
            lmsg.error('Missing geometric definition of weld '+ self.descr + ' two points or one line is needed')
        self.length=self.weldP1.dist(self.weldP2)
        if not nDiv: nDiv=int(round(self.length/(self.weldSz)))
        distWeldEl=self.length/nDiv
        if not self.setName: self.setName=str(uuid.uuid1())
        if prep.getSets.exists(self.setName):
            lmsg.warning('Set ',self.setName, ' already defined, check if weld elements should be in a new set')
        self.weldSet=prep.getSets.defSet(self.setName)

        # surfaces thickness
        self.tWS1=self.setWS1.getElements[0].getPhysicalProperties.getVectorMaterials[0].h   # thickness of surface 1is taken from only first element (constant thickness is supossed)
        self.tWS2=self.setWS2.getElements[0].getPhysicalProperties.getVectorMaterials[0].h   # thickness of surface 1is taken from only first element (constant thickness is supossed)
        self.minSz=ASTM_materials.getFilletWeldMinimumLegSheets(self.tWS1,self.tWS2)
        self.maxSz=ASTM_materials.getFilletWeldMaximumLegSheets(self.tWS1,self.tWS2)
        #elements on surfaces
        e1= self.setWS1.getNearestElement(self.weldP1)
        e2= self.setWS2.getNearestElement(self.weldP1)
        #vectors perpendicular to welding surfaces
        WS1sign=WS1sign/abs(WS1sign)
        WS2sign=WS2sign/abs(WS2sign)
        vps1=WS1sign*e1.getKVector3d(True)
        vps2=WS2sign*e2.getKVector3d(True)
        #extremity points and line in middle surface 1
        p1lWS1=self.weldP1+vps2*(self.tWS2/2.+self.weldSz/2.)
        p2lWS1=self.weldP2+vps2*(self.tWS2/2.+self.weldSz/2.)
        lWS1=geom.Segment3d(p1lWS1,p2lWS1)
        nod_lWS1=[(nodes.newNodeXYZ(pos.x,pos.y,pos.z)) for pos in lWS1.Divide(nDiv)]
        #extremity points and line in centroid of weld bead
        p1lW=p1lWS1+vps1*(distWeldEl_WS1)
        p2lW=p2lWS1+vps1*(distWeldEl_WS1)
        lW=geom.Segment3d(p1lW,p2lW)
        nod_lW=[(nodes.newNodeXYZ(pos.x,pos.y,pos.z)) for pos in lW.Divide(nDiv)]
        #extremity points and line in middle surface 2
        p1lWS2=self.weldP1+vps1*(distWeldEl_WS1)
        p2lWS2=self.weldP2+vps1*(distWeldEl_WS1)
        lWS2=geom.Segment3d(p1lWS2,p2lWS2)
        nod_lWS2=[(nodes.newNodeXYZ(pos.x,pos.y,pos.z)) for pos in lWS2.Divide(nDiv)]
        #extremity points and line on face of welding surface 2
        p1lFWS2=p1lWS2+vps2*(weldElSz)
        p2lFWS2=p2lWS2+vps2*(weldElSz)
        lFWS2=geom.Segment3d(p1lFWS2,p2lFWS2)
        nod_lFWS2=[(nodes.newNodeXYZ(pos.x,pos.y,pos.z)) for pos in lFWS2.Divide(nDiv)]

        #Cross section's properties
        L=lWS1.getLength()
        # fictitious moduli so that A.E=546.A.f_uw and A.G=546.A.f_u according to
        # sfiffness given in page 460 of reference [1]
        fictE=546*self.weldMetal.fu
        fictG=546*self.weldMetal.fu
        #  welding elements section
        A_w=L/nDiv*self.weldSz
        I_w=1/10*1/12*A_w**2
        sectWeldPr= xc.CrossSectionProperties3d()
        sectWeldPr.A=A_w; sectWeldPr.E=fictE ; sectWeldPr.G=fictG
        sectWeldPr.Iz=I_w ;  sectWeldPr.Iy=I_w ; sectWeldPr.J=I_w
        sectWeld=tm.defElasticSectionFromMechProp3d(prep, "sectWeld",sectWeldPr)
        # welding elements section in the extremities of the weld seam 
        sectWeldExtrPr=xc.CrossSectionProperties3d()
        sectWeldExtrPr.A=A_w/2.; sectWeldExtrPr.E=fictE ; sectWeldExtrPr.G=fictG
        sectWeldExtrPr.Iz=I_w/2. ;  sectWeldExtrPr.Iy=I_w/2. ; sectWeldExtrPr.J=I_w/2.
        sectWeldExtr=tm.defElasticSectionFromMechProp3d(prep, "sectWeldExtr",sectWeldExtrPr)
        #rigid elements section
        A_r=20*A_w
        I_r=1/12*A_r**2
        sectRigPr= xc.CrossSectionProperties3d()
        sectRigPr.A=A_r; sectRigPr.E=fictE ; sectRigPr.G=fictG
        sectRigPr.Iz=I_r ;  sectRigPr.Iy=I_r ; sectRigPr.J=I_r
        sectRig=tm.defElasticSectionFromMechProp3d(prep, "sectRig",sectRigPr)

         #rigid elements section  in the extremities of the weld seam 
        sectRigExtrPr=xc.CrossSectionProperties3d()
        sectRigExtrPr.A=A_r/2.; sectRigExtrPr.E=fictE ; sectRigExtrPr.G=fictG
        sectRigExtrPr.Iz=I_r/2. ;  sectRigExtrPr.Iy=I_r/2. ; sectRigExtrPr.J=I_r/2.
        sectRigExtr=tm.defElasticSectionFromMechProp3d(prep, "sectRigExtr",sectRigExtrPr)
        #linear transformation
        linname= str(uuid.uuid1())
        lin=prep.getTransfCooHandler.newLinearCrdTransf3d(linname)
        lin.xzVector= xc.Vector(vps1.cross(vps2))
        # set of rigid elements to glue to surface 1
        elements.defaultTransformation= lin.name
        elements.defaultMaterial=sectRigExtr.name
        e=elements.newElement("ElasticBeam3d",xc.ID([nod_lWS1[0].tag,nod_lW[0].tag]))
        e=elements.newElement("ElasticBeam3d",xc.ID([nod_lWS1[-1].tag,nod_lW[-1].tag]))
        elements.defaultMaterial=sectRig.name
        for i in range(1,nDiv):
            e=elements.newElement("ElasticBeam3d",xc.ID([nod_lWS1[i].tag,nod_lW[i].tag]))
        # set of rigid elements to glue to surface 2
        elements.defaultTransformation= lin.name
        elements.defaultMaterial=sectRigExtr.name
        e=elements.newElement("ElasticBeam3d",xc.ID([nod_lWS2[0].tag,nod_lFWS2[0].tag]))
        e=elements.newElement("ElasticBeam3d",xc.ID([nod_lWS2[-1].tag,nod_lFWS2[-1].tag]))
        elements.defaultMaterial=sectRig.name
        for i in range(1,nDiv):
            e=elements.newElement("ElasticBeam3d",xc.ID([nod_lWS2[i].tag,nod_lFWS2[i].tag]))
        # set of welding elemets
        #  extremity elements
        elements.defaultTransformation= lin.name
        elements.defaultMaterial=sectWeldExtr.name
        e=elements.newElement("ElasticBeam3d",xc.ID([nod_lFWS2[0].tag,nod_lW[0].tag]))
        e.setProp('ass_wL',distWeldEl/2.)
        self.weldSet.elements.append(e)
        e=elements.newElement("ElasticBeam3d",xc.ID([nod_lFWS2[-1].tag,nod_lW[-1].tag]))
        e.setProp('ass_wL',distWeldEl/2.)
        self.weldSet.elements.append(e)
        elements.defaultMaterial=sectWeld.name
        for i in range(1,nDiv):
            e=elements.newElement("ElasticBeam3d",xc.ID([nod_lFWS2[i].tag,nod_lW[i].tag]))
            e.setProp('ass_wL',distWeldEl)
            self.weldSet.elements.append(e)
        # glue rigid elements to plates
        gluedDOFs=[0,1,2,3,4,5]
        for n in nod_lWS1:
            nodePos= n.getInitialPos3d
            e=self.setWS1.getNearestElement(nodePos)
            dist= e.getDist(nodePos, True)
            glue=prep.getBoundaryCondHandler.newGlueNodeToElement(n,e,xc.ID(gluedDOFs))
        for n in nod_lWS2:
            nodePos= n.getInitialPos3d
            e=self.setWS2.getNearestElement(nodePos)
            dist= e.getDist(nodePos, True)
            glue=prep.getBoundaryCondHandler.newGlueNodeToElement(n,e,xc.ID(gluedDOFs))
        self.weldSet.fillDownwards()
        
    def getTotalIntForc(self):
        '''Return the total forces in directions parallel and perpendiculars to
        the weld seam for the calculated load case.
        '''
#        Fpar=0 ; Fperp1=0 ; Fperp2=0
        Fpar=0 ; Fperp=0
        for e in self.weldSet.elements:
            Fpar+=e.getVz()
            Fperp1=e.getN()
            Fperp2=e.getVy()
            Fperp+=math.sqrt(Fperp1**2+Fperp2**2)
#        Fperp=math.sqrt(Fperp1**2+Fperp2**2)
        return (Fpar,Fperp)


class FilletWeld(BaseWeld):
    '''Generation and verifications of a straight weld
    :param weldTyp: instance of class WeldTyp that defines the generic
                    parameters:

                    - weldSz: weld size (leg dimension or actual throat) (t)
                    - weldMetal: weld metal
                    - weldThroat: weld throat thickness (a)

    :param setWS1: set with the elements of the welding surface 1
    :param setWS2: set with the elements of the welding surface 2
    :param setName: name of the set of weld elements
    :param descr: description (defaults to '')
    :param weldExtrPoints: [P1, P2] XC-points or Pos3d at the extremities of the 
                           weld bead in the intersection of the two welding surfaces.
                            If not given, the geometric definition will be given by 
                           a line using attribute weldLine. (defaults to [])
    :param weldLine: XC-line or Segment3d along the weld bead (defaults to None)
    '''
    
    def __init__(self,weldTyp,setWS1,setWS2,setName=None,descr='',weldExtrPoints=[],weldLine=None):
        super(FilletWeld,self).__init__(weldTyp,setWS1,setWS2,setName,descr,weldExtrPoints,weldLine)
 
    def generateWeld(self,nDiv=None,WS1sign=1,WS2sign=1):
        '''Generates nDiv+1 points of welding along the weld seam. At each point 
        creates two rigid offset elements and a weld element according to page 
        455 of reference [1].
        The welding elements are included in a set for further verification.

        :param nDiv: number of divisions in the weld bead to insert elements.
                     If None, elements are placed at a distance of 2*weldSz
                     (defaults to None)

        :param WS1sign: face of welding surface 1 to place the weld 
                        1 for positive face, -1 for negative face (defaults to 1)
        :param WS2sign: face of welding surface 2 to place the weld 
                        1 for positive face, -1 for negative face (defaults to 1)
        '''
        prep=self.setWS1.getPreprocessor
        self.tWS1=self.setWS1.getElements[0].getPhysicalProperties.getVectorMaterials[0].h   # thickness of surface 1is taken from only first element (constant thickness is supossed)
        weldElSz=self.weldSz/2
        distWeldEl_WS1=self.tWS1/2+self.weldSz/2
        super(FilletWeld,self).generateWeld(weldElSz,distWeldEl_WS1,nDiv,WS1sign,WS2sign)
        
    def getWeldElemDesignStrength(self,weldEl,Fpar,Fperp):
        '''Return design strength of a weld element according
        to section J.2 of AISC (reference [2])
        '''
        if abs(Fpar) > 0:
            angleDir=math.atan(abs(Fperp/Fpar))
        else:
            angleDir=math.pi/2
        #directional strength increase
#        print('Fpar=', round(Fpar), ' Fperp=',round(Fperp), ' angleDir=',math.degrees(angleDir))
        dirSthIncr=1+0.5*(math.sin(angleDir))**1.5
        Fnw=0.6*self.weldMetal.fu*dirSthIncr
        Awe=weldEl.getProp('ass_wL')*self.weldThroat
        Rn_weldEl=Fnw*Awe
        return Rn_weldEl 
        
    def getCF_AISCverif(self,baseMetal,Phi=0.75):
        '''Return the capacity factor of the weld
        according to section J.2 of AISC (reference [2])

        :param baseMetal: base metal
        :param Phi: resistance factor (defaults to 0.75)
        '''
        sumCF=0
        for weldEl in self.weldSet.elements:
            Fpar=weldEl.getVz()
            Fperp1=weldEl.getN()
            Fperp2=weldEl.getVy()
            Fperp=math.sqrt(Fperp1**2+Fperp2**2)
            #Base metal design strength  (Sect. J2 AISC)
            A_BM=weldEl.getProp('ass_wL')*self.weldSz
            F_nBM=Phi*baseMetal.fu   #sect. J4-2 AISC)
            Rn_base=F_nBM*A_BM
            #Weld  design strengths  (Sect. J2 AISC)
            Rn_weldEl_V=self.getWeldElemDesignStrength(weldEl,Fpar,Fperp)
            #design shear internal forces
            V=math.sqrt(Fpar**2+Fperp**2)
            # Capacity factors
            Rn=min(Rn_base,Phi*Rn_weldEl_V)
            CFel=V/Rn
            sumCF+=CFel
#            print('elem:', weldEl.tag,' l=', round(weldEl.getProp('ass_wL'),4),' Rn_base=',round(Rn_base),' Rn_weldEl_V=',round(Rn_weldEl_V),' CF=',CFel)
        CF=sumCF/self.weldSet.elements.size
#        print('CF=',CF)
        return CF

class PenetrationWeld(BaseWeld):
    '''Generation and verifications of a straight weld
    :param weldTyp: instance of class WeldTyp that defines the generic
                    parameters:

                    - weldSz: weld size (leg dimension or actual throat) (t)
                    - weldMetal: weld metal
                    - weldThroat: weld throat thickness (a)

    :param setWS1: set with the elements of the welding surface 1
    :param setWS2: set with the elements of the welding surface 2
    :param setName: name of the set of weld elements
    :param descr: description (defaults to '')
    :param weldExtrPoints: [P1, P2] XC-points or Pos3d at the extremities of the 
                           weld bead in the intersection of the two welding surfaces.
                            If not given, the geometric definition will be given by 
                           a line using attribute weldLine. (defaults to [])
    :param weldLine: XC-line or Segment3d along the weld bead (defaults to None)
    '''
    
    def __init__(self,weldTyp,setWS1,setWS2,setName=None,descr='',weldExtrPoints=[],weldLine=None):
        super(PenetrationWeld,self).__init__(weldTyp,setWS1,setWS2,setName,descr,weldExtrPoints,weldLine)
 
    def generateWeld(self,nDiv=None,WS1sign=1,WS2sign=1):
        '''Generates nDiv+1 points of welding along the weld seam. At each point 
        creates two rigid offset elements and a weld element according to page 
        455 of reference [1].
        The welding elements are included in a set for further verification.

        :param nDiv: number of divisions in the weld bead to insert elements.
                     If None, elements are placed at a distance of 2*weldSz
                     (defaults to None)

        :param WS1sign: face of welding surface 1 to place the weld 
                        1 for positive face, -1 for negative face (defaults to 1)
        :param WS2sign: face of welding surface 2 to place the weld 
                        1 for positive face, -1 for negative face (defaults to 1)
        '''
        prep=self.setWS1.getPreprocessor
        self.tWS1=self.setWS1.getElements[0].getPhysicalProperties.getVectorMaterials[0].h   # thickness of surface 1is taken from only first element (constant thickness is supossed)
        weldElSz=self.weldSz
        distWeldEl_WS1=self.tWS1/4
        super(PenetrationWeld,self).generateWeld(weldElSz,distWeldEl_WS1,nDiv,WS1sign,WS2sign)
        

class MultiFilletWeld(object):
    ''''Generation and verifications of multiple welds

    :param weldTyp: instance of class WeldTyp that defines the generic
                    parameters:

                    - weldSz: weld size (leg dimension or actual throat) (t)
                    - weldMetal: weld metal
                    - weldThroat: weld throat thickness (a)
    :param setWS1: set with the elements of the welding surface 1
    :param setWS2: set with the elements of the welding surface 2
    :param setName: name of the set of weld elements
    :param lstLines: list of XC-lines or Segment3d (each line corresponding to one weld)
    :param genDescr: generic description (defaults to '')
    :param specDescr: list of specific description (each description
                      applies for the correspondig weld defined 
                      in lstLines), (defaults to [])
    '''
    def __init__(self,weldTyp,setWS1,setWS2,lstLines,setName=None,genDescr='',specDescr=[]):
        self.weldTyp=weldTyp
        self.setWS1=setWS1
        self.setWS2=setWS2
        self.setName=setName
        self.lstLines=lstLines
        self.genDescr=genDescr
        self.specDescr=specDescr
        self.lstWelds=list()

    def generateWeld(self,nDiv=None,WS1sign=1,WS2sign=1,bothSidesOfWS1=False,bothSidesOfWS2=False):
        ''''Generates nDiv+1 points of welding along each line. At each point 
        creates two rigid offset elements and a weld element according to page 
        455 of reference [1].
        The welding elements are included in a set for further verification.

        :param nDiv: number of divisions in the weld bead to insert elements.
                     If None, elements are placed at a distance of 2*weldSz
                     (defaults to None)
        :param WS1sign: face of welding surface 1 to place the weld 
                        1 for positive face, -1 for negative face (defaults to 1)
        :param WS2sign: face of welding surface 2 to place the weld 
                        1 for positive face, -1 for negative face (defaults to 1)
        :param bothSidesOfWS1: if True, weld on both sides of surface SW1 
                               (WS1sign ignored), (defaults to False)
        :param bothSidesOfWS2: if True, weld on both sides of surface SW2 
                               (WS2sign ignored) (defaults to False)
        '''
        prep=self.setWS1.getPreprocessor
        pnts=prep.getMultiBlockTopology.getPoints
        if not self.setName: self.setName=str(uuid.uuid1())
        if len(self.specDescr) < len(self.lstLines):
            self.specDescr=['weld '+str(i) for i in range(len(self.lstLines))]
        for i in range(len(self.lstLines)):
            l=self.lstLines[i]
            if bothSidesOfWS1 or bothSidesOfWS2:
                self.lstWelds.append(FilletWeld(self.weldTyp,self.setWS1,self.setWS2,self.setName+str(i)+'_s1',descr=self.genDescr+', '+self.specDescr[i]+' side 1',weldLine=l))
                self.lstWelds.append(FilletWeld(self.weldTyp,self.setWS1,self.setWS2,self.setName+str(i)+'_s2',descr=self.genDescr+', '+self.specDescr[i]+' side 2',weldLine=l))
            else:
                 self.lstWelds.append(FilletWeld(self.weldTyp,self.setWS1,self.setWS2,self.setName+str(i),descr=self.genDescr+', '+self.specDescr[i],weldLine=l))
        for w in self.lstWelds:
            w.weldSet=None
        if bothSidesOfWS1:
            for i in range(0,len(self.lstWelds),2):
                self.lstWelds[i].generateWeld(nDiv,1,WS2sign)
                self.lstWelds[i+1].generateWeld(nDiv,-1,WS2sign)
        elif bothSidesOfWS2:
            for i in range(0,len(self.lstWelds),2):
                self.lstWelds[i].generateWeld(nDiv,WS1sign,1)
                self.lstWelds[i+1].generateWeld(nDiv,WS1sign,-1)
        else:
            for i in range(len(self.lstWelds)):
                self.lstWelds[i].generateWeld(nDiv,WS1sign,WS2sign)

    def getLstTotalIntForc(self):
        '''Return the list of total forces in directions parallel and 
        perpendiculars to the weld seam for the calculated load case.
        '''
        lstIF=list()
        for w in self.lstWelds:
            lstIF.append(w.getTotalIntForc())
        return lstIF
    
    def getLstCF_AISCverif(self,baseMetal,Phi=0.75):
        '''Return the list of capacity factors of the welds
        according to section J.2 of AISC (reference [2])

        :param Phi: resistance factor (defaults to 0.75)
        '''
        lstCF=list()
        for w in self.lstWelds:
            lstCF.append(w.getCF_AISCverif(baseMetal,Phi))
        return lstCF

    def getMaxCF_AISCverif(self,baseMetal,Phi=0.75):
        '''Return the maximum capacity factors of the welds
        according to section J.2 of AISC (reference [2])

        :param Phi: resistance factor (defaults to 0.75)
        '''
        lstCF=self.getLstCF_AISCverif(baseMetal,Phi)
        return max(lstCF)
    

# Functions to check bolts and welds according to AISC-16
    
def aisc_check_bolts_welds(modelSpace,ULSs,boltSets2Check=[],welds2Check=[],baseMetal=None,meanShearProc=True,resFile=None,linear=True,warningsFile=None,Phi=0.75):
    '''Verification of bolts and welds according to AISC-16
    Checking of bolts uses the capacity factor # formula proposed by Rugarli
    https://www.steelchecks.com/CONNECTIONS-GUIDE/index.html?check_welds.htm
    Parasitic moments in the bolt shafts are neglected.

    :param ULSs: list of pairs (ULS name, ULS expression) with the name
          and expression of the ultimate limit states to be analyzed
    :param boltSets2Check: list of pairs (bolt set, bolt type) with the
          set of bolts and bolt material (instance of class
          astm.BoltFastener) to be analyzed. (Defaults to [])
    :param welds2Check: welds (instances of classes FilletWeld or multiFilletWeld) to check
    :param baseMetal: steel of the plate (only used when welds are checked). Defaults to None
    :paran meanShearProc: if True, each bolt is verified using the mean shear of 
                          the set of bolts (defaults to True)
    :param resFile: file to which dump the results (path and name without extension)
                    (if None-> print to terminal)
    :param linear: if linear analysis (default) = True, else nonlinear analysis.
    :param warningsFile: name of the file of warnings (defaults to None)
    :param Phi: resistance factor (defaults to 0.75)
    '''
    #Initialize properties
    init_prop_checking_bolts(boltSets2Check)
    singlWelds=init_prop_checking_welds(welds2Check)
    # Calculation and checking
    if linear:
        modelSpace.analysis= predefined_solutions.simple_static_linear(modelSpace.getProblem())
    else:
        modelSpace.analysis=  predefined_solutions.penalty_modified_newton(modelSpace.getProblem(), mxNumIter=50, convergenceTestTol= 5.0e-3, printFlag= 2)
    for ULS in ULSs:
        ULS=str(ULS)
        modelSpace.removeAllLoadPatternsFromDomain()
        modelSpace.revertToStart()
        modelSpace.addLoadCaseToDomain(ULS)
        result= modelSpace.analyze(calculateNodalReactions= True)
        oh= output_handler.OutputHandler(modelSpace)
        #bolts checking
        set_bolt_check_resprop_current_LC(ULS,boltSets2Check,meanShearProc)
        #welds checking
        set_welds_check_resprop_current_LC(ULS,singlWelds,baseMetal,Phi)
    #print results of bolt checking
    if len(boltSets2Check)>0:
        Lres=print_bolt_results(boltSets2Check)
        if resFile:
            f=open(resFile+'_bolts.tex','w')
            f.writelines(Lres)
            f.close()
        else:
            for l in Lres: print(l)
    #print results of weld checking
    if len(welds2Check)>0:
        Lres=print_weld_results(singlWelds)
        if resFile:
            f=open(resFile+'_welds.tex','w')
            f.writelines(Lres)
            f.close()
        else:
           for l in Lres: print(l)
    if warningsFile:
        write_check_warnings(warningsFile,boltSets2Check,singlWelds)

def print_bolt_results(boltSets2Check):
    '''return a list with the results

    :param singlWelds: list of welds and results generated during 
          weld checking
    '''
    retval=list()
    for checkIt in  boltSets2Check:
        bset=checkIt[0]
        btype=checkIt[1] 
        CFmax=0
        for e in bset.elements:
            CF=e.getProp('CF')
            if CF>CFmax: CFmax=CF
        retval.append('Bolt set: ' + bset.description + ' diameter=' + str(round(btype.diameter,3)) + ' CF=' + str(round(CFmax,2))+'\n')
    return retval

def print_weld_results(singlWelds):
    '''return a list with the results

    :param singlWelds: list of welds and results generated during 
          weld checking
    '''
    retval=list()
    for w in  singlWelds:
        weld=w[0]
        par=w[1]
        retval.append('Weld: ' + weld.descr+ ' minSz=' + str(round(weld.minSz*1e3,1)) + ' maxSz=' + str(round(weld.maxSz*1e3,1))  + ' size='+ str(round(weld.weldSz*1e3,1)) + ' CF=' + str(round(par[1],2)) + '\n')
    return retval
        
def write_check_warnings(warningsFile,boltSets2Check,singlWelds):
    f=open(warningsFile,'w')
    for checkIt in  boltSets2Check:
        bset=checkIt[0]
        CFmax=0
        for e in bset.elements:
            CF=e.getProp('CF')
            if CF>CFmax: CFmax=CF
        if CFmax >1:
            btype=checkIt[1] 
            f.write('Bolt set: '  + bset.description + ' with diameter=' + str(round(btype.diameter,3)) + ' has a CF=' + str(round(CFmax,2))  + ' > 1 \n \n') 
    for sw in singlWelds:
        w=sw[0]
        par=sw[1]
        txtW='Weld: '+ w.descr + ' between plates with t1= ' + str(w.tWS1) + ' and t2=' + str(w.tWS2) + ' szMin='+ str(w.minSz) + ' szMax=' + str(w.maxSz)
        if w.weldSz < w.minSz:
            f.write(txtW + ' has a size=' + str(w.weldSz) + ' less than minimum=' + str(w.minSz) +'\n \n')
        if w.weldSz > w.maxSz:
            f.write(txtW + ' has a size=' + str(w.weldSz) + ' greater than maximum=' + str(round(w.maxSz,3)) +'\n \n')
        if par[1] > 1:
            f.write(txtW + ' with size=' + str(w.weldSz) + ' has a CF=' +  str(round(par[1],2)) +' > 1 minSZ=' + str(round(w.minSz,3)) +' maxSz=' + str(round(w.maxSz,4)) +'\n \n')
    f.close()
                      
        
    
def init_prop_checking_bolts(boltSets2Check):
    '''Initialize properties of bolt elements for checking''' 
    for checkIt in  boltSets2Check:
        bset=checkIt[0]
        for e in bset.elements:
            e.setProp('CF',0.0);e.setProp('LS','');e.setProp('N',0.0);e.setProp('V',0.0)
    
def init_prop_checking_welds(welds2Check):
    '''Initialize properties of weld elements for checking
    Return a list of single welds
    ''' 
    singlWelds=list()
    for checkW in welds2Check:
        LS='' ; CF=0
        if not hasattr(checkW,'lstWelds'):
            singlWelds.append([checkW,[CF]])
        else:
            for w in checkW.lstWelds: singlWelds.append([w,[LS,CF]])
    return singlWelds

def set_bolt_check_resprop_current_LC(ULS,boltSets2Check,meanShearProc):
    '''Set, for each bolt,  the capacity factor, and internal forces resulting
    for the current ULS
    '''
    for checkIt in  boltSets2Check:
        bset=checkIt[0]
        btyp=checkIt[1]
        Fdt=btyp.getDesignTensileStrength()
        Fdv=btyp.getDesignShearStrength()
        # mean of shear internal forces in the set of bolts
        if meanShearProc:
            Vmean=0
            for e in bset.elements:
                Vmean+=math.sqrt((e.getVy())**2+(e.getVz())**2)
            Vmean=Vmean/bset.elements.size
        for e in bset.elements:
            N=e.getN()
            V=Vmean if meanShearProc else math.sqrt((e.getVy())**2+(e.getVz())**2)
            eN=max(N/Fdt,0)
            eV=V/Fdv
            CF=math.sqrt((2*eN**4+4*eN**2*eV**2+2*eV**4)/(2*eV**2+2*eN**2))
            if CF>e.getProp('CF'):
                e.setProp('CF',CF);e.setProp('LS',ULS);e.setProp('N',N);e.setProp('V',V)

def set_welds_check_resprop_current_LC(ULS,singlWelds,baseMetal,Phi=0.75):
    for i in range(len(singlWelds)):
        weld=singlWelds[i][0]
        CFinit=singlWelds[i][1][-1]
        CF=weld.getCF_AISCverif(baseMetal,Phi)
        if CF>CFinit:
            LS=ULS
#            Rd=0.75*weld.getWeldDesignStrength(Fpar,Fperp)
            singlWelds[i][1]=[LS,CF]

def gen_bolts_xc_conn_model(modelSpace,matchedBolts):
    '''Generate the bolts from the data elaborated in an  XC-connection-model.
    Return the dictionary 'boltSets2Check' with the created sets of bolts
    to check.
    '''
    preprocessor=matchedBolts[0].line.getPreprocessor
    # Bolt sets dictionary
    boltSets2Check=dict()
    for blt in matchedBolts:
        grpName= blt.getBoltGroupName() # Name of the bolt group.
        if grpName not in boltSets2Check.keys():
            D=blt.getDiameter()
            mat=blt.getMaterial()
            boltSets2Check[grpName]={'boltSet': None, 'boltCheckTyp': None, 'boltSeed': None}
            boltSets2Check[grpName]['boltSet']=preprocessor.getSets.defSet(grpName)
            boltSets2Check[grpName]['boltSet'].description=blt.getSetDescription()
            boltSets2Check[grpName]['boltCheckTyp']=ASTM_materials.BoltFastener(diameter=D, steelType=mat)
            boltSets2Check[grpName]['boltSeed']=Bolt(diam=D,mat=mat)
        bltSeed=boltSets2Check[grpName]['boltSeed']
        pntA=blt.endA.kPoint
        pntB=blt.endB.kPoint
        bltSeed.createBolt([pntA,pntB],grpName)  #bolt generation and addition to set
        #raddi end A
        if blt.endA.hole:
            pntHoleLst=blt.endA.hole.getVertices
            plateTh=blt.endA.getPlateThickness()
            bltSeed.generateRadii(plateTh,pntA,pntHoleLst)
        else:
            n=pntA.getNode()
            modelSpace.fixNode000_000(n.tag)
        #raddi end B
        if blt.endB.hole:
            pntHoleLst=blt.endB.hole.getVertices
            plateTh=blt.endB.getPlateThickness()
            bltSeed.generateRadii(plateTh,pntB,pntHoleLst)
        else:
            n=pntB.getNode()
            modelSpace.fixNode000_000(n.tag)
    return boltSets2Check
    
def gen_welds_xc_conn_model(welds,weldMetal,wEldSzFactor=None,avlbWeldSz=None):
    '''Generate the welds from the data elaborated in an XC-connection-model.
    Return the dictionary 'welds2Check' with the created sets of welds
    to check.
    '''
    if avlbWeldSz: avlbWeldTyp=[WeldTyp(t,weldMetal) for t in avlbWeldSz]  #available weld types
    welds2Check=list()
    for w in welds:
        l= w.line
        descr= w.getSetDescription()
        # check if the orientation of the surface is the same as its elements
        # if yes, correction factor for its orientation is equal to 1,
        # otherwise this correction factor = -1 (the orientation is changed)
        vWS1= w.memberToWeld.getKVector 
        vWS1el= w.memberToWeld.elements[0].getKVector3d(True)
        WS1_corrfact= 1 if ((vWS1-vWS1el).getModulus()<1e-2) else -1
        tWS1=w.memberToWeld.elements[0].getPhysicalProperties.getVectorMaterials[0].h  #thickness of member to weld
        for fk in w.faceWelds.keys():
            f= w.faceWelds[fk]
            WS1= f.memberToWeld
            WS2= f.face
            if avlbWeldSz:
                tWS1=WS1.elements[0].getPhysicalProperties.getVectorMaterials[0].h
                tWS2=WS2.elements[0].getPhysicalProperties.getVectorMaterials[0].h
                minSz=ASTM_materials.getFilletWeldMinimumLegSheets(tWS1,tWS2)
                maxSz=ASTM_materials.getFilletWeldMaximumLegSheets(tWS1,tWS2)
                weightedSz=minSz+wEldSzFactor*(maxSz-minSz)
                weldTyp=avlbWeldTyp[dsu.get_index_closest_inlist(avlbWeldSz,weightedSz)]
            else:
                weldTyp=WeldTyp(w.legSize,weldMetal)
            if f.side:
                # check if the orientation of the surface is the same as its elements
                vWS2= WS2.getKVector
                vWS2el=WS2.elements[0].getKVector3d(True)
                WS2_corrfact=1 if ((vWS2-vWS2el).getModulus()<1e-2) else -1
                WS2sign= float(f.side+str(1))*WS2_corrfact
                if f.orientation in ('+-', '-+'):
                    welds2Check.append(MultiFilletWeld(
                        weldTyp,WS1,WS2,[l],genDescr=descr))
                    welds2Check[-1].generateWeld(WS2sign=WS2sign,bothSidesOfWS1=True)
                else:
                    WS1sign= float(f.orientation+str(1))*WS1_corrfact
                    welds2Check.append(FilletWeld(
                        weldTyp,WS1,WS2,descr=descr,weldLine=l))
                    welds2Check[-1].generateWeld(WS1sign=WS1sign,WS2sign=WS2sign)
    return welds2Check


# ---------------------------------------------------------
#Classes intended to generate models of baseplates, gussets, ...

class BoltArray(object):
    '''Defines an arry of bolts

    :ivar nRows: number of rows (elements run in X direction)
    :ivar nCols: number of columns (elements run in Y direction)
    :ivar rowDist: distance Y between rows
    :ivar colDist: distance X between columns 
    :ivar boltDiam: diameter of the bolt
    :ivar holeDiam: diameter of the hole
    :ivar xCentr: global X-coord. of the centroid of the array 
                  (defaults to 0)
    :ivar yCentr: global Y-coord. of the centroid of the array
                  (defaults to 0)
    :ivar excludeBoltIndex: list of index (i,j) in the array where there is
                       no bolt (defaults to empty list -> all the 
                       elements in array has a bolt
    :ivar anglXaxis: angle (degrees, counterclockwise) between a row and X axis.
                     Defaults to 0 (rows parallel to global X axis)
    '''
    
    def __init__(self,nRows,nCols,rowDist,colDist,boltDiam,holeDiam,xCentr=0.0,yCentr=0.0,anglXaxis=0,excludeBoltIndex=[]):
        self.nRows=nRows
        self.nCols=nCols
        self.rowDist=rowDist
        self.colDist=colDist
        self.boltDiam=boltDiam
        self.holeDiam=holeDiam
        self.xCentr=xCentr
        self.yCentr=yCentr
        self.anglXaxis=math.radians(anglXaxis)
        self.excludeBoltIndex=excludeBoltIndex

    def boltXYLcoord(self,ind):
        '''Return the local coordinates (x,y) of the bolt placed in 
        index ind=(indexI,indexJ) given as parameters 
        (first row and column have indexes 0)

        :param ind: (indexI,indexJ) indexes of the bolt in 
                    the array (row and column)
        '''
        x=round(-((self.nCols-1)*self.colDist)/2.0+ind[1]*self.colDist,3)
        y=round(-((self.nRows-1)*self.rowDist)/2.0+ind[0]*self.rowDist,3)
        return (x,y)

    def boltXYcoord(self,ind):
        '''Return the global coordinates (x,y) of the bolt placed in 
        index ind=(indexI,indexJ) given as parameters 
        (first row and column have indexes 0)

        :param ind: (indexI,indexJ) indexes of the bolt in 
                    the array (row and column)
        '''
        (xL,yL)=self.boltXYLcoord(ind)  #local coord.
        x=round(self.xCentr+xL*math.cos(self.anglXaxis)-yL*math.sin(self.anglXaxis),3)
        y=round(self.yCentr+xL*math.sin(self.anglXaxis)+yL*math.cos(self.anglXaxis),3)
        return (x,y)

    def getXYcorners(self):
        '''Return a list with the global coordinates (x,y) of the four
        corner bolts
        '''
        (x1,y1)=self.boltXYcoord((self.nCols-1,self.nRows-1))
        (x2,y2)=self.boltXYcoord((0,self.nRows-1))
        (x3,y3)=self.boltXYcoord((0,0))
        (x4,y4)=self.boltXYcoord((self.nCols-1,0))
        return [(x1,y1),(x2,y2),(x3,y3),(x4,y4)]
        
    def getXmin(self):
        '''Return the minimum global X coordinate of the array of bolts
        '''
        xCorners=[coo[0] for coo in self.getXYcorners()]
        return min(xCorners)

    def getXmax(self):
        '''Return the maximum global X coordinate of the array of bolts
        '''
        xCorners=[coo[0] for coo in self.getXYcorners()]
        return max(xCorners)

    def getYmin(self):
        '''Return the minimum Y coordinate of the array of bolts
        '''
        yCorners=[coo[1] for coo in self.getXYcorners()]
        return min(yCorners)


    def getYmax(self):
        '''Return the maximum Y coordinate of the array of bolts
        '''
        yCorners=[coo[1] for coo in self.getXYcorners()]
        return max(yCorners)
    
    def getBoltIndexes(self):
        '''Return the list of indexes (i,j) in the array where there is 
        bolt.
        '''
        boltIndex=[(i,j) for i in range(self.nRows) for j in range(self.nCols)]
        for indExcl in self.excludeBoltIndex:
            boltIndex.remove(indExcl)
        return boltIndex

    def getPntHole(self,prep,ind):
        '''Generate the 8 points of a hole for bolt in index ind=(i,j).
        Those points belong to a circle of diameter holeDiam, are 
        qually spaced starting at angle 0 and ordered counterclockwise.

        A list of ordered points in returned. Start point is added to the list
        again on last position to close the circle.

        '''
        lstPnt=list()
        points= prep.getMultiBlockTopology.getPoints
        R=self.holeDiam/2.0
        (xbolt,ybolt)=self.boltXYcoord(ind)
        for i in range(8):
            ang=math.radians(i*45)
            pnt=points.newPntFromPos3d(geom.Pos3d(xbolt+R*math.cos(ang),ybolt+R*math.sin(ang),0))
            lstPnt.append(pnt)
        lstPnt.append(lstPnt[0])
        return lstPnt
            
class BoltPlate(object):
    '''Basic class to create a bolt plate of contour defined by width and height, centered in (0,0).

    :ivar width: width of the steel plate (X direction)
    :ivar height: height of the steel plate (Y direction)
    :ivar boltArray: instance of class BoltArray defining an array of 
                     bolts
    :ivar squareSide: side of the square centered in each bolt to 
                      open the mesh
    :ivar setName: name of the set 
    :ivar tolerance: minimum distance between grid lines
                     (defaults to 0.015)
    :ivar minContSize: minimum size of the plate contour around the 
                       bolt-squares array layout  (not used)
    '''

    def __init__(self,width,height,boltArray,squareSide,setName,tolerance=0.015,minContSize=0.015):
        self.width=width
        self.height=height
        self.boltArray=boltArray
        self.squareSide=squareSide
        self.minContSize=minContSize
        self.setName=setName
        self.tol=tolerance
        self.grid=None
        self.partSet=None
        self.dictPntsBoltHole=dict()
        
    def checkSqSide(self):
        '''Check the bolt-square side to meet the minimum distance to the
        contour of the plate. 
        '''
        xmaxCont=self.width/2.-self.minContSize
        xminCont=-self.width/2.+self.minContSize
        ymaxCont=self.height/2.-self.minContSize
        yminCont=-self.height/2.+self.minContSize
        self.squareSide=min(self.squareSide,
                            2*(xmaxCont-self.boltArray.getXmax()),
                            2*(self.boltArray.getXmin()-xminCont),
                            2*(ymaxCont-self.boltArray.getYmax()),
                            2*(self.boltArray.getYmin()-yminCont),
                            self.boltArray.rowDist-self.minContSize,
                            self.boltArray.colDist-self.minContSize)
        
    def generateGridPoints(self,prep,xList2Add=[],yList2Add=[]):
        '''Create the grid with the basic points (contour of the shape) and 
        those points defined by the coordinates in xList2Add, yList2Add and 
        zList2Add (all the three defaults to empty list)
        Create the part set and append to it all grid points
        '''
        self.halfSqrSide=round(self.squareSide/2.,2)
        xList=[-self.width/2.,self.width/2.]+xList2Add
        yList=[-self.height/2.,self.height/2.]+yList2Add
        for ind in self.boltArray.getBoltIndexes():
            (xBolt,yBolt)=self.boltArray.boltXYcoord(ind)
            coor=round(xBolt-self.halfSqrSide,3)
            if abs(coor-dsu.get_closest_inlist(xList,coor))>self.tol: xList.append(coor)
            if abs(xBolt-dsu.get_closest_inlist(xList,xBolt))>self.tol: xList.append(xBolt)
            coor=round(xBolt+self.halfSqrSide,3)
            if abs(coor-dsu.get_closest_inlist(xList,coor))>self.tol: xList.append(coor)
            coor=round(yBolt-self.halfSqrSide,3)
            if abs(coor-dsu.get_closest_inlist(yList,coor))>self.tol: yList.append(coor)
            if abs(yBolt-dsu.get_closest_inlist(yList,yBolt))>self.tol: yList.append(yBolt)
            coor=round(yBolt+self.halfSqrSide,3)
            if abs(coor-dsu.get_closest_inlist(yList,coor))>self.tol: yList.append(coor)
        xList.sort()
        yList.sort()
        zList=[0]
        xList.sort()
        yList.sort()
        lastXpos=len(xList)-1 ; lastYpos=len(yList)-1 ;  lastZpos=len(zList)-1 
        self.grid= gm.GridModel(prep,xList,yList,zList)
        self.grid.generatePoints()
        self.partSet=prep.getSets.defSet(self.setName)
        pnts=self.partSet.getPoints
        for p in self.grid.getLstPntRange(gm.IJKRange((0,0,0),(lastXpos,lastYpos,lastZpos))):
            pnts.append(p)

    def generateSurfaces(self,prep):
        '''Generate the set of surfaces perforated by the holes
        '''
        if not self.grid:
            self.generateGridPoints(prep)
        lastXpos=len(self.grid.gridCoo[0])-1
        lastYpos=len(self.grid.gridCoo[1])-1

        surfaces=prep.getMultiBlockTopology.getSurfaces
#        self.checkSqSide()
        auxSetTot=self.grid.genSurfOneRegion(gm.IJKRange((0,0,0),(lastXpos,lastYpos,0)),'auxSetTot')
        surfSqRgXYZ=list()
        bltInd=self.boltArray.getBoltIndexes() #squares with bolts
        for ind in bltInd:
            (xmin,xmax,ymin,ymax)=self.getLimSquare(ind)
            surfSqRgXYZ.append([(xmin,ymin,0),(xmax,ymax,0)])
        auxSetSqr=self.grid.genSurfMultiXYZRegion(surfSqRgXYZ,'auxSetSqr')
        for s in auxSetTot.getSurfaces:
            if s not in auxSetSqr.getSurfaces:
                self.partSet.getSurfaces.append(s)
        auxSetTot.clear()
        auxSetSqr.clear()
        #squares with bolts
#        bltInd=self.boltArray.getBoltIndexes()
        for ind in bltInd:
            pntSquare,pntHole=self.getPntSurfHole(prep,ind)
            for i in range(len(pntSquare)-1):
                s=surfaces.newQuadSurfacePts(pntHole[i].tag,pntSquare[i].tag,pntSquare[i+1].tag,pntHole[i+1].tag)
                self.partSet.getSurfaces.append(s)
        self.partSet.fillDownwards()

    def generateMesh(self,prep,thickness,steelMat,eSize):
        if not self.partSet:
            self.generateSurfaces(prep)
        self.mat=tm.DeckMaterialData(name=self.setName+'_mat',thickness=thickness,material=steelMat)
        self.mat.setupElasticSection(prep)
        self.meshpar=fem.SurfSetToMesh(surfSet=self.partSet,matSect=self.mat,elemSize=eSize,elemType='ShellMITC4')
        fem.multi_mesh(prep,[self.meshpar])
        
    def getPntSurfHole(self,prep,ind):
        '''Capture the points in the square others than those that 
        belong to the octagon and creates the analogous points in the 
        hole perimeter. Add those points to the two lists of points
        pntSquare and pntHole that will be used to create the surfaces
        surrounding each hole.
        '''
        points= prep.getMultiBlockTopology.getPoints
        (xbolt,ybolt)=self.boltArray.boltXYcoord(ind)
        dictKey=str(ind[0])+'-'+str(ind[1])
        pntBolt=self.grid.getPntXYZ((xbolt,ybolt,0))
        R=self.boltArray.holeDiam/2.0
        pntSquare=self.getPntSquare(ind)
        pntHole=self.boltArray.getPntHole(prep,ind)
        self.dictPntsBoltHole[dictKey]=[pntBolt,pntHole[0:8]]
        indPntSquare=self.getGridIndPntSquare(ind)
        incrAng=math.radians(45)
        Sqtags=[p.tag for p in pntSquare]
        np=0 ; ang=0
        for p in range(8):
            pnt0=pntSquare[np]
            posPnt0=pnt0.getPos
            indIpnt1=indPntSquare[np][0]
            indIpnt2=indPntSquare[np+1][0]
            indJpnt1=indPntSquare[np][1]
            indJpnt2=indPntSquare[np+1][1]
            indKpnt1=indPntSquare[np][2]
            indKpnt2=indPntSquare[np+1][2]
            if abs(indIpnt1-indIpnt2)>1:
                if indIpnt2>indIpnt1: r=range(indIpnt1+1,indIpnt2)
                else: r=range(indIpnt1-1,indIpnt2,-1)
                for i in r:
                    pntSqIns=self.grid.getPntGrid((i,indJpnt1,indKpnt1))
                    posPntSqIns=pntSqIns.getPos
                    relatDist=posPnt0.dist(posPntSqIns)/self.halfSqrSide
                    angPnt=ang+relatDist*incrAng
                    pntHoleIns=points.newPntFromPos3d(geom.Pos3d(xbolt+R*math.cos(angPnt),ybolt+R*math.sin(angPnt),0))
                    pntSquare.insert(np+1,pntSqIns)
                    pntHole.insert(np+1,pntHoleIns)
                    indPntSquare.insert(np+1,'O')
                    np+=1
            if abs(indJpnt1-indJpnt2)>1:
                if indJpnt2>indJpnt1: r=range(indJpnt1+1,indJpnt2)
                else: r=range(indJpnt1-1,indJpnt2,-1)
                for j in r:
                    pntSqIns=self.grid.getPntGrid((indIpnt1,j,indKpnt1))
                    posPntSqIns=pntSqIns.getPos
                    relatDist=posPnt0.dist(posPntSqIns)/self.halfSqrSide
                    angPnt=ang+relatDist*incrAng
                    pntHoleIns=points.newPntFromPos3d(geom.Pos3d(xbolt+R*math.cos(angPnt),ybolt+R*math.sin(angPnt),0))
                    pntSquare.insert(np+1,pntSqIns)
                    pntHole.insert(np+1,pntHoleIns)
                    indPntSquare.insert(np+1,'O')
                    np+=1
            Sqtags=[p.tag for p in pntSquare]
            np+=1
            ang+=incrAng
        return pntSquare,pntHole
            
    def getLimSquare(self,ind):
        '''Return the limit coordinates (xmin,xmax,ymin,ymax) of the square surrounding 
        a bolt with index in the array of bolts ind=(i,j)
        '''
        (xBolt,yBolt)=self.boltArray.boltXYcoord(ind)
        xmin=round(xBolt-self.halfSqrSide,3)
        xmax=round(xBolt+self.halfSqrSide,3)
        ymin=round(yBolt-self.halfSqrSide,3)
        ymax=round(yBolt+self.halfSqrSide,3)
        return (xmin,xmax,ymin,ymax)              


    def getPntSquare(self,ind):
        '''Return an ordered list of points in the square surrounding 
        a bolt with index in the array of bolts ind=(i,j)
        The last point is a duplicate of initial point to close the circle.

        List starts with point at angle 0 and is ordered counterclockwise.
        '''
        (xBolt,yBolt)=self.boltArray.boltXYcoord(ind)
        (xmin,xmax,ymin,ymax)=self.getLimSquare(ind)
        pnt1=self.grid.getPntXYZ((xmax,yBolt,0))
        pnt2=self.grid.getPntXYZ((xmax,ymax,0))
        pnt3=self.grid.getPntXYZ((xBolt,ymax,0))
        pnt4=self.grid.getPntXYZ((xmin,ymax,0))
        pnt5=self.grid.getPntXYZ((xmin,yBolt,0))
        pnt6=self.grid.getPntXYZ((xmin,ymin,0))
        pnt7=self.grid.getPntXYZ((xBolt,ymin,0))
        pnt8=self.grid.getPntXYZ((xmax,ymin,0))
        return [pnt1,pnt2,pnt3,pnt4,pnt5,pnt6,pnt7,pnt8,pnt1]
    
    def getGridIndPntSquare(self,ind):
        '''Return an ordered list of indexes (i,j,k) in the grid 
        of the points in the square surrounding 
        a bolt with index in the array of bolts ind=(i,j)
        The last point is a duplicate of initial point to close the circle.

        List starts with point at angle 0 and is ordered counterclockwise.
        '''
        (xBolt,yBolt)=self.boltArray.boltXYcoord(ind)
        (xmin,xmax,ymin,ymax)=self.getLimSquare(ind)
        indPnt1=self.grid.getIJKfromXYZ((xmax,yBolt,0))
        indPnt2=self.grid.getIJKfromXYZ((xmax,ymax,0))
        indPnt3=self.grid.getIJKfromXYZ((xBolt,ymax,0))
        indPnt4=self.grid.getIJKfromXYZ((xmin,ymax,0))
        indPnt5=self.grid.getIJKfromXYZ((xmin,yBolt,0))
        indPnt6=self.grid.getIJKfromXYZ((xmin,ymin,0))
        indPnt7=self.grid.getIJKfromXYZ((xBolt,ymin,0))
        indPnt8=self.grid.getIJKfromXYZ((xmax,ymin,0))
        return [indPnt1,indPnt2,indPnt3,indPnt4,indPnt5,indPnt6,indPnt7,indPnt8,indPnt1]
    

class RectPlate(BoltPlate):
    '''Create a rectangular plate perfored with holes,
    centered in (0,0) global coordinates

    :ivar width: width of the steel plate (X direction)
    :ivar height: height of the steel plate (Y direction)
    :ivar boltArray: instance of class BoltArray defining an array of 
                     bolts
    :ivar squareSide: side of the square centered in each bolt to 
                      open the mesh
    :ivar  setName: name of the set
    :ivar tolerance: minimum distance between grid lines
                     (defaults to 0.015)
    :ivar minContSize: minimum size of the plate contour around the 
                       bolt-squares array layout (for now not used
                       because some problems arrive when the geometry
                       is not regular).
    '''

    def __init__(self,width,height,boltArray,squareSide,setName,tolerance=0.015,minContSize=0.015):
        super(RectPlate,self).__init__(width,height,boltArray,squareSide,setName,tolerance,minContSize)



class Gusset1Chamfer(BoltPlate):
    '''Create a gusset plate with one chamfer, perfored with holes.
    The corner opposite to chamfer is placed in (0,0) global coordinates

    :ivar width: total width of the steel plate (X direction)
    :ivar height: total height of the steel plate (Y direction)
    :LxChamfer: length of the chamfer in X direction
    :LyChamfer: length of the chamfer in Y direction
    :ivar boltArray: instance of class BoltArray defining an array of 
                     bolts
    :ivar squareSide: side of the square centered in each bolt to 
                      open the mesh
    :ivar setName: set name
    :ivar tolerance: minimum distance between grid lines
                     (defaults to 0.015)
    :ivar minContSize: minimum size of the plate contour around the 
                       bolt-squares array layout (for now not used
                       because some problems arrive when the geometry
                       is not regular).
    '''
    def __init__(self,width,height,LxChamfer,LyChamfer,boltArray,squareSide,setName,tolerance=0.015,minContSize=0.015):
        self.LxChamfer=LxChamfer
        self.LyChamfer=LyChamfer
        super(Gusset1Chamfer,self).__init__(width,height,boltArray,squareSide,setName,tolerance,minContSize)

    def generateSurfaces(self,prep):
        xChamfer=round(self.width/2-self.LxChamfer,3)
        angChamfer=math.atan(self.LyChamfer/self.LxChamfer)
        yChamfer=round(self.height/2-5/4.*self.LyChamfer,3)
        self.generateGridPoints(prep,xList2Add=[xChamfer],yList2Add=[yChamfer])
        xList=self.grid.gridCoo[0]
        yList=self.grid.gridCoo[1]
        lastXpos=len(xList)-1
        lastYpos=len(yList)-1
        
        indXChamfer=xList.index(xChamfer)
        indYChamfer=yList.index(yChamfer)
        Hmax=yList[-1]-yChamfer
        for i in range(indXChamfer,lastXpos+1):
            Lx=xList[i]-xChamfer
            H=Hmax-math.tan(angChamfer)*Lx
            scale=H/Hmax
            rg=gm.IJKRange((i,indYChamfer,0),(i,lastYpos,0))
            self.grid.scaleCoorYPointsRange(rg,yChamfer,scale)
        super(Gusset1Chamfer,self).generateSurfaces(prep)    
                              
        
class diagPlateForGusset(BoltPlate):
    '''Create a suitable rectangular plate that joints a diagonal and a gusset 
    w/ 1 chamfer given as parameter.

    :ivar gusset: instance of class Gusset1Chamfer
    :ivar width: width of the steel plate (X direction)
    :ivar height: height of the steel plate (Y direction)
    :ivar xCentrBolts: global X-coord. of the centroid of the array of bolts
    :ivar yCentrBolts: global Y-coord. of the centroid of the array of bolts
    :ivar squareSide: side of the square centered in each bolt to 
                      open the mesh
    :ivar setName: name of the set
    :ivar tolerance: minimum distance between grid lines
                     (defaults to 0.015)
    '''
    def __init__(self,gusset,width,height,xCentrBolts,yCentrBolts,squareSide,setName,tolerance=0.015):
        gb=gusset.boltArray
        boltArray=BoltArray(gb.nRows,gb.nCols,gb.rowDist,gb.colDist,gb.boltDiam,gb.holeDiam,xCentrBolts,yCentrBolts,0,gb.excludeBoltIndex)
        self.gussetBolts=gb
        super(diagPlateForGusset,self).__init__(width,height,boltArray,squareSide,setName,tolerance)

    def generateSurfaces(self,prep):
        '''Generate the set of surfaces perforated by the holes
        '''
        super(diagPlateForGusset,self).generateSurfaces(prep)
        deltaDisp=(self.gussetBolts.xCentr-self.boltArray.xCentr,
                   self.gussetBolts.yCentr-self.boltArray.yCentr,
                   0)
#        (x0g,y0g)=self.gussetBolts.boltXYcoord(self.gussetBolts.getBoltIndexes()[0])
#        (x0b,y0b)=self.boltArray.boltXYcoord(self.boltArray.getBoltIndexes()[0])
#        deltaDisp=(x0g-x0b,y0g-y0b,0)
        sets.translat(self.partSet,deltaDisp)
        rotAxis=geom.Line3d(geom.Pos3d(self.gussetBolts.xCentr,self.gussetBolts.yCentr,0.0), geom.Pos3d(self.gussetBolts.xCentr,self.gussetBolts.yCentr,100.0))
        rot=xc.Rotation(geom.Rotation3d(rotAxis,self.gussetBolts.anglXaxis))
        self.partSet.transforms(rot)
        
               
class Icolumn(object):
    '''Create an I-shaped column with axis in global-Z direction 
    passing through global coord. origin. Flanges are oriented 
    in X-direction.

    :ivar height: overall height of the I section
    :ivar flWidht: flange width
    :ivar webThick: web thickness
    :ivar flThick: flange thickness
    :ivar membL: length of the column
    :ivar setName: base name for the sets
    '''
    def __init__(self,height,flWidht,webThick,flThick,membL,setName):
        self.height=height
        self.flWidht=flWidht
        self.webThick=webThick
        self.flThick=flThick
        self.membL=membL
        self.setName=setName
        self.halfFlWidth=round(self.flWidht/2.,3)
        self.halfH=round((self.height-self.flThick)/2.,3)
        self.grid=None
        self.flXnegSet=None
        self.flXposSet=None
        self.webSet=None

    def generateGridPoints(self,prep,xList2Add=[],yList2Add=[],zList2Add=[]):
        '''Create the grid with the basic points (contour of the shape) and 
        those points defined by the coordinates in xList2Add, yList2Add and 
        zList2Add (all the three defaults to empty list)
        '''
        xList=[-self.halfFlWidth,0,self.halfFlWidth]+xList2Add
        yList=[-self.halfH,0,self.halfH]+yList2Add
        zList=[0,self.membL]+zList2Add
        xList.sort() ; yList.sort() ; zList.sort()
        self.grid= gm.GridModel(prep,xList,yList,zList)
        self.grid.generatePoints()
        
    def generateSurfaces(self,prep):
        '''Create sets of surfaces flXnegSet, flXposSurfSet and
        webSurfSet to generate the flange in negative X, 
        the flange in positive X and the web of the column,
        respectively
        '''
        if not self.grid:
            self.generateGridPoints(prep)
        lastXpos=len(self.grid.gridCoo[0])-1
        lastYpos=len(self.grid.gridCoo[1])-1
        lastZpos=len(self.grid.gridCoo[2])-1
        surfaces=prep.getMultiBlockTopology.getSurfaces
        self.flXnegSet=self.grid.genSurfOneRegion(gm.IJKRange((0,0,0),(lastXpos,0,lastZpos)),self.setName+'flXneg')
        self.flXposSet=self.grid.genSurfOneRegion(gm.IJKRange((0,lastYpos,0),(lastXpos,lastYpos,lastZpos)),self.setName+'flXpos')
        self.webSet=self.grid.genSurfOneXYZRegion(((0,-self.halfH,0),(0,self.halfH,self.membL)), self.setName+'web')        

    def generateMesh(self,prep,steelMat,eSize):
        if not self.webSet:
            self.generateSurfaces(prep)
        flange_mat=tm.DeckMaterialData(name='flange_mat',thickness= self.flThick,material=steelMat)
        flange_mat.setupElasticSection(prep)
        web_mat=tm.DeckMaterialData(name='web_mat',thickness= self.webThick,material=steelMat)
        web_mat.setupElasticSection(prep)
        flXneg_mesh=fem.SurfSetToMesh(surfSet=self.flXnegSet,matSect=flange_mat,elemSize=eSize,elemType='ShellMITC4')
        flXpos_mesh=fem.SurfSetToMesh(surfSet=self.flXposSet,matSect=flange_mat,elemSize=eSize,elemType='ShellMITC4')
        web_mesh=fem.SurfSetToMesh(surfSet=self.webSet,matSect=web_mat,elemSize=eSize,elemType='ShellMITC4')
        fem.multi_mesh(preprocessor=prep,lstMeshSets=[flXneg_mesh,flXpos_mesh,web_mesh],sectGeom='N') 


class ColumnBaseConnection(object):
    '''Assembly a steel column, a base plate and one or two diagonals
     
    :ivar column: column object
    :ivar basePlate: base plate object
    :ivar gussetFlange: gusset object glued to the flange of the column
    :ivar diagPlateGussetFlange: plate that joints a diagonal and the gussetFlange
    :ivar gussetWeb: gusset object glued to the web of the column
    :ivar diagPlateGussetWeb: plate that joints a diagonal and the gussetWeb
    '''
     
    def __init__(self,column,basePlate,gussetFlange=None,diagPlateGussetFlange=None,gussetWeb=None,diagPlateGussetWeb=None):
        self.column=column
        self.basePlate=basePlate
        self.gussetFlange=gussetFlange
        self.diagPlateGussetFlange=diagPlateGussetFlange
        self.gussetWeb=gussetWeb
        self.diagPlateGussetWeb=diagPlateGussetWeb

            
    def generateMesh(self,prep,steelColumn,steelBasePlate,steelGussets,thickPasePlate,thickGussetFlange,thickDiagPlateGussetFlange,thickGussetWeb,thickDiagPlateGussetWeb,eSize):
        '''Assembly the elements and generate the mesh
        '''
        self.column.generateMesh(prep,steelColumn,eSize)
        self.basePlate.generateMesh(prep,thickPasePlate,steelBasePlate,eSize)
        if self.gussetFlange:
            self.gussetFlange.generateSurfaces(prep)
            if self.diagPlateGussetFlange:
                self.diagPlateGussetFlange.generateSurfaces(prep)
            sets.rot_X(self.gussetFlange.partSet,90)
            sets.rot_Z(self.gussetFlange.partSet,90)
            dy=self.column.height/2+self.gussetFlange.width/2.
            dz=self.gussetFlange.height/2.
            sets.translat(self.gussetFlange.partSet,(0,dy,dz))
            if self.diagPlateGussetFlange:
                sets.rot_X(self.diagPlateGussetFlange.partSet,90)
                sets.rot_Z(self.diagPlateGussetFlange.partSet,90)
                sets.translat(self.diagPlateGussetFlange.partSet,(thickGussetFlange/2.+thickDiagPlateGussetFlange/2.,dy,dz))
                self.diagPlateGussetFlange.generateMesh(prep,thickDiagPlateGussetFlange,steelGussets,eSize)

            self.gussetFlange.generateMesh(prep,thickGussetFlange,steelGussets,eSize)
        if self.gussetWeb:
            self.gussetWeb.generateSurfaces(prep)
            if self.diagPlateGussetWeb:
                self.diagPlateGussetWeb.generateSurfaces(prep)
            sets.rot_X(self.gussetWeb.partSet,90)
            dx=self.gussetWeb.width/2.
            dz=self.gussetWeb.height/2.
            sets.translat(self.gussetWeb.partSet,(dx,0,dz))
            if self.diagPlateGussetWeb:
                sets.rot_X(self.diagPlateGussetWeb.partSet,90)
                sets.translat(self.diagPlateGussetWeb.partSet,(dx,thickGussetWeb/2.+thickDiagPlateGussetWeb/2.,dz))
                self.diagPlateGussetWeb.generateMesh(prep,thickDiagPlateGussetWeb,steelGussets,eSize)
            self.gussetWeb.generateMesh(prep,thickGussetWeb,steelGussets,eSize)

            
#avlbWeldSz=[4e-3,5e-3,6e-3,7e-3,8e-3,9e-3,10e-3,11e-3,12e-3,13e-3,14e-3]  #available weld sizes

def gen_bolts_and_weld_elements(modelSpace, matchedBolts,  weldMetal,welds,weldSzFactor=None,avlbWeldSz=None):
    ''' Create the elements corresponding to bolds and welds.
    '''
    boltSets2Check= gen_bolts_xc_conn_model(modelSpace,matchedBolts)
    welds2Check= gen_welds_xc_conn_model(welds,weldMetal,weldSzFactor,avlbWeldSz)
    return boltSets2Check, welds2Check

            
                                 
def change_weld_size(xcWelds,welds2change):
    '''Change the size of the welds in xcWelds that match 
    the properties defined in welds2change.

    :param xcWelds: list of welds generated by XC
    :param welds2change: dictionary of type 
          {'w1':{'name': 'baseplate', 'oldSize': 0.009, 't1': 0.025, 'newSize':0.010}}
    where 'name' is a string contained in the target weld description,
    'oldSize', 't1', 'newSize' are the size, thickness of the plate to weld 
    and desired size of the target weld which size we want to change.
    '''
    for wch in welds2change:
        name=welds2change[wch]['name'].lower()
        oldSize=welds2change[wch]['oldSize']
        t1=welds2change[wch]['t1']
        newSize=welds2change[wch]['newSize']
        for w in xcWelds:
            # lmsg.info('weld size changed')
            wt1=w.memberToWeld.elements[0].getPhysicalProperties.getVectorMaterials[0].h
            if (name in w.getSetDescription().lower()) and (abs(oldSize-w.legSize)<1e-4) and (abs(t1-wt1)<1e-4):
                w.setLegSize(newSize)
                        
            
            
    
    
