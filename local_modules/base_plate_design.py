# -*- coding: utf-8 -*-
''' Base plate design.'''

from __future__ import division
from __future__ import print_function

import sys
import math
import csv
import xc_base
import geom
import ezdxf
import json
from materials.astm_aisc import ASTM_materials
from colorama import Fore
from colorama import Style
from rough_calculations import ng_aisc_base_plates as bp
from import_export import block_topology_entities as bte
from misc_utils import log_messages as lmsg

def exportULSReactions(writer, combName, joints):
    '''Export reactions in ultimate limit states.

    :param writer: csv writer to use.
    :param structureId: identifier for the structure.
    :param combName: load combination name.
    :param supportSet: set containing support nodes.
    '''
    for j in joints:
        n= j[0]
        pos= n.getInitialPos3d
        pointId= j[1]
        Rx= n.getReaction[0]
        Ry= n.getReaction[1]
        Rz= n.getReaction[2]
        writer.writerow([combName, pointId, pos.x, pos.y, pos.z, Rx, Ry, Rz])

def myround(x, prec=2, base=.05):
  return round(base * round(float(x)/base),prec)

def getAnchorGroup(steel, diameter, squareSide, xCenter= 0.0, yCenter= 0.0):
    ''' Return four anchors in the corners of the square.'''
    delta= squareSide/2.0
    origin= geom.Pos3d(xCenter, yCenter, 0.0)
    positions= list()
    positions.append(origin+geom.Vector3d(delta,delta,0.0))
    positions.append(origin+geom.Vector3d(-delta,delta,0.0))
    positions.append(origin+geom.Vector3d(-delta,-delta,0.0))
    positions.append(origin+geom.Vector3d(delta,-delta,0.0))
    return ASTM_materials.AnchorGroup(steel, diameter, positions)


class CustomBasePlate(bp.RectangularBasePlate):
    ''' Base plate adapted to this project.

    '''
    def __init__(self, N, B, t, steelShape, anchorGroup, fc, steel, origin):
        ''' Constructor.

        :param N: dimension parallel to the web of the shaft.
        :param B: dimension parallel to the flange of the shaft.
        :param t: thickness.
        :param steelShape: shape of the steel column supported
                           by the plate.
        :param anchorGroup: anchor group.
        :param fc: minimum concrete compressive strength.
        :param steel: steel material.
        :param origin: center of the base plate.
        '''
        super(CustomBasePlate,self).__init__(N, B, t, steelShape, anchorGroup, fc, steel, origin)


    def centerAnchors(self, columnShape):
        ''' Center anchors with respect to the column steel shape.'''
        nAnchors= self.anchorGroup.getNumberOfBolts()
        if(nAnchors<=4):
            flangeThickness= columnShape.get('tf')
            delta= (columnShape.get('h')-flangeThickness)/4.0
            positions= list()
            positions.append(geom.Vector3d(delta,delta,0.0))
            positions.append(geom.Vector3d(-delta,delta,0.0))
            positions.append(geom.Vector3d(-delta,-delta,0.0))
            positions.append(geom.Vector3d(delta,-delta,0.0))
            self.anchorGroup.setPositions(positions)
        else:
            lmsg.warning('Number of anchors is not 4. Cannot center them.')
        
    def writeDXFShapeContour(self, modelSpace, layerName):
        ''' Writes the shape contour in the model
            space argument.

        :param modelSpace: model space to write into.
        :param layerName: layer name.
        '''
        plg= self.steelShape.getContour()
        posVec3d= self.origin.getPositionVector()
        posVec2d= geom.Vector2d(posVec3d.x, posVec3d.y)
        plg.move(posVec2d)
        vtx= plg.getVertices()
        vtx.append(vtx[0])
        v0= vtx[0]
        for v in vtx[1:]:
            modelSpace.add_line((v0.x, v0.y), (v.x, v.y), dxfattribs={'layer': layerName})
            v0= v
            
    def writeDXFBasePlate(self, modelSpace, layerName):
        ''' Draw base plate

        :param modelSpace: model space to write into.
        :param layerName: layer name.
        '''
        deltaX= self.B/2.0
        deltaY= self.N/2.0
        positions= self.getContour().getVertexList()
        modelSpace.add_line((positions[0].x, positions[0].y), (positions[1].x, positions[1].y), dxfattribs={'layer': layerName})
        modelSpace.add_line((positions[1].x, positions[1].y), (positions[2].x, positions[2].y), dxfattribs={'layer': layerName})
        modelSpace.add_line((positions[2].x, positions[2].y), (positions[3].x, positions[3].y), dxfattribs={'layer': layerName})
        modelSpace.add_line((positions[3].x, positions[3].y), (positions[0].x, positions[0].y), dxfattribs={'layer': layerName})

    def getHoleDiameter(self):
        ''' Return the hole diameter.'''
        return myround(self.anchorGroup.anchors[0].getNominalHoleDiameter(), prec=3, base=.005)
        
    def writeDXFAnchorBolts(self, modelSpace, layerName):
        ''' Draw anchor bolts

        :param modelSpace: model space to write into.
        :param layerName: layer name.
        '''
        boltDiameter= self.anchorGroup.anchors[0].diameter
        self.holeDiameter= self.getHoleDiameter()
        origin2d= geom.Pos2d(self.origin.x, self.origin.y)
        for anchor in self.anchorGroup.anchors:
            center= origin2d+geom.Vector2d(anchor.pos3d.x, anchor.pos3d.y)
            modelSpace.add_circle((center.x, center.y), self.holeDiameter/2.0, dxfattribs={'layer': layerName})
            
    def report(self, outputFile):
        ''' Writes base plate specification.'''
        super(CustomBasePlate,self).report(outputFile)
        holeDiameter= self.getHoleDiameter()
        outputFile.write('     hole diameter: '+ str(holeDiameter*1e3)+ ' mm\n')
        #outputFile.write('fc= ', fc/1e6,' MPa')
        #outputFile.write('   area: '+ self.getArea()+ ' m2')
 
class BasePlateGroup(object):
    ''' Group of similar base plates.'''
    def __init__(self, N, B, t, steelShape, anchorGroup, fc, steel, pointMap):
        ''' Constructor.

        :param N: dimension parallel to the web of the shaft.
        :param B: dimension parallel to the flange of the shaft.
        :param t: thickness.
        :param steelShape: shape of the steel column supported
                           by the plate.
        :param anchorGroup: anchor group.
        :param fc: minimum concrete compressive strength.
        :param steel: steel material.
        :poram points: indentifiers and coordinates of the 
                       base plate centers.
        '''
        self.basePlates= dict()
        for key in pointMap:
            p= pointMap[key]
            self.basePlates[key]= CustomBasePlate(B= B, N= N, t= t, steelShape= steelShape, anchorGroup= anchorGroup, steel= steel, fc= fc, origin= p)
            
    def getDict(self):
        ''' Put member values in a dictionary.'''
        retval= dict()
        for key in self.basePlates:
            retval[key]= self.basePlates[key].getDict()
        if(hasattr(self,'h_ef')):
           retval.update({'h_ef':self.h_ef})
        return retval

    def setFromDict(self,dct):
        ''' Read member values from a dictionary.'''
        if('h_ef' in dct):
           self.h_ef= dct['h_ef']
        dct.pop('h_ef', None) # Remove already used key
        for key in dct:
            self.basePlates[key]=  CustomBasePlate(B= 0, N= 0, t= 0, steelShape= None, anchorGroup= None, steel= None, fc= 0.0, origin= None)
        for key in dct:
            self.basePlates[key].setFromDict(dct[key])

    def jsonRead(self, inputFileName):
        ''' Read object from JSON file.'''
        with open(inputFileName) as json_file:
            basePlateGroupDict= json.load(json_file)
        self.setFromDict(basePlateGroupDict)
        json_file.close()
        
    def getBlocks(self, blockProperties):
        ''' Return the block decomposition of the base plates.

        :param blockProperties: labels and attributes to assign to the newly created blocks.
        '''
        retval= bte.BlockData()
        for key in self.basePlates:
            basePlate= self.basePlates[key]
            retval.extend(basePlate.getBlocks(blockProperties))
        return retval
        
    def writeDXF(self, baseName):
        doc= ezdxf.new('R2010')
        doc.header['$MEASUREMENT'] = 1 # Metric
        doc.header['$LUNITS'] = 2 # Decimal units.
        doc.header['$INSUNITS'] = 6 # # Default drawing units.
        steelShapesLayerName= 'xc_'+baseName+'_steel_shapes'
        doc.layers.new(name= steelShapesLayerName, dxfattribs={'color': 4})
        basePlatesLayerName= 'xc_'+baseName+'_base_plates'
        doc.layers.new(name= basePlatesLayerName, dxfattribs={'color': 4})
        anchorsLayerName= 'xc_'+baseName+'_anchor_bolts'
        doc.layers.new(name= anchorsLayerName, dxfattribs={'color': 2})
        msp = doc.modelspace()  # add new entities to the modelspace
        for key in self.basePlates:
            basePlate= self.basePlates[key]
            # Draw steel shape
            basePlate.writeDXFShapeContour(msp, steelShapesLayerName)
            # Draw base plate
            basePlate.writeDXFBasePlate(msp, basePlatesLayerName)
            # Draw anchor holes
            basePlate.writeDXFAnchorBolts(msp, anchorsLayerName)
        fileName= baseName+'_base_plates.dxf'
        doc.saveas(fileName)

    def getNumberOfBolts(self):
        ''' Return the total number of bolts.'''
        retval= 0
        for key in self.basePlates:
            basePlate= self.basePlates[key]
            retval+= basePlate.anchorGroup.getNumberOfBolts()
        return retval
        
    def report(self, outputFile):
        numberOfBolts= 0
        numberOfPlates= len(self.basePlates)
        outputFile.write(str(numberOfPlates)+' x ')
        firstKey= list(self.basePlates.keys())[0]
        basePlate= self.basePlates[firstKey]
        basePlate.report(outputFile)
        numberOfBolts= self.getNumberOfBolts()
        outputFile.write('total number of anchors: '+str(numberOfBolts)+'\n')
        outputFile.write('depth of embedment: '+ str(self.h_ef)+ ' m\n')
        #outputFile.write('number of base plates: '+str(len(self.basePlates)))
        
            
def getBasePlateGroupFromFile(N, B, t, steelShape, anchorGroup, fc, steel, fileName):
    ''' Extract the centroids position from the reactions file.'''
    mapPoints= dict()
    with open(fileName) as csvfile:
        readCSV = csv.reader(csvfile, delimiter=',')
        for row in readCSV:
            pointId= str(row[1])
            if( not pointId in mapPoints):
                x= float(row[2])
                y= float(row[3])
                origin= geom.Pos3d(x,y,0.0)
                mapPoints[pointId]= origin
    csvfile.close()
    return BasePlateGroup(N, B, t, steelShape, anchorGroup, fc, steel, mapPoints)

def readBasePlateGroupFromJSONFile(inputFileName):
    ''' Read base plate group object from a JSON file.'''
    retval= BasePlateGroup(N= 0.0, B= 0.0, t= 0.0, steelShape= None, anchorGroup= None, fc= 0.0, steel= None, pointMap= {})
    retval.jsonRead(inputFileName)
    return retval

        
class CapacityFactors(object):
    def __init__(self, basePlateGroup):
        self.basePlateGroup= basePlateGroup
        self.tCF= 0.0
        self.rodCF= 0.0
        self.webStressCF= 0.0
        self.concreteStrengthCF= 0.0
        self.pulloutCF= 0.0
        self.breakoutCF= 0.0
        self.shearCF= 0.0
        
    def compute(self, fileName, h_ef):
        with open(fileName) as csvfile:
            readCSV = csv.reader(csvfile, delimiter=',')
            for row in readCSV:
                Pu= -float(row[7])
                Vu= math.sqrt(float(row[5])**2+float(row[6])**2)
                pointId= str(row[1])
                basePlate= self.basePlateGroup.basePlates[pointId]
                basePlate.h_ef= h_ef
                self.shearCF= max(self.shearCF,basePlate.getShearEfficiency(Pu, Vu))
                self.concreteStrengthCF= max(self.concreteStrengthCF,basePlate.getConcreteStrengthEfficiency(Pu))
                self.tCF= max(self.tCF,basePlate.getThicknessEfficiency(Pu))
                self.pulloutCF= max(self.pulloutCF,basePlate.getPulloutEfficiency(Pu))
                self.breakoutCF= max(self.breakoutCF,basePlate.getBreakoutEfficiency(h_ef,Pu))
                self.webStressCF= max(self.webStressCF,basePlate.getWebStressEfficiency(Pu))
                self.rodCF= max(self.rodCF, basePlate.getRodTensileStrengthEfficiency(Pu))
                self.shearTensileInteractionCF= math.sqrt(self.rodCF**2+self.shearCF**2)
        self.maxCF= max([self.tCF, self.rodCF, self.webStressCF, self.concreteStrengthCF, self.pulloutCF, self.breakoutCF, self.shearCF, self.shearTensileInteractionCF])

        if(self.maxCF<= 1.0):
            self.basePlateGroup.h_ef= h_ef

    def report(self):
        #print('fc= ', fc/1e6,' MPa')
        self.basePlateGroup.report(sys.stdout)
        print('concreteStrengthCF= ', self.concreteStrengthCF)
        print('thickness efficiency tCF= ', self.tCF)
        print('rodCF= ', self.rodCF)
        print('webStressCF= ', self.webStressCF)
        print('pulloutCF= ', self.pulloutCF)
        print('breakoutCF= ', self.breakoutCF)
        print('shearCF= ', self.shearCF)
        print('shearTensileInteractionCF= ', self.shearTensileInteractionCF)
        if(self.maxCF<= 1.0):
            print(Fore.GREEN+'OK'+Style.RESET_ALL)
        elif(self.breakoutCF>1.0 and (max([self.tCF, self.rodCF, self.webStressCF, self.concreteStrengthCF, self.pulloutCF,self.shearCF])<=1.0)):
            print(Fore.GREEN+'OK'+Style.RESET_ALL+', but supplementary reinforcement needed (breakoutCF>1).')            
        else:
            print(Fore.RED+'KO'+Style.RESET_ALL)

    def output(self, outputFileName):
        ''' Generate output: report+dxf file.'''
        self.report()
        #print('h_ef= ', self.h_ef, 'm')
        self.basePlateGroup.writeDXF(outputFileName)
        basePlatesOutputFileName= './'+outputFileName+'_base_plates.json'
        with open(basePlatesOutputFileName, 'w') as outfile:
            json.dump(self.basePlateGroup.getDict(), outfile)
        outfile.close()


