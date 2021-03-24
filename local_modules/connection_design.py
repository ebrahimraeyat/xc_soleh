# -*- coding: utf-8 -*-
''' Connecttion design. Export connection members from the data
    obtained from the structure model.'''

from __future__ import division
from __future__ import print_function

import enum
import math
import ezdxf
import json
from import_export import block_topology_entities as bte
import xc_base
import geom
from misc_utils import log_messages as lmsg
from materials import limit_state_checking_base as lsc
from postprocess import limit_state_data
from materials.astm_aisc import ASTM_materials
import base_plate_design as bpd
from import_export import neutral_mesh_description as nmd
from connections import gusset_plate as gp
from connections import connected_members

class WorstCase(object):
    ''' Connection design worst case.

    :ivar CF: efficiency.
    :ivar eTag: element tag.
    :ivar combName: combination name.
    :ivar forces: forces corresponding to the combination.
    '''
    def __init__(self, CF= 0.0, eTag= -1, forces= None):
        ''' Constructor.

        :param CF: efficiency.
        :param eTag: element tag.
        :param forces: forces corresponding to the combination.
        '''
        self.CF= CF
        self.eTag= eTag
        self.forces= forces

    def update(self, CF, eTag, forces):
        ''' Constructor.

        :param CF: efficiency.
        :param eTag: element tag.
        :param forces: forces corresponding to the combination.
        '''
        if(self.CF<CF):
            self.CF= CF
            self.eTag= eTag
            self.forces= forces

    def __str__(self):
        return 'CF= '+str(self.CF)+' element tag: '+str(self.eTag)+ ' load combination: ' + str(self.forces.idComb)+ ' forces: ' + str(self.forces)

class BoltedPlateController(lsc.LimitStateControllerBase):
    ''' bolted plate limit state checking.

    :ivar boltedPlate: bolted plate to check.
    '''
    def __init__(self, boltedPlate):
        ''' Constructor.

        :param boltedPlate: bolted plate to check.
        '''
        super(BoltedPlateController,self).__init__(limitStateLabel= limit_state_data.normalStressesResistance.label)
        self.boltedPlate= boltedPlate
        
    # def initControlVars(self,setCalc):
    #     '''Initialize control variables over elements.

    #     :param setCalc: set of elements to which define control variables
    #     '''
    #     for e in setCalc.elements:
    #         e.setProp(self.limitStateLabel+'Sect1',cv.AISCBiaxialBendingControlVars(idSection= 'Sect1'))
    #         e.setProp(self.limitStateLabel+'Sect2',cv.AISCBiaxialBendingControlVars(idSection= 'Sect2'))
            
    def predimConnection(self, intForcCombFileName, setCalc=None):
        '''Launch predim connection.

        :param intForcCombFileName: name of the file to read the internal 
               force results
        :param setCalc: set of elements to check
        '''
        intForcItems= limit_state_data.readIntForcesFile(intForcCombFileName,setCalc)
        internalForcesValues= intForcItems[2]
        worstCase= WorstCase()
        for e in setCalc.elements:
            sh= e.getProp('crossSection')
            elIntForc= internalForcesValues[e.tag]
            if(len(elIntForc)==0):
                lmsg.warning('No internal forces for element: '+str(e.tag)+' of type: '+e.type())
            for lf in elIntForc:
                CFtmp= self.boltedPlate.getEfficiency(lf)
                worstCase.update(CFtmp, e.tag, lf)
        return worstCase

class ConnectedMember(connected_members.ConnectedMemberMetaData):
    ''' Connected member.'''
    def getFlangeBoltedPlate(self, boltSteel, plateSteel= ASTM_materials.A36, lbls= None):
        ''' Return a suitable bolted plate for the beam flange.

        :param boltSteel: steel type of the bolts that connect the plate with
                          the flange.
        :param plateSteel: steel type of the bolted plate.
        '''
        flangeStrength= self.shape.getFlangeYieldStrength()
        bolt= self.shape.getFlangeMaximumBolt(steelType= boltSteel)
        numberOfBolts= bolt.getNumberOfBoltsForShear(flangeStrength, numberOfRows= 2, threadsExcluded= True)
        spacing= self.shape.getFlangeWidth()/2.0
        boltArray= ASTM_materials.BoltArray(bolt, nRows= 2, nCols= int(numberOfBolts/2), dist= spacing)
        thicknessRatio= max(self.shape.steelType.fy/plateSteel.fy, self.shape.steelType.fu/plateSteel.fu)
        plateThickness= round(thicknessRatio*self.shape.getFlangeThickness()*1000,0)/1000
        retval= ASTM_materials.BoltedPlate(boltArray, width= self.shape.getFlangeWidth(), thickness= plateThickness, steelType= plateSteel)
        print('plate thickness: ', plateThickness*1e3, ' mm')
        return retval
    

class Connection(connected_members.ConnectionMetaData):
    ''' Naive connection model.

    :ivar columnLengthFactor: vector that multiplies the column unary
                               direction vector to obtain the length
                               of the column.
    :ivar beamLengthFactor: factor that multiplies the beam unary
                            direction vector to obtain the length
                            of the beam to modelize.
    :ivar gussetLengthFactor: factor that multiplies the bolted plate
                               length to obtain the lenght of the gusset
                               plate.
    :ivar boltedPlateTemplate: bolted plate object: dimensions of the bolted 
                          plate and bolt type and arrangement.
    :ivar flangeGussetLegsSlope: tangent of the angle of the flange gusset legs
                                 with its member axis.
    :ivar webGussetBottomLegSlope:
    '''
    def __init__(self, connectionMetaData, columnLengthFactor, beamLengthFactor, gussetLengthFactor, boltedPlateTemplate, boltSteel= ASTM_materials.A490):
        ''' Constructor.

        :param connectionMetaData: connection origin node and members 
                                   connected to it.
        :param columnLengthFactor: vector that multiplies the column unary
                                   direction vector to obtain the length
                                   of the column.
        :param beamLengthFactor: factor that multiplies the beam unary
                                 direction vector to obtain the length
                                 of the beam to modelize.
        :param gussetLengthFactor: factor that multiplies the bolted plate
                                   length to obtain the lenght of the gusset
                                   plate.
        :param boltedPlateTemplate: bolted plate dimensions and bolt type and 
                                    arrangement.
        :param boltSteel: steel for the connection bolts.
        '''
        super(Connection,self).__init__(connectionMetaData.originNode, connectionMetaData.column, connectionMetaData.beams, connectionMetaData.diagonals)
        self.boltSteel= boltSteel
        self.columnLengthFactor= columnLengthFactor
        self.beamLengthFactor= beamLengthFactor
        self.gussetLengthFactor= gussetLengthFactor
        self.boltedPlateTemplate= boltedPlateTemplate
        self.flangeGussetLegsSlope= math.tan(math.radians(30))
        self.webGussetBottomLegSlope= 'vertical'
                    
    def getBasePlateIntersectionPoint(self, sg):
        ''' Get the intersection of the segment with the baseplate.

        :param sg: segment to intersect.
        '''
        basePlatePlane= self.basePlate.getMidPlane()
        retval= basePlatePlane.getIntersection(sg)
        if(math.isnan(retval.x) or math.isnan(retval.y) or math.isnan(retval.z)):
            lmsg.warning('No intersection with base plate.')
        return retval
    
    def getFlangeGussetPlate(self, baseVectors, diagSegment, gussetLength, halfChamfer, slope):
        ''' Return the GussetPlate object for the gusset attached to the
            flange.

        :param baseVectors: unary vectors of the gusset plate reference system.
        :param diagSegment: 3D segment on the diagonal axis.
        :param gussetLength: distance from the connection origin to the
                             gusset chamfer.
        :param halfChamfer: 3D vector from the gusset chamfer mid-point
                            to the end of the chamfer.
        :param slope: tangent of the angle of the gusset leg with its member axis.
        '''
        p0= self.getColumnIntersectionPoint(diagSegment) # intersection with the column
        gussetTip= p0-gussetLength*diagSegment.getVDir().normalized()
        retval= gp.GussetPlate(self.boltedPlateTemplate, gussetTip, halfChamfer, ijkVectors= baseVectors)
        # Top leg
        p1, p2= retval.getSlopedTopLeg(slope, gussetLength)
        topLegSegment= geom.Segment3d(p1,p2)
        p2= self.getColumnIntersectionPoint(topLegSegment) # intersection with the column
        # Bottom leg.
        p3, p4, p5= retval.getToColumnBottomLeg(p0, cutKnifePoint= 0.6)
        if(p5): # knife point not cutted
            retval.setContour([p1, p2, p0, p5, p4, p3])
        else:
            retval.setContour([p1, p2, p0, p4, p3])
        return retval;

    def getWebGussetPlate(self, baseVectors, diagSegment, gussetLength, halfChamfer, bottomLegSlope):
        ''' Return the GussetPlate object for the gusset attached to the
            flange.

        :param baseVectors: unary vectors of the gusset plate reference system.
        :param diagSegment: 3D segment on the diagonal axis.
        :param gussetLength: distance from the connection origin to the
                             gusset chamfer.
        :param halfChamfer: 3D vector from the gusset chamfer mid-point
                            to the end of the chamfer.
        :param bottomLegSlope: if not 'vertical' tangent of the angle of the 
                               gusset bottom leg with its  member axis.
        '''
        origin= diagSegment.getFromPoint()
        gussetTip= origin+gussetLength*diagSegment.getVDir().normalized()
        retval= gp.GussetPlate(self.boltedPlateTemplate, gussetTip, halfChamfer, ijkVectors= baseVectors)
        # Top leg.
        p1, p2= retval.getHorizontalTopLeg(origin)
        # Bottom leg.
        p3= None; p4= None
        if(bottomLegSlope=='vertical'):
            p3, p4= retval.getVerticalBottomLeg(origin)
        else:
            p3, p4= retval.getSlopedBottomLeg(bottomLegSlope, gussetLength)
        bottomLegSegment= geom.Segment3d(p3,p4)
        p4= self.getBasePlateIntersectionPoint(bottomLegSegment) # intersection with the base plate
        retval.setContour([p1, p2, origin, p4, p3])
        return retval

    def getBoltedPlateTemplate(self):
        ''' Return the blocks corresponding to the plate
            bolted to the gusset plate.
        '''
        # Create bolted plate.
        boltedPlate= ASTM_materials.BoltedPlate()
        boltedPlate.setFromDict(self.boltedPlateTemplate.getDict())
        boltedPlate.eccentricity= geom.Vector2d(.025,0.0)
        boltedPlate.length+= .05
        return boltedPlate
        
    def getGussetBlocksForDiagonal(self, diagonal, blockProperties= None):
        ''' Return the blocks that define the gusset for the
            diagonal argument.

        :param diagonal: diagonal to get the gusset for.
        :param blockProperties: labels and attributes to assign to the newly created blocks.
        '''
        def getHalfChamferVector(diagonal):
            ''' Return a vector normal to the diagonal contained in
                a vertical plane.'''
            iVector= diagonal.iVector
            # Horizontal vector perpendicular to the projection
            # of iVector on the horizontal plane.
            perpHoriz= geom.Vector3d(-iVector.y, iVector.x, 0.0)
            return iVector.cross(perpHoriz).normalized()
        
        retval= bte.BlockData()
        origin= self.getOrigin()
        baseVectors= diagonal.getDirection(origin)
        extrusionLength= self.columnLengthFactor
        p1= origin+extrusionLength*baseVectors[0]
        webPlane= self.getColumnWebMidPlane()
        angleWithWeb= webPlane.getAngleWithVector3d(baseVectors[0])
        dgSegment= geom.Segment3d(origin,p1)
        gussetLength= self.gussetLengthFactor*self.boltedPlateTemplate.length
        halfChamferVector= getHalfChamferVector(diagonal)
        halfChamfer= self.boltedPlateTemplate.width/2.0*halfChamferVector
        verticalWeldLegSize= 0.0 # leg size for the vertical welds.
        horizontalWeldLegSize= math.floor(self.getHorizontalWeldLegSize()*1e3)/1e3 # leg size for the horizontal welds.      
        if(abs(angleWithWeb)<1e-3): # diagonal parallel to web => flange gusset.
            verticalWeldLegSize= math.floor(self.getFlangeLegSize()*1e3)/1e3
            objType= 'flange_gusset'
            gussetPlate= self.getFlangeGussetPlate(baseVectors= baseVectors, diagSegment= dgSegment, gussetLength= gussetLength, halfChamfer= halfChamfer, slope= self.flangeGussetLegsSlope)
        else: # diagonal normal to web  => web gusset
            verticalWeldLegSize= math.floor(self.getWebLegSize()*1e3)/1e3
            objType= 'web_gusset'
            gussetPlate= self.getWebGussetPlate(baseVectors= baseVectors, diagSegment= dgSegment, gussetLength= gussetLength, halfChamfer= halfChamfer, bottomLegSlope= self.webGussetBottomLegSlope)
        # Attached plate.
        boltedPlate= self.getBoltedPlateTemplate()
        gussetPlateProperties= bte.BlockProperties.copyFrom(blockProperties)
        gussetPlateProperties.appendAttribute('objType', objType)
        
        gussetPlateBlocks= gussetPlate.getBlocks(verticalWeldLegSize, horizontalWeldLegSize, boltedPlate, diagonal, self.getOrigin(), blockProperties= gussetPlateProperties)
        retval.extend(gussetPlateBlocks)
        return retval
    
    def getBeamShapeBlocks(self, factor, blockProperties= None):
        ''' Return the faces of the beams.

        :param factor: factor multiplies the unary direction vector
                       of the member to define its extrusion 
                       direction and lenght.
        :param blockProperties: labels and attributes to assign to the newly created blocks.
        '''
        retval= bte.BlockData()
        beamBlocks= super(Connection,self).getBeamShapeBlocks(factor)
        retval.extend(beamBlocks)
        plateProperties= bte.BlockProperties.copyFrom(blockProperties)
        plateProperties.appendAttribute('objType', 'flange_plate')
        # Flange plates.
        for b in self.beams:
            flangePlate= b.getFlangeBoltedPlate(self.boltSteel)
            origin= self.getOrigin()
            print('origin: ', origin, ' beam origin: ', b.memberOrigin)
            baseVectors= b.getDirection(origin)
            halfH= (b.shape.h()+b.shape.getFlangeThickness()+flangePlate.thickness)/2.0
            halfD= flangePlate.length/2.0
            print('half H:', halfH*1e3,'mm')
            print('half D:', halfD*1e3,'mm')
            # Top plate
            topPlateCenter= b.memberOrigin + halfH*baseVectors[1] + halfD*baseVectors[0]
            topPlateRefSys= geom.Ref3d3d(topPlateCenter, baseVectors[0], baseVectors[2])
            topPlateBlocks= flangePlate.getBlocks(refSys= topPlateRefSys, blockProperties= plateProperties)
            retval.extend(topPlateBlocks)
            # Holes in top flange
            print('has holes: ', topPlateBlocks.hasHoles())
            holesList= topPlateBlocks.getHoles()
            for holes in holesList:
                for key in holes.points:
                    p= holes.points[key]
                    objType= p.getAttribute('objType')
                    if(objType=='hole_center'):
                        pos= geom.Pos3d(p.getX(), p.getY(), p.getZ())
                        diameter= p.getAttribute('diameter')
                        nearestFace= beamBlocks.getNearest(pos)
                        posInFlange= nearestFace.getGeomObject(beamBlocks.points).getPlane().getPos3dProjection(pos)
                        dist= posInFlange.dist(pos)
                        print(pos, objType, diameter, nearestFace.id, dist)
                        XXX
            quit()
            # Bottom plate
            bottomPlateCenter= b.memberOrigin - halfH*baseVectors[1] + halfD*baseVectors[0]
            bottomPlateRefSys= geom.Ref3d3d(bottomPlateCenter, baseVectors[0], baseVectors[2])
            bottomPlateBlocks= flangePlate.getBlocks(refSys= bottomPlateRefSys, blockProperties= plateProperties)
            retval.extend(bottomPlateBlocks)
        return retval
    
    def getBlocks(self, blockProperties= None):
        ''' Creates the block data for later meshing.

        :param blockProperties: labels and attributes to assign to the newly created blocks.
        '''
        originNodeTag= str(self.originNode.tag)
        properties= bte.BlockProperties.copyFrom(blockProperties)
        properties.appendAttribute('jointId', originNodeTag)
        retval= bte.BlockData()
        # Column blocks.
        columnShapeBlocks= self.getColumnShapeBlocks(self.columnLengthFactor, blockProperties= properties)
        retval.extend(columnShapeBlocks)
        # Beam blocks.
        beamShapeBlocks= self.getBeamShapeBlocks(self.beamLengthFactor, blockProperties= properties)
        retval.extend(beamShapeBlocks)
        # Diagonal blocks.
        for e in self.diagonals:
            retval.extend(self.getGussetBlocksForDiagonal(e, blockProperties= properties))
        if(hasattr(self,'basePlate')):
            retval.extend(self.getBasePlateBlocks(columnShapeBlocks, blockProperties= properties))
        else:
            lmsg.warning('base plate not found.')
        return retval

    def getFlangeLegMinSize(self):
        ''' Return the minimum leg size of the gusset plate
            with the flange.
        '''
        flangeThickness= self.getColumnShape().get('tf')
        return self.boltedPlateTemplate.getFilletMinimumLeg(flangeThickness)
    
    def getFlangeLegMaxSize(self):
        ''' Return the maximum leg size of the gusset plate
            with the flange.
        '''
        flangeThickness= self.getColumnShape().get('tf')
        return self.boltedPlateTemplate.getFilletMaximumLeg(flangeThickness)
    
    def getFlangeLegSize(self, factor= 0.75):
        ''' Return the weld leg size of the gusset plate
            with the flange.
        '''
        minFlangeLeg= self.getFlangeLegMinSize()
        maxFlangeLeg= self.getFlangeLegMaxSize()
        return minFlangeLeg+factor*(maxFlangeLeg-minFlangeLeg)

    def getWebLegMinSize(self):
        ''' Return the minimum leg size of the gusset plate
            with the web.
        '''
        webThickness= self.getColumnShape().get('tw')
        return self.boltedPlateTemplate.getFilletMinimumLeg(webThickness)
    
    def getWebLegMaxSize(self):
        ''' Return the maximum leg size of the gusset plate
            with the web.
        '''
        webThickness= self.getColumnShape().get('tw')
        return self.boltedPlateTemplate.getFilletMaximumLeg(webThickness)
    
    def getWebLegSize(self, factor= 0.6):
        ''' Return the leg size of the gusset plate
            with the web.
        '''
        minWebLeg= self.getWebLegMinSize()
        maxWebLeg= self.getWebLegMaxSize()
        return minWebLeg+factor*(maxWebLeg-minWebLeg)
                    
    def report(self, outputFile):
        ''' Reports connection design values.'''
        outputFile.write('Connection ID: '+str(self.originNode.tag)+'\n')
        columnShape= self.getColumnShape()
        outputFile.write('  column steel shape: '+columnShape.getMetricName()+' (US: '+columnShape.name+')\n')
        diagonalShapes= self.getDiagonalShapes()
        outputFile.write('  diagonal shapes: ')
        for ds in diagonalShapes:
            outputFile.write(ds.getMetricName()+' (US: '+ds.name+') ')
        outputFile.write('\n')
        self.boltedPlateTemplate.report(outputFile)
        outputFile.write('    gusset plate - column welds:\n')
        outputFile.write('      with the flange(s): 2 x '+str(math.floor(self.getFlangeLegSize()*1000))+' mm (fillet weld leg size)\n')
        outputFile.write('      with the web: 2 x '+str(math.floor(self.getWebLegSize()*1000))+' mm (fillet weld leg size)\n')
        outputFile.write('      with the plate 2 x '+str(math.floor(self.getHorizontalWeldLegSize()*1000))+' mm (fillet weld leg size)\n')
        
class DiagonalConnection(Connection):
    ''' Connection that has one or more diagonals.'''
    
    def getHorizontalWeldLegSize(self):
        ''' Return the size of the weld that connects the 
            gusset plate with horizontal plate.
        '''
        print('Not implemented yet.')
        return 0.0
    
class BasePlateConnection(Connection):
    ''' Base plate connection.'''
    
    def centerAnchors(self):
        ''' Center anchors with respect to the column steel shape.'''
        columnShape= self.getColumnShape()
        flangeThickness= columnShape.get('tf')
        interiorDist= columnShape.get('h')-2*flangeThickness
        self.basePlate.centerAnchors(columnShape)
        
    def getBasePlateWeldLegMinSize(self):
        ''' Return the minimum leg size of the weld that connects the 
            gusset plate with the base plate.
        '''
        plateThickness= self.basePlate.t
        return self.boltedPlateTemplate.getFilletMinimumLeg(plateThickness)
    
    def getBasePlateWeldLegMaxSize(self):
        ''' Return the maximum leg size of the weld that connects the 
            gusset plate with the base plate.
        '''
        plateThickness= self.basePlate.t
        return self.boltedPlateTemplate.getFilletMaximumLeg(plateThickness)
    
    def getPlateWeldLegSize(self, factor= 0.6):
        ''' Return the leg size of the weld that connects the 
            gusset plate with the base plate.
        '''
        minPlateThickness= self.getBasePlateWeldLegMinSize()
        maxPlateThickness= self.getBasePlateWeldLegMaxSize()
        return minPlateThickness+factor*(maxPlateThickness-minPlateThickness)

    def getHorizontalWeldLegSize(self):
        ''' Return the size of the weld that connects the 
            gusset plate with the base plate.
        '''
        return self.getPlateWeldLegSize()

    def getColumnBaseplateWeldBlocks(self, flangeWeldLegSize, webWeldLegSize, blockProperties= None):
        ''' Return the lines roughly corresponding to weld beads.

        :param flangeWeldLegSize: leg size for the weld to the flange.
        :param webWeldLegSize: leg size for the weld to the web.
        :param blockProperties: labels and attributes to assign to the newly created blocks.
        '''
        basePlateProperties= bte.BlockProperties.copyFrom(blockProperties)
        basePlateProperties.appendAttribute('objType', 'baseplate')
        return self.column.getFrontalWeldBlocks(flangeWeldLegSize, webWeldLegSize, blockProperties= basePlateProperties)
    
    def getBasePlateBlocks(self, columnShapeBlocks, blockProperties= None):
        ''' Create the blocks corresponding to the baseplate.

        :param columnShapeBlocks: blocks of the column welded to the baseplate.
        :param blockProperties: labels and attributes to assign to the newly created blocks.
        '''
        properties= bte.BlockProperties.copyFrom(blockProperties)
        retval= bte.BlockData()
        retval.extend(self.basePlate.getBlocks(blockProperties= properties))
        flangeLegSize= math.floor(self.basePlate.getFlangeWeldLegSize(0.3)*1e3)/1e3 # Arbitrary factor: temporary solution. LP 29/09/2020
        webLegSize= math.floor(self.basePlate.getWebWeldLegSize()*1e3)/1e3 # Default factor: temporary solution. LP 29/09/2020
        columnBasePlateWeldBlocks= self.getColumnBaseplateWeldBlocks(flangeLegSize, webLegSize, properties)
        for face, weld in zip(columnShapeBlocks.faceBlocks, columnBasePlateWeldBlocks.weldBlocks):
            weldProperties= bte.BlockProperties.copyFrom(properties)
            weldProperties.appendAttribute('ownerId', 'f'+str(face.id)) # owner identifier.
            weld.blockProperties+=(weldProperties)
        retval.extend(columnBasePlateWeldBlocks)
        return retval
    
    def report(self, outputFile):
        ''' Reports connection design values.

        :param outputFile: Python file descriptor for output.
        '''
        super(BasePlateConnection,self).report(outputFile)
        self.basePlate.report(outputFile)
    
        
class ConnectionGroup(object):
    ''' Group of similar connections.

    :ivar name: name for the group of connections.
    :ivar connectionData: connection origin node and elements connected 
                           to it classified as column or diagonals.
    :ivar gussetLengthFactor: factor that multiplies the boltedPlate
                               length to obtain the lenght of the gusset
                               plate.
    :ivar boltedPlateTemplate: bolted plate dimensions and bolt type and 
                                arrangement.
    :ivar connections: list of connections of the group
    '''
    def __init__(self, name, connectionData, columnLengthFactor, beamLengthFactor, gussetLengthFactor, boltedPlateTemplate, ConnectionType):
        ''' Constructor.

        :param name: name for the group of connections.
        :param connectionType: type of the connection (see derived classes).
        :param connectedMembers: connection origin node and members connected 
                                 to it classified as columns, beams or
                                 diagonals.
        :param columnLengthFactor: factor that multiplies the column unary
                                   direction vector to obtain the length
                                   of the column to modelize.
        :param beamLengthFactor: factor that multiplies the beam unary
                                 direction vector to obtain the length
                                 of the beam to modelize.
        :param gussetLengthFactor: factor that multiplies the boltedPlate
                                   length to obtain the lenght of the gusset
                                   plate.
        :param boltedPlateTemplate: bolted plate dimensions and bolt type and 
                                    arrangement.
        '''
        self.name= name
        self.connectionData= connectionData
        self.gussetLengthFactor= gussetLengthFactor
        self.boltedPlateTemplate= boltedPlateTemplate
        self.connections= list()
        for nTag in self.connectionData:
            cData= self.connectionData[nTag]
            connect= ConnectionType(cData, columnLengthFactor, beamLengthFactor, self.gussetLengthFactor, self.boltedPlateTemplate)
            self.connections.append(connect)

    def joinBasePlates(self, basePlateGroup, tol= 1e-2):
        ''' Add base plates to each connection using the origin
            coordinates as key.

        :param basePlateGroup: base plates to add.
        '''
        basePlates= basePlateGroup.basePlates
        for key in basePlates:
            bp= basePlates[key]
            bpOrg= bp.origin
            for c in self.connections:
                cOrg= c.getOrigin()
                dist= cOrg.dist(bpOrg)
                if(dist<tol):
                    c.basePlate= bp

    def setFlangeGussetLegsSlope(self, flangeGussetLegsSlope):
        ''' Set the slope for the gusset flange legs.'''
        for c in self.connections:
            c.flangeGussetLegsSlope= flangeGussetLegsSlope

    def setWebGussetBottomLegSlope(self, webGussetBottomLegSlope):
        ''' Set the slope for the gusset bottom legs.'''
        for c in self.connections:
            c.webGussetBottomLegSlope= webGussetBottomLegSlope

    def centerAnchors(self):
        ''' Center anchors with respect to the column steel shape.'''
        for c in self.connections:
            c.centerAnchors()
            
    def getBlocks(self):
        ''' Creates the block data for meshing.'''
        retval= bte.BlockData()
        retval.name= self.name+'_blocks'
        for c in self.connections:
            retval.extend(c.getBlocks())
        return retval

    def getLoadData(self,inputFileName):
        ''' Extracts the internal forces for each member from the
            argument.

        :param inputFileName: data file containing the internal forces.
        '''
        retval= dict()
        with open(inputFileName) as inputFile:
            data= json.load(inputFile)
            for c in self.connections:
                retval.update(c.getLoadData(data))
        return retval

    def report(self, outputFile):
        ''' Reports connection design values.'''
        numberOfPlates= len(self.connections)
        outputFile.write(str(numberOfPlates)+' x ')
        connect= self.connections[0]
        connect.report(outputFile)
        # for c in self.connections:
        #     c.report(outputFile)

    def output(self):
        ''' Write output: report + dxf file. '''
        blocks= self.getBlocks()

        outputFileNameBase= self.name
        
        xcImportExportData= nmd.XCImportExportData()
        xcImportExportData.problemName= outputFileNameBase+'_FEPrb'
        xcImportExportData.outputFileName= outputFileNameBase+'_blocks'
        xcImportExportData.xcFileName= outputFileNameBase+'.py'
        xcImportExportData.blockData= blocks
        # Write XC file.
        xcImportExportData.writeToXCFile()
        # Write DXF file.
        xcImportExportData.writeDxfFile(outputFileNameBase+'.dxf')
        # Write TXT file.
        outputFileName= outputFileNameBase+'.txt'
        outputFile= open(outputFileName, 'w')
        self.report(outputFile)
        outputFile.close()
        return blocks

class DiagonalConnectionGroup(ConnectionGroup):
    ''' Connection group with one or more diagonals. '''
    
    def __init__(self, name, columnLengthFactor, beamLengthFactor, gussetLengthFactor, xcSet, ConnectionType= DiagonalConnection):
        ''' Constructor.

        :param name: name for the group of connections.
        :param columnLengthFactor: factor that multiplies the column unary
                                   direction vector to obtain the length
                                   of the column to modelize.
        :param beamLengthFactor: factor that multiplies the beam unary
                                 direction vector to obtain the length
                                 of the beam to modelize.
        :param gussetLengthFactor: factor that multiplies the boltedPlate
                                   length to obtain the lenght of the gusset
                                   plate.
        :param xcSet: set containing the joint nodes.
        '''
        
        # Read bolted plate data.
        boltedPlate= None #ASTM_materials.readBoltedPlateFromJSONFile('./diagonal_fastener.json')
        
        # Get members connected to the joint
        # from the model of the whole structure.
        jointMembers= connected_members.getConnectedMembers(xcSet, ConnectedMemberType= ConnectedMember)

        super(DiagonalConnectionGroup, self).__init__(name, jointMembers, columnLengthFactor, beamLengthFactor, gussetLengthFactor, boltedPlate, ConnectionType)
    
class BasePlateConnectionGroup(DiagonalConnectionGroup):
    ''' Base plate connection group. '''
    
    def __init__(self, name, columnLengthFactor, beamLengthFactor, gussetLengthFactor, xcSet, basePlateDefFileName= './base_plates.json'):
        ''' Constructor.

        :param name: name for the group of connections.
        :param columnLengthFactor: factor that multiplies the column unary
                                   direction vector to obtain the length
                                   of the column to modelize.
        :param beamLengthFactor: factor that multiplies the beam unary
                                 direction vector to obtain the length
                                 of the beam to modelize.
        :param gussetLengthFactor: factor that multiplies the boltedPlate
                                   length to obtain the lenght of the gusset
                                   plate.
        :param xcSet: set containing the base plate nodes.
        :param basePlateDefFileName: name of the base plate definition file.
        '''
        super(BasePlateConnectionGroup, self).__init__(name, columnLengthFactor, beamLengthFactor, gussetLengthFactor, xcSet, ConnectionType= BasePlateConnection)
        # Read base plate data.
        basePlateGroup= bpd.readBasePlateGroupFromJSONFile(basePlateDefFileName)
        self.joinBasePlates(basePlateGroup)
