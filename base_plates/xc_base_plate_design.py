# -*- coding: utf-8 -*-
''' Base plate preliminary design according to document
    Base Plate and Anchor Rod Design Second Edition
    American Institute of Steel Construction, Inc.
'''

from __future__ import division
from __future__ import print_function

import sys
sys.path.insert(0, '../local_modules')
import base_plate_design as bpd

import json
import math
import csv
import xc_base
import geom
from materials.astm_aisc import ASTM_materials
# from rough_calculations import ng_aisc_base_plates as bp
import ezdxf

ksi2Pa= 6.89476e6

class ThisBasePlate(bpd.CustomBasePlate):
    ''' Taylor made base plate :)'''
    def getWebStress(self, Pu):
        ''' Return the tension stress in the shaft web.

        :param Pu: axial load (LRFD).
        '''
        retval= 0.0
        if(Pu<0): # tensile load
            T_rod= -Pu # Tensile load
            tw= self.steelShape.get('tw') # Web thickness
            tf= self.steelShape.get('tf') # Flange thickness
            d= self.steelShape.get('h')-2*tf # Web height
            area_web= d*tw
            b= self.steelShape.get('b') # Flange width
            area_flange= 0.5*b*tf
            retval= T_rod/(area_web+area_flange)
        return retval
    
class ThisBasePlateGroup(bpd.BasePlateGroup):
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
            self.basePlates[key]= ThisBasePlate(B= B, N= N, t= t, steelShape= steelShape, anchorGroup= anchorGroup, steel= steel, fc= fc, origin= p)
            self.nShearBolts= len(positions) # Use welded washers

    
# Materials
steel_W= ASTM_materials.A36 #steel support W shapes
steel_W.fy = 240e6
steel_W.gammaM= 1.00
# steelShape= ASTM_materials.WShape(steel_W,'W18X192')
steelShape = ASTM_materials.IShape(.2, .012, .008, .2, steel_W, name="W18X76")
fc= 25e6 # Minimum concrete compressive strength


# Anchors
boltDiameter= 24e-3

## Positions
positions= list()
x1 = .075
y1 = .05
positions.append(geom.Pos3d(x1, y1, 0.0))
positions.append(geom.Pos3d(x1, -y1, 0.0))
positions.append(geom.Pos3d(-x1, -y1, 0.0))
positions.append(geom.Pos3d(-x1, y1, 0.0))
rodMaterial= ASTM_materials.F1554gr36
#rodMaterial= ASTM_materials.F1554gr55
## Bolt template
boltTemplate= ASTM_materials.AnchorBolt(name= 'template', steel= rodMaterial, diameter= boltDiameter)

## Plate washer
#plateWasher=  ASTM_materials.SquarePlateWasher(boltTemplate)
plateWasher= None

anchorGroupLeft= ASTM_materials.AnchorGroup(steel= rodMaterial, diameter= boltDiameter, positions= positions, plateWasher= plateWasher)
    
h_ef= .35
h_total= h_ef+0.15+0.05+4.0*boltDiameter # 150mm of concrete + 50mm grouting = total 200mm
print(h_total)

# Base plate
B= math.ceil((steelShape.get('b')+0.06)/0.05)*0.05
N= math.ceil((steelShape.get('h')+0.06)/0.05)*0.05
# B = .6
# N = .4
# N =.4
reactionsFileName= 'uls_reactions.csv'
basePlateGroup= bpd.getBasePlateGroupFromFile(B= B, N= N, t= .015, steelShape= steelShape, anchorGroup= anchorGroupLeft, fc= fc, steel= steel_W, fileName= reactionsFileName)
for key in basePlateGroup.basePlates:
    bp= basePlateGroup.basePlates[key]
    bp.nShearBolts= bp.anchorGroup.getNumberOfBolts() # Use welded washers
    # if(bp.origin.x>0.5):
    #     bp.offsetB= -offset
    #     bp.anchorGroup= anchorGroupRight
    # else:
    #     bp.offsetB= offset


capacityFactors= bpd.CapacityFactors(basePlateGroup)
capacityFactors.compute(reactionsFileName, h_ef)
basePlateGroup.writeDXF('stair_tower')
basePlateGroup.h_ef= h_ef
capacityFactors.report()
print('h_ef= ', h_ef, 'm')
outputFileName= './base_plates.json'
with open(outputFileName, 'w') as outfile:
    json.dump(basePlateGroup.getDict(), outfile)
outfile.close()





