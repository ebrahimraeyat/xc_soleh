# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function



exec(open('./xc_connection_model.py').read())

sys.path.insert(0, '../../local_modules')
import steel_connection_reports
genDescr='Stair tower.'
specDescr='Base plate connections.'
reportPath= '../../../reports/calculation_report/'
rltvResPath='connections/stair_tower/results/'
grWidth='\\linewidth'
texfileNm='baseplates'

# Generation of graphics corresponding to loads and displacements for each load case and checking of bolts and welds   
#steel_connection_reports.gen_report_files(modelSpace,genDescr,specDescr,loadCaseNames,reportPath,rltvResPath,grWidth,texfileNm,boltSets2Check=lstBoltSets2Check, welds2Check=welds2Check, baseMetal=connection_meshing.steel_dict['A36'],meanShearProc=True)
steel_connection_reports.gen_report_files(modelSpace,genDescr,specDescr,loadCaseNames,reportPath,rltvResPath,grWidth,texfileNm,boltSets2Check=[], welds2Check=welds2Check, baseMetal=connection_meshing.steel_dict['A36'],meanShearProc=True,genGrULSs=False,warningsFile='warnings.tex')

'''
sets2disp=[columnSet,baseplateSet,webGussetSet]
steel_connection_reports.gen_baseplates_vonmises_results(sets2disp,modelSpace,genDescr,specDescr,reportPath,rltvResPath,grWidth,texfileNm)
'''

