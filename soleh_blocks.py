preprocessor= FEcase.getPreprocessor
nodes= preprocessor.getNodeHandler
elements= preprocessor.getElementHandler
points= preprocessor.getMultiBlockTopology.getPoints
lines= preprocessor.getMultiBlockTopology.getLines
surfaces= preprocessor.getMultiBlockTopology.getSurfaces
groups= preprocessor.getSets
# imported from file: /home/ebi/xc/my_models/sole_zeinali/aux/soleh.FCStd on 2021-02-21 12:05:35.944220
pt0= points.newPntIDPos3d(0,geom.Pos3d(0.0,0.0,0.0)); pt0.setProp("labels",['IFCSoleh'])
pt1= points.newPntIDPos3d(1,geom.Pos3d(0.0,7.6,0.0)); pt1.setProp("labels",['IFCSoleh'])
pt2= points.newPntIDPos3d(2,geom.Pos3d(12.5,12.14962792832753,0.0)); pt2.setProp("labels",['IFCSoleh'])
pt3= points.newPntIDPos3d(3,geom.Pos3d(25.000000000000004,7.6,0.0)); pt3.setProp("labels",['IFCSoleh'])
pt4= points.newPntIDPos3d(4,geom.Pos3d(25.000000000000004,0.0,0.0)); pt4.setProp("labels",['IFCSoleh'])
pt5= points.newPntIDPos3d(5,geom.Pos3d(37.5,12.149627928327531,0.0)); pt5.setProp("labels",['IFCSoleh'])
pt6= points.newPntIDPos3d(6,geom.Pos3d(50.0,7.6,0.0)); pt6.setProp("labels",['IFCSoleh'])
pt7= points.newPntIDPos3d(7,geom.Pos3d(50.0,0.0,0.0)); pt7.setProp("labels",['IFCSoleh'])

xcPointsDict= {0:pt0,1:pt1,2:pt2,3:pt3,4:pt4,5:pt5,6:pt6,7:pt7}

l0= lines.newLine(0, 1); l0.setProp("labels",['IFCSoleh']); l0.setProp("attributes",{'IfcType': 'Structural Curve Member', 'PredefinedType': 'RIGID_JOINED_MEMBER', 'IfcProperties': {}, 'matId': None}); l0.setProp("thickness",0.0)
l1= lines.newLine(1, 2); l1.setProp("labels",['IFCSoleh']); l1.setProp("attributes",{'IfcType': 'Structural Curve Member', 'PredefinedType': 'RIGID_JOINED_MEMBER', 'IfcProperties': {}, 'matId': None}); l1.setProp("thickness",0.0)
l2= lines.newLine(2, 3); l2.setProp("labels",['IFCSoleh']); l2.setProp("attributes",{'IfcType': 'Structural Curve Member', 'PredefinedType': 'RIGID_JOINED_MEMBER', 'IfcProperties': {}, 'matId': None}); l2.setProp("thickness",0.0)
l3= lines.newLine(4, 3); l3.setProp("labels",['IFCSoleh']); l3.setProp("attributes",{'IfcType': 'Structural Curve Member', 'PredefinedType': 'RIGID_JOINED_MEMBER', 'IfcProperties': {}, 'matId': None}); l3.setProp("thickness",0.0)
l4= lines.newLine(3, 5); l4.setProp("labels",['IFCSoleh']); l4.setProp("attributes",{'IfcType': 'Structural Curve Member', 'PredefinedType': 'RIGID_JOINED_MEMBER', 'IfcProperties': {}, 'matId': None}); l4.setProp("thickness",0.0)
l5= lines.newLine(5, 6); l5.setProp("labels",['IFCSoleh']); l5.setProp("attributes",{'IfcType': 'Structural Curve Member', 'PredefinedType': 'RIGID_JOINED_MEMBER', 'IfcProperties': {}, 'matId': None}); l5.setProp("thickness",0.0)
l6= lines.newLine(7, 6); l6.setProp("labels",['IFCSoleh']); l6.setProp("attributes",{'IfcType': 'Structural Curve Member', 'PredefinedType': 'RIGID_JOINED_MEMBER', 'IfcProperties': {}, 'matId': None}); l6.setProp("thickness",0.0)

xcBlocksDict= {0:l0,1:l1,2:l2,3:l3,4:l4,5:l5,6:l6}

