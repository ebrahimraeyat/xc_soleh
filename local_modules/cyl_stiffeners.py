# -*- coding: utf-8 -*-
from __future__ import division 

import math
import xc_base
import geom
import xc
from model.geometry import grid_model as gm
from materials import typical_materials as tm
from model.mesh import finit_el_model as fem
from materials import typical_materials as tm
import gen_functions as gf

class AnnularStiff(object):
    '''Create a horizontal annular stiffener part with symmetry with respect to
    vertical plane at angle 0 and a bolt centered in that plane.
    :ivar RcoordBolt: radial coordinate where the bolt is placed.

    '''
    def __init__(self,Rint,Rext,RcoordBolt,semiAng,z,holeRad,squareSide,nDiv,setName):
       self.Rint=Rint
       self.Rext=Rext
       self.RcoordBolt=RcoordBolt
       self.semiAng=semiAng
       self.z=z
       self.holeRad=holeRad
       self.squareSide=squareSide
       self.nDiv=nDiv
       self.setName=setName
       self.grid=None
       self.partSet=None
       self.pntBolt=None
       self.pntsHole=None
       
    def generateSurfaces(self,prep):
        '''Generate the set of surfaces perforated by the hole
        '''
        surfaces=prep.getMultiBlockTopology.getSurfaces
        points= prep.getMultiBlockTopology.getPoints
        semiLsq=round(self.squareSide/2.,3)
        semiAngSq=round(math.degrees(semiLsq/self.RcoordBolt),3)
        Rlist=[self.Rint,self.RcoordBolt-semiLsq,self.RcoordBolt,self.RcoordBolt+semiLsq,self.Rext]
        Rlist.sort()
        Anglist=[-self.semiAng,-semiAngSq,0,semiAngSq,self.semiAng]
        inc=(self.semiAng-semiAngSq)/self.nDiv
        Anglist+=[-self.semiAng+i*inc for i in range(1,self.nDiv)]
        Anglist+=[semiAngSq+i*inc for i in range(1,self.nDiv)]
        Anglist.sort()
        Zlist=[self.z]
        self.grid=gm.GridModel(prep,Rlist,Anglist,Zlist,xCentCoo=0,yCentCoo=0)
        self.grid.generateCylZPoints()
        self.partSet=self.grid.genSurfMultiXYZRegion([
            ((self.Rint,-self.semiAng,self.z),(self.RcoordBolt-semiLsq,self.semiAng,self.z)),
            ((self.RcoordBolt-semiLsq,-self.semiAng,self.z),(self.RcoordBolt+semiLsq,-semiAngSq,self.z)),
            ((self.RcoordBolt-semiLsq,semiAngSq,self.z),(self.RcoordBolt+semiLsq,self.semiAng,self.z)),
            ((self.RcoordBolt+semiLsq,-self.semiAng,self.z),(self.Rext,self.semiAng,self.z))],self.setName)
        if self.holeRad>0:
            #Points of the hole (counterclokwise from angle=0)
            self.pntBolt=self.grid.getPntXYZ((self.RcoordBolt,0,self.z))
            (ibolt,jbolt,kbolt)=self.grid.getIJKfromXYZ((self.RcoordBolt,0,self.z)) #indexes
            (xbolt,ybolt,zbolt)=(self.pntBolt.getPos[0],self.pntBolt.getPos[1],self.pntBolt.getPos[2])
            self.pntsHole=list()
            for i in range(8):
                ang=math.radians(i*45)
                pnt=points.newPntFromPos3d(geom.Pos3d(xbolt+self.holeRad*math.cos(ang),ybolt+self.holeRad*math.sin(ang),zbolt))
                self.pntsHole.append(pnt)
            self.pntsHole.append(self.pntsHole[0]) #Start point is added to the list again on last position to close the circle.
            #Points of the square
            ind_square=[(ibolt+1,jbolt,kbolt)]
            ind_square+=[(ibolt+i,jbolt+1,kbolt) for i in range(1,-2,-1)]
            ind_square+=[(ibolt-1,jbolt,kbolt)]
            ind_square+=[(ibolt+i,jbolt-1,kbolt) for i in range(-1,2)]
            pnts_square=[self.grid.getPntGrid(i) for i in ind_square]
            pnts_square.append(pnts_square[0])
            for i in range(8):
                s=surfaces.newQuadSurfacePts(self.pntsHole[i].tag,pnts_square[i].tag,pnts_square[i+1].tag,self.pntsHole[i+1].tag)
                self.partSet.getSurfaces.append(s)

        self.partSet.fillDownwards()

    def generateMesh(self,prep,thickness,steelMat,eSize):
        if not self.partSet:
            self.generateSurfaces(prep)
        self.mat=tm.DeckMaterialData(name=self.setName+'_mat',thickness=thickness,material=steelMat)
        self.mat.setupElasticSection(prep)
        meshpar=fem.SurfSetToMesh(surfSet=self.partSet,matSect=self.mat,elemSize=eSize,elemType='ShellMITC4')
        fem.multi_mesh(prep,[meshpar])

def cyl_bound_cond(setNodes,orientation,Klist,name):
    '''

    :param setNodes: set of nodes to apply boundary conditions
    :param orientation: (list) of two vectors [x,yp] used to orient 
       the zero length element, where: 
       x are the vector components in global coordinates defining 
          local x-axis (optional)
       y: vector components in global coordinates defining a  vector
            that lies in the local x-y plane of the element(optional).
     If the optional orientation vector are not specified, the local
     element axes coincide with the global axes. Otherwise, the local
     z-axis is defined by the cross product between the vectors x 
     and yp specified in the command line.
    :param Klist: stiffness [KX,KY,KZ,KrotX,KrotY,KrotZ]
    
    '''
    prep=setNodes.getPreprocessor
    nodes=prep.getNodeHandler
    constr=prep.getBoundaryCondHandler
    matKX=tm.defElasticMaterial(prep,name+'matKX',Klist[0])
    matKY=tm.defElasticMaterial(prep,name+'matKY',Klist[1])
    matKZ=tm.defElasticMaterial(prep,name+'matKZ',Klist[2])
    matKrotX=tm.defElasticMaterial(prep,name+'matKrotX',Klist[3])
    matKrotY=tm.defElasticMaterial(prep,name+'matKropY',Klist[4])
    matKrotZ=tm.defElasticMaterial(prep,name+'matKrotZ',Klist[5])
    materials=[matKX.name,matKY.name,matKZ.name,matKrotX.name,matKrotY.name,matKrotZ.name]
    for n in setNodes.nodes:
        p=n.getInitialPos3d
        nn=nodes.newNodeXYZ(p.x,p.y,p.z)
        for i in range(6):
            constr.newSPConstraint(nn.tag,i,0.0)
        gf.setBearingBetweenNodes(prep,n.tag,nn.tag,materials,orientation)
    

def get_low_high_stiff(partThickness,partMat):
    '''Return a low and high stiffness with respect to the 
    thickness and material of a shell part
    '''
    low_A=partThickness*1e-10
    high_A=100*partThickness
    return (low_A*partMat.E,high_A*partMat.E)
