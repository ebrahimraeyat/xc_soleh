# preprocessor= stair_tower_column_bases_FEPrb.getPreprocessor
nodes= preprocessor.getNodeHandler
elements= preprocessor.getElementHandler
points= preprocessor.getMultiBlockTopology.getPoints
lines= preprocessor.getMultiBlockTopology.getLines
surfaces= preprocessor.getMultiBlockTopology.getSurfaces
groups= preprocessor.getSets
pt0= points.newPntIDPos3d(0,geom.Pos3d(47.894,-0.1,0.0)); pt0.setProp("attributes",{'jointId': '123', 'objType': 'column', 'loadTag': 151, 'loadDirI': [0.0, 0.0, 1.0], 'loadDirJ': [1.0, 0.0, 0.0], 'loadDirK': [0.0, 1.0, 0.0], 'shape': 'W18X35'})
pt1= points.newPntIDPos3d(1,geom.Pos3d(47.894,0.0,0.0)); pt1.setProp("attributes",{'jointId': '123', 'objType': 'column', 'loadTag': 151, 'loadDirI': [0.0, 0.0, 1.0], 'loadDirJ': [1.0, 0.0, 0.0], 'loadDirK': [0.0, 1.0, 0.0], 'shape': 'W18X35'})
pt2= points.newPntIDPos3d(2,geom.Pos3d(47.894,0.1,0.0)); pt2.setProp("attributes",{'jointId': '123', 'objType': 'column', 'loadTag': 151, 'loadDirI': [0.0, 0.0, 1.0], 'loadDirJ': [1.0, 0.0, 0.0], 'loadDirK': [0.0, 1.0, 0.0], 'shape': 'W18X35'})
pt3= points.newPntIDPos3d(3,geom.Pos3d(48.106,-0.1,0.0)); pt3.setProp("attributes",{'jointId': '123', 'objType': 'column', 'loadTag': 151, 'loadDirI': [0.0, 0.0, 1.0], 'loadDirJ': [1.0, 0.0, 0.0], 'loadDirK': [0.0, 1.0, 0.0], 'shape': 'W18X35'})
pt4= points.newPntIDPos3d(4,geom.Pos3d(48.106,0.0,0.0)); pt4.setProp("attributes",{'jointId': '123', 'objType': 'column', 'loadTag': 151, 'loadDirI': [0.0, 0.0, 1.0], 'loadDirJ': [1.0, 0.0, 0.0], 'loadDirK': [0.0, 1.0, 0.0], 'shape': 'W18X35'})
pt5= points.newPntIDPos3d(5,geom.Pos3d(48.106,0.1,0.0)); pt5.setProp("attributes",{'jointId': '123', 'objType': 'column', 'loadTag': 151, 'loadDirI': [0.0, 0.0, 1.0], 'loadDirJ': [1.0, 0.0, 0.0], 'loadDirK': [0.0, 1.0, 0.0], 'shape': 'W18X35'})
pt6= points.newPntIDPos3d(6,geom.Pos3d(47.894,-0.1,1.5)); pt6.setProp("attributes",{'jointId': '123', 'objType': 'column', 'loadTag': 151, 'loadDirI': [0.0, 0.0, 1.0], 'loadDirJ': [1.0, 0.0, 0.0], 'loadDirK': [0.0, 1.0, 0.0], 'shape': 'W18X35'})
pt7= points.newPntIDPos3d(7,geom.Pos3d(47.894,0.0,1.5)); pt7.setProp("attributes",{'jointId': '123', 'objType': 'column', 'loadTag': 151, 'loadDirI': [0.0, 0.0, 1.0], 'loadDirJ': [1.0, 0.0, 0.0], 'loadDirK': [0.0, 1.0, 0.0], 'shape': 'W18X35'})
pt8= points.newPntIDPos3d(8,geom.Pos3d(47.894,0.1,1.5)); pt8.setProp("attributes",{'jointId': '123', 'objType': 'column', 'loadTag': 151, 'loadDirI': [0.0, 0.0, 1.0], 'loadDirJ': [1.0, 0.0, 0.0], 'loadDirK': [0.0, 1.0, 0.0], 'shape': 'W18X35'})
pt9= points.newPntIDPos3d(9,geom.Pos3d(48.106,-0.1,1.5)); pt9.setProp("attributes",{'jointId': '123', 'objType': 'column', 'loadTag': 151, 'loadDirI': [0.0, 0.0, 1.0], 'loadDirJ': [1.0, 0.0, 0.0], 'loadDirK': [0.0, 1.0, 0.0], 'shape': 'W18X35'})
pt10= points.newPntIDPos3d(10,geom.Pos3d(48.106,0.0,1.5)); pt10.setProp("attributes",{'jointId': '123', 'objType': 'column', 'loadTag': 151, 'loadDirI': [0.0, 0.0, 1.0], 'loadDirJ': [1.0, 0.0, 0.0], 'loadDirK': [0.0, 1.0, 0.0], 'shape': 'W18X35'})
pt11= points.newPntIDPos3d(11,geom.Pos3d(48.106,0.1,1.5)); pt11.setProp("attributes",{'jointId': '123', 'objType': 'column', 'loadTag': 151, 'loadDirI': [0.0, 0.0, 1.0], 'loadDirJ': [1.0, 0.0, 0.0], 'loadDirK': [0.0, 1.0, 0.0], 'shape': 'W18X35'})
pt12= points.newPntIDPos3d(12,geom.Pos3d(48.15,0.15000000000000002,0.0)); pt12.setProp("attributes",{'jointId': '123', 'objType': 'baseplate', 'matId': 'A36'})
pt13= points.newPntIDPos3d(13,geom.Pos3d(47.85,0.15000000000000002,0.0)); pt13.setProp("attributes",{'jointId': '123', 'objType': 'baseplate', 'matId': 'A36'})
pt14= points.newPntIDPos3d(14,geom.Pos3d(47.85,-0.15000000000000002,0.0)); pt14.setProp("attributes",{'jointId': '123', 'objType': 'baseplate', 'matId': 'A36'})
pt15= points.newPntIDPos3d(15,geom.Pos3d(48.15,-0.15000000000000002,0.0)); pt15.setProp("attributes",{'jointId': '123', 'objType': 'baseplate', 'matId': 'A36'})
pt16= points.newPntIDPos3d(16,geom.Pos3d(48.09661875,0.05,0.0)); pt16.setProp("attributes",{'jointId': '123', 'objType': 'hole', 'matId': None, 'boltGroup': 'joint_123_baseplate', 'ownerId': 'f5'})
pt17= points.newPntIDPos3d(17,geom.Pos3d(48.090286764725775,0.06528676472577667,0.0)); pt17.setProp("attributes",{'jointId': '123', 'objType': 'hole', 'matId': None, 'boltGroup': 'joint_123_baseplate', 'ownerId': 'f5'})
pt18= points.newPntIDPos3d(18,geom.Pos3d(48.075,0.07161875000000001,0.0)); pt18.setProp("attributes",{'jointId': '123', 'objType': 'hole', 'matId': None, 'boltGroup': 'joint_123_baseplate', 'ownerId': 'f5'})
pt19= points.newPntIDPos3d(19,geom.Pos3d(48.059713235274224,0.06528676472577669,0.0)); pt19.setProp("attributes",{'jointId': '123', 'objType': 'hole', 'matId': None, 'boltGroup': 'joint_123_baseplate', 'ownerId': 'f5'})
pt20= points.newPntIDPos3d(20,geom.Pos3d(48.05338125,0.05000000000000001,0.0)); pt20.setProp("attributes",{'jointId': '123', 'objType': 'hole', 'matId': None, 'boltGroup': 'joint_123_baseplate', 'ownerId': 'f5'})
pt21= points.newPntIDPos3d(21,geom.Pos3d(48.059713235274224,0.034713235274223334,0.0)); pt21.setProp("attributes",{'jointId': '123', 'objType': 'hole', 'matId': None, 'boltGroup': 'joint_123_baseplate', 'ownerId': 'f5'})
pt22= points.newPntIDPos3d(22,geom.Pos3d(48.075,0.02838125,0.0)); pt22.setProp("attributes",{'jointId': '123', 'objType': 'hole', 'matId': None, 'boltGroup': 'joint_123_baseplate', 'ownerId': 'f5'})
pt23= points.newPntIDPos3d(23,geom.Pos3d(48.090286764725775,0.03471323527422332,0.0)); pt23.setProp("attributes",{'jointId': '123', 'objType': 'hole', 'matId': None, 'boltGroup': 'joint_123_baseplate', 'ownerId': 'f5'})
pt24= points.newPntIDPos3d(24,geom.Pos3d(48.075,0.05,0.0)); pt24.setProp("attributes",{'jointId': '123', 'objType': 'hole_center', 'matId': 'A36', 'boltGroup': 'joint_123_baseplate', 'ownerId': 'f6', 'diameter': 0.024, 'boltMaterial': 'F1554gr36'})
pt25= points.newPntIDPos3d(25,geom.Pos3d(48.075,0.05,-0.024)); pt25.setProp("attributes",{'jointId': '123', 'objType': 'anchor_point', 'matId': 'A36', 'boltGroup': 'joint_123_baseplate', 'ownerId': None, 'diameter': 0.024, 'boltMaterial': 'F1554gr36'})
pt26= points.newPntIDPos3d(26,geom.Pos3d(48.09661875,-0.05,0.0)); pt26.setProp("attributes",{'jointId': '123', 'objType': 'hole', 'matId': None, 'boltGroup': 'joint_123_baseplate', 'ownerId': 'f5'})
pt27= points.newPntIDPos3d(27,geom.Pos3d(48.090286764725775,-0.03471323527422333,0.0)); pt27.setProp("attributes",{'jointId': '123', 'objType': 'hole', 'matId': None, 'boltGroup': 'joint_123_baseplate', 'ownerId': 'f5'})
pt28= points.newPntIDPos3d(28,geom.Pos3d(48.075,-0.02838125,0.0)); pt28.setProp("attributes",{'jointId': '123', 'objType': 'hole', 'matId': None, 'boltGroup': 'joint_123_baseplate', 'ownerId': 'f5'})
pt29= points.newPntIDPos3d(29,geom.Pos3d(48.059713235274224,-0.03471323527422332,0.0)); pt29.setProp("attributes",{'jointId': '123', 'objType': 'hole', 'matId': None, 'boltGroup': 'joint_123_baseplate', 'ownerId': 'f5'})
pt30= points.newPntIDPos3d(30,geom.Pos3d(48.05338125,-0.049999999999999996,0.0)); pt30.setProp("attributes",{'jointId': '123', 'objType': 'hole', 'matId': None, 'boltGroup': 'joint_123_baseplate', 'ownerId': 'f5'})
pt31= points.newPntIDPos3d(31,geom.Pos3d(48.059713235274224,-0.06528676472577667,0.0)); pt31.setProp("attributes",{'jointId': '123', 'objType': 'hole', 'matId': None, 'boltGroup': 'joint_123_baseplate', 'ownerId': 'f5'})
pt32= points.newPntIDPos3d(32,geom.Pos3d(48.075,-0.07161875000000001,0.0)); pt32.setProp("attributes",{'jointId': '123', 'objType': 'hole', 'matId': None, 'boltGroup': 'joint_123_baseplate', 'ownerId': 'f5'})
pt33= points.newPntIDPos3d(33,geom.Pos3d(48.090286764725775,-0.06528676472577669,0.0)); pt33.setProp("attributes",{'jointId': '123', 'objType': 'hole', 'matId': None, 'boltGroup': 'joint_123_baseplate', 'ownerId': 'f5'})
pt34= points.newPntIDPos3d(34,geom.Pos3d(48.075,-0.05,0.0)); pt34.setProp("attributes",{'jointId': '123', 'objType': 'hole_center', 'matId': 'A36', 'boltGroup': 'joint_123_baseplate', 'ownerId': 'f8', 'diameter': 0.024, 'boltMaterial': 'F1554gr36'})
pt35= points.newPntIDPos3d(35,geom.Pos3d(48.075,-0.05,-0.024)); pt35.setProp("attributes",{'jointId': '123', 'objType': 'anchor_point', 'matId': 'A36', 'boltGroup': 'joint_123_baseplate', 'ownerId': None, 'diameter': 0.024, 'boltMaterial': 'F1554gr36'})
pt36= points.newPntIDPos3d(36,geom.Pos3d(47.94661875,-0.05,0.0)); pt36.setProp("attributes",{'jointId': '123', 'objType': 'hole', 'matId': None, 'boltGroup': 'joint_123_baseplate', 'ownerId': 'f5'})
pt37= points.newPntIDPos3d(37,geom.Pos3d(47.940286764725776,-0.03471323527422333,0.0)); pt37.setProp("attributes",{'jointId': '123', 'objType': 'hole', 'matId': None, 'boltGroup': 'joint_123_baseplate', 'ownerId': 'f5'})
pt38= points.newPntIDPos3d(38,geom.Pos3d(47.925,-0.02838125,0.0)); pt38.setProp("attributes",{'jointId': '123', 'objType': 'hole', 'matId': None, 'boltGroup': 'joint_123_baseplate', 'ownerId': 'f5'})
pt39= points.newPntIDPos3d(39,geom.Pos3d(47.909713235274225,-0.03471323527422332,0.0)); pt39.setProp("attributes",{'jointId': '123', 'objType': 'hole', 'matId': None, 'boltGroup': 'joint_123_baseplate', 'ownerId': 'f5'})
pt40= points.newPntIDPos3d(40,geom.Pos3d(47.90338125,-0.049999999999999996,0.0)); pt40.setProp("attributes",{'jointId': '123', 'objType': 'hole', 'matId': None, 'boltGroup': 'joint_123_baseplate', 'ownerId': 'f5'})
pt41= points.newPntIDPos3d(41,geom.Pos3d(47.909713235274225,-0.06528676472577667,0.0)); pt41.setProp("attributes",{'jointId': '123', 'objType': 'hole', 'matId': None, 'boltGroup': 'joint_123_baseplate', 'ownerId': 'f5'})
pt42= points.newPntIDPos3d(42,geom.Pos3d(47.925,-0.07161875000000001,0.0)); pt42.setProp("attributes",{'jointId': '123', 'objType': 'hole', 'matId': None, 'boltGroup': 'joint_123_baseplate', 'ownerId': 'f5'})
pt43= points.newPntIDPos3d(43,geom.Pos3d(47.940286764725776,-0.06528676472577669,0.0)); pt43.setProp("attributes",{'jointId': '123', 'objType': 'hole', 'matId': None, 'boltGroup': 'joint_123_baseplate', 'ownerId': 'f5'})
pt44= points.newPntIDPos3d(44,geom.Pos3d(47.925,-0.05,0.0)); pt44.setProp("attributes",{'jointId': '123', 'objType': 'hole_center', 'matId': 'A36', 'boltGroup': 'joint_123_baseplate', 'ownerId': 'f10', 'diameter': 0.024, 'boltMaterial': 'F1554gr36'})
pt45= points.newPntIDPos3d(45,geom.Pos3d(47.925,-0.05,-0.024)); pt45.setProp("attributes",{'jointId': '123', 'objType': 'anchor_point', 'matId': 'A36', 'boltGroup': 'joint_123_baseplate', 'ownerId': None, 'diameter': 0.024, 'boltMaterial': 'F1554gr36'})
pt46= points.newPntIDPos3d(46,geom.Pos3d(47.94661875,0.05,0.0)); pt46.setProp("attributes",{'jointId': '123', 'objType': 'hole', 'matId': None, 'boltGroup': 'joint_123_baseplate', 'ownerId': 'f5'})
pt47= points.newPntIDPos3d(47,geom.Pos3d(47.940286764725776,0.06528676472577667,0.0)); pt47.setProp("attributes",{'jointId': '123', 'objType': 'hole', 'matId': None, 'boltGroup': 'joint_123_baseplate', 'ownerId': 'f5'})
pt48= points.newPntIDPos3d(48,geom.Pos3d(47.925,0.07161875000000001,0.0)); pt48.setProp("attributes",{'jointId': '123', 'objType': 'hole', 'matId': None, 'boltGroup': 'joint_123_baseplate', 'ownerId': 'f5'})
pt49= points.newPntIDPos3d(49,geom.Pos3d(47.909713235274225,0.06528676472577669,0.0)); pt49.setProp("attributes",{'jointId': '123', 'objType': 'hole', 'matId': None, 'boltGroup': 'joint_123_baseplate', 'ownerId': 'f5'})
pt50= points.newPntIDPos3d(50,geom.Pos3d(47.90338125,0.05000000000000001,0.0)); pt50.setProp("attributes",{'jointId': '123', 'objType': 'hole', 'matId': None, 'boltGroup': 'joint_123_baseplate', 'ownerId': 'f5'})
pt51= points.newPntIDPos3d(51,geom.Pos3d(47.909713235274225,0.034713235274223334,0.0)); pt51.setProp("attributes",{'jointId': '123', 'objType': 'hole', 'matId': None, 'boltGroup': 'joint_123_baseplate', 'ownerId': 'f5'})
pt52= points.newPntIDPos3d(52,geom.Pos3d(47.925,0.02838125,0.0)); pt52.setProp("attributes",{'jointId': '123', 'objType': 'hole', 'matId': None, 'boltGroup': 'joint_123_baseplate', 'ownerId': 'f5'})
pt53= points.newPntIDPos3d(53,geom.Pos3d(47.940286764725776,0.03471323527422332,0.0)); pt53.setProp("attributes",{'jointId': '123', 'objType': 'hole', 'matId': None, 'boltGroup': 'joint_123_baseplate', 'ownerId': 'f5'})
pt54= points.newPntIDPos3d(54,geom.Pos3d(47.925,0.05,0.0)); pt54.setProp("attributes",{'jointId': '123', 'objType': 'hole_center', 'matId': 'A36', 'boltGroup': 'joint_123_baseplate', 'ownerId': 'f12', 'diameter': 0.024, 'boltMaterial': 'F1554gr36'})
pt55= points.newPntIDPos3d(55,geom.Pos3d(47.925,0.05,-0.024)); pt55.setProp("attributes",{'jointId': '123', 'objType': 'anchor_point', 'matId': 'A36', 'boltGroup': 'joint_123_baseplate', 'ownerId': None, 'diameter': 0.024, 'boltMaterial': 'F1554gr36'})

xcPointsDict= {0:pt0,1:pt1,2:pt2,3:pt3,4:pt4,5:pt5,6:pt6,7:pt7,8:pt8,9:pt9,10:pt10,11:pt11,12:pt12,13:pt13,14:pt14,15:pt15,16:pt16,17:pt17,18:pt18,19:pt19,20:pt20,21:pt21,22:pt22,23:pt23,24:pt24,25:pt25,26:pt26,27:pt27,28:pt28,29:pt29,30:pt30,31:pt31,32:pt32,33:pt33,34:pt34,35:pt35,36:pt36,37:pt37,38:pt38,39:pt39,40:pt40,41:pt41,42:pt42,43:pt43,44:pt44,45:pt45,46:pt46,47:pt47,48:pt48,49:pt49,50:pt50,51:pt51,52:pt52,53:pt53,54:pt54,55:pt55}

f0= surfaces.newQuadSurfacePts(0, 1, 7, 6); f0.setProp("attributes",{'jointId': '123', 'objType': 'column', 'loadTag': 151, 'loadDirI': [0.0, 0.0, 1.0], 'loadDirJ': [1.0, 0.0, 0.0], 'loadDirK': [0.0, 1.0, 0.0], 'shape': 'W18X35', 'part': 'bottom_flange', 'sub_part': 1, 'matId': 'A36'}); f0.setProp("thickness",0.012)
f1= surfaces.newQuadSurfacePts(1, 2, 8, 7); f1.setProp("attributes",{'jointId': '123', 'objType': 'column', 'loadTag': 151, 'loadDirI': [0.0, 0.0, 1.0], 'loadDirJ': [1.0, 0.0, 0.0], 'loadDirK': [0.0, 1.0, 0.0], 'shape': 'W18X35', 'part': 'bottom_flange', 'sub_part': 2, 'matId': 'A36'}); f1.setProp("thickness",0.012)
f2= surfaces.newQuadSurfacePts(3, 4, 10, 9); f2.setProp("attributes",{'jointId': '123', 'objType': 'column', 'loadTag': 151, 'loadDirI': [0.0, 0.0, 1.0], 'loadDirJ': [1.0, 0.0, 0.0], 'loadDirK': [0.0, 1.0, 0.0], 'shape': 'W18X35', 'part': 'top_flange', 'sub_part': 1, 'matId': 'A36'}); f2.setProp("thickness",0.012)
f3= surfaces.newQuadSurfacePts(4, 5, 11, 10); f3.setProp("attributes",{'jointId': '123', 'objType': 'column', 'loadTag': 151, 'loadDirI': [0.0, 0.0, 1.0], 'loadDirJ': [1.0, 0.0, 0.0], 'loadDirK': [0.0, 1.0, 0.0], 'shape': 'W18X35', 'part': 'top_flange', 'sub_part': 2, 'matId': 'A36'}); f3.setProp("thickness",0.012)
f4= surfaces.newQuadSurfacePts(1, 4, 10, 7); f4.setProp("attributes",{'jointId': '123', 'objType': 'column', 'loadTag': 151, 'loadDirI': [0.0, 0.0, 1.0], 'loadDirJ': [1.0, 0.0, 0.0], 'loadDirK': [0.0, 1.0, 0.0], 'part': 'web', 'matId': 'A36'}); f4.setProp("thickness",0.008)
f5= surfaces.newPolygonalFacePts([12, 13, 14, 15]); f5.setProp("attributes",{'jointId': '123', 'objType': 'baseplate', 'matId': 'A36'}); f5.setProp("thickness",0.015)
f6= surfaces.newPolygonalFacePts([16, 17, 18, 19, 20, 21, 22, 23]); f6.setProp("attributes",{'jointId': '123', 'objType': 'hole', 'matId': None, 'boltGroup': 'joint_123_baseplate', 'ownerId': 'f5'}); f6.setProp("thickness",0.0)
l7= lines.newLine(24, 25); l7.setProp("attributes",{'matId': None}); l7.setProp("thickness",0.0)
f8= surfaces.newPolygonalFacePts([26, 27, 28, 29, 30, 31, 32, 33]); f8.setProp("attributes",{'jointId': '123', 'objType': 'hole', 'matId': None, 'boltGroup': 'joint_123_baseplate', 'ownerId': 'f5'}); f8.setProp("thickness",0.0)
l9= lines.newLine(34, 35); l9.setProp("attributes",{'matId': None}); l9.setProp("thickness",0.0)
f10= surfaces.newPolygonalFacePts([36, 37, 38, 39, 40, 41, 42, 43]); f10.setProp("attributes",{'jointId': '123', 'objType': 'hole', 'matId': None, 'boltGroup': 'joint_123_baseplate', 'ownerId': 'f5'}); f10.setProp("thickness",0.0)
l11= lines.newLine(44, 45); l11.setProp("attributes",{'matId': None}); l11.setProp("thickness",0.0)
f12= surfaces.newPolygonalFacePts([46, 47, 48, 49, 50, 51, 52, 53]); f12.setProp("attributes",{'jointId': '123', 'objType': 'hole', 'matId': None, 'boltGroup': 'joint_123_baseplate', 'ownerId': 'f5'}); f12.setProp("thickness",0.0)
l13= lines.newLine(54, 55); l13.setProp("attributes",{'matId': None}); l13.setProp("thickness",0.0)
l14= lines.newLine(0, 1); l14.setProp("labels",['welds']); l14.setProp("attributes",{'jointId': '123', 'objType': 'weld', 'part': 'bottom_flange', 'sub_part': 1, 'legSize': 0.007, 'matId': 'A36', 'ownerId': 'f0'}); l14.setProp("thickness",None)
l15= lines.newLine(1, 2); l15.setProp("labels",['welds']); l15.setProp("attributes",{'jointId': '123', 'objType': 'weld', 'part': 'bottom_flange', 'sub_part': 2, 'legSize': 0.007, 'matId': 'A36', 'ownerId': 'f1'}); l15.setProp("thickness",None)
l16= lines.newLine(3, 4); l16.setProp("labels",['welds']); l16.setProp("attributes",{'jointId': '123', 'objType': 'weld', 'part': 'top_flange', 'sub_part': 1, 'legSize': 0.007, 'matId': 'A36', 'ownerId': 'f2'}); l16.setProp("thickness",None)
l17= lines.newLine(4, 5); l17.setProp("labels",['welds']); l17.setProp("attributes",{'jointId': '123', 'objType': 'weld', 'part': 'top_flange', 'sub_part': 2, 'legSize': 0.007, 'matId': 'A36', 'ownerId': 'f3'}); l17.setProp("thickness",None)
l18= lines.newLine(1, 4); l18.setProp("labels",['welds']); l18.setProp("attributes",{'jointId': '123', 'objType': 'weld', 'part': 'web', 'legSize': 0.006, 'matId': 'A36', 'ownerId': 'f4'}); l18.setProp("thickness",None)

xcBlocksDict= {0:f0,1:f1,2:f2,3:f3,4:f4,5:f5,6:f6,7:l7,8:f8,9:l9,10:f10,11:l11,12:f12,13:l13,14:l14,15:l15,16:l16,17:l17,18:l18}

