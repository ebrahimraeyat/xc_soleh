# -*- coding: utf-8 -*-
from __future__ import division 

import math
import xc_base
import geom
import xc

# Generic functions
def cross(xcV1,xcV2):
    '''cross product of two xc vectors of 3-D
    '''
    v1=geom.Vector3d(xcV1[0],xcV1[1],xcV1[2])
    v2=geom.Vector3d(xcV2[0],xcV2[1],xcV2[2])
    vcross=v1.cross(v2)
    xcVcross=xc.Vector([vcross.x,vcross.y,vcross.z])
    return xcVcross
            
def getSuitableXZVector(iNode, jNode):
    ''' Return a vector that can be used to define
        a coordinate transformation for an element
        between the node arguments.

    :param iNode: first node.
    :param jNode: second node.
    '''
    p1= iNode.getInitialPos3d
    p2= jNode.getInitialPos3d
    sg= geom.Line3d(p1,p2)
    v3d= sg.getKVector
    return xc.Vector([v3d.x, v3d.y, v3d.z])

def setBearingBetweenNodes(prep,iNodA,iNodB,bearingMaterialNames,orientation= None):
    '''Modelize a bearing between the nodes

     :param iNodA: (int) first node identifier (tag).
     :param iNodB: (int) second node identifier (tag).
     :param bearingMaterialNames: (list) material names for the zero 
        length element [mat1,mat2,mat3,mat4,mat5,mat6], where:
        mat1,mat2,mat3 correspond to translations along local x,y,z 
        axes, respectively,
        mat3,mat4,mat5 correspond to rotation about local x,y,z 
        axes, respectively.
     :param orientation: (list) of two vectors [x,yp] used to orient 
        the zero length element, where: 
        x: are the vector components in global coordinates defining 
           local x-axis (optional)
        yp: vector components in global coordinates defining a  vector
             that lies in the local x-y plane of the element(optional).
      If the optional orientation vector are not specified, the local
      element axes coincide with the global axes. Otherwise, the local
      z-axis is defined by the cross product between the vectors x 
      and yp specified in the command line.
      :return: newly created zero length element that represents the bearing.

    '''
    # Element definition
    elems= prep.getElementHandler
    elems.dimElem= prep.getNodeHandler.dimSpace # space dimension.
    elems.defaultMaterial= next((item for item in bearingMaterialNames if item is not None), 'All are Nones')
    zl= elems.newElement("ZeroLength",xc.ID([iNodA,iNodB]))
    zl.clearMaterials()
    if(orientation): #Orient element.
        zl.setupVectors(orientation[0],orientation[1])
    numMats= len(bearingMaterialNames)
    for i in range(0,numMats):
        material= bearingMaterialNames[i]
        if(material!=None):
            zl.setMaterial(i,material)
    return zl
