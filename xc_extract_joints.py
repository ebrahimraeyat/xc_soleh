# -*- coding: utf-8 -*-
''' Extract the model joints and put them in a DXF file. It's useful to
compute the number and complexity of the joints.'''


exec(open('./xc_model.py').read())

import ezdxf

joints= dict()
setNames= set()
for p in xcTotalSet.getPoints:
    nl= p.getNLines
    length= 0.0
    lineTags= p.getConnectedEdgesTags;
    for ltag in lineTags:
        l= xcTotalSet.lines.findTag(ltag)
        assert(ltag==l.tag)
        length+= l.getLength()
    length= round(length,0)
    setName= 'joints_'+str(nl)+'_legs_'+str(length)
    setNames.add(setName)
    joints[p.tag]= [nl, length, lineTags, setName]

# Create sets.
xcSets= list()
for key in setNames:
    xcSet= preprocessor.getSets.defSet(key)
    xcSets.append(xcSet)
    
# Populate sets.
for key in joints:
    joint= joints[key]
    setName= joint[-1]
    xcSet= preprocessor.getSets.getSet(setName)
    pt= xcTotalSet.points.findTag(key)
    xcSet.points.append(pt)

dwg= ezdxf.new()
msp= dwg.modelspace()
color= 0

for xcSet in xcSets:
    xcSet.fillUpwards()
    layerName= xcSet.name
    dwg.layers.new(name= layerName, dxfattribs={'color': color})
    print(layerName,',',xcSet.points.size)
    color+= 1
    for p in xcSet.points: # joint
        pos= p.getPos
        v = (pos.x, pos.z, pos.y)
        msp.add_point(v, dxfattribs={'layer': layerName})
        # msp.add_text(str(p.tag), dxfattribs={'layer': layerName, 'height': 0.35}).set_pos(v)
        length= joints[p.tag][1]
        lineTags= joints[p.tag][2]
        for tag in lineTags: # bars of this joint.
            l= xcSet.lines.findTag(tag)
            assert(tag==l.tag)
            length+= l.getLength()
            c= pos+(l.getCentroid()-pos)*.5
            msp.add_line((pos.x,pos.z,pos.y),(c.x,c.z,c.y), dxfattribs={'layer': layerName})
dwg.saveas('soleh_zeinali_joints.dxf')
