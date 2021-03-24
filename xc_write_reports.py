# -*- coding: utf-8 -*-
''' Write LaTeX reports about analysis results'''

from __future__ import division
from __future__ import print_function


from postprocess.reports import graphical_reports
from postprocess import limit_state_data as lsd
from materials.astm_aisc import AISC_limit_state_checking as aisc
from postprocess.reports import report_generator as rprt
from solution import predefined_solutions

exec(open("./xc_model.py").read()) # FE model generation
exec(open("./loads.py").read()) # Load generation

loadDispParameters= dict()

loadCasesToDisp= loadCaseNames

for lcn in loadCasesToDisp:
        lp= loadCaseManager.getLoadCase(lcn)
        dp= graphical_reports.getLoadCaseDispParametersFromLoadPattern(lp, modelSpace)
        dp.setsToDispLoads= []
        dp.setsToDispBeamLoads= [allMemberSet]
        dp.setsToDispIntForc= []
        dp.setsToDispBeamIntForc= [allMemberSet]#allMemberSetList
        loadDispParameters[lp.name]= dp

cfg= default_config.EnvConfig(language='en', fNameMark= 'xc_model.py')
cfg.projectDirTree.reportPath= 'reports/calculation_report/'
cfg.projectDirTree.resultsPath='calc_results/sole_zeinali/'
texReportFName= cfg.projectDirTree.getReportLoadsFile()  #laTex file where to include the graphics 
pathGrph= cfg.projectDirTree.getReportLoadsGrPath()   #directory to place the figures

textfl=open(texReportFName,'w')  #tex file to be generated
for lcn in loadCasesToDisp:
    if((lcn!='Tup') and (lcn!='Tdown')): # No external loads for thermal actions.
        lc= loadDispParameters[lcn]
        lc.writeLoadReport(modelSpace= modelSpace, texFile=textfl, cfg= cfg)
textfl.close()
## Set non-linear analysis.
modelSpace.analysis= predefined_solutions.penalty_newton_raphson(modelSpace.preprocessor.getProblem)

# Simple load cases results.
outFile= cfg.projectDirTree.getReportSimplLCFile()
grPath= cfg.projectDirTree.getReportSimplLCGrPath()
textfl=open(outFile,'w')  #tex file to be generated
for lcn in loadCasesToDisp:
    lc=  loadDispParameters[lcn]
    print(lcn)
    lc.simplLCReports(FEproblem=FEcase,texFile=textfl,cfg= cfg)
textfl.close()


#Load properties to display:
lsd.LimitStateData.envConfig= cfg
exec(open(cfg.projectDirTree.getVerifNormStrFile()).read())
exec(open(cfg.projectDirTree.getVerifShearFile()).read())
limitStateLabel= lsd.normalStressesResistance.label

setsBmEl= [allMemberSet]
argsBmEl=['CF','Mz','N']
report=rprt.ReportGenerator(modelSpace,cfg)
report.checksReport(limitStateLabel,[],[],setsBmEl,argsBmEl)
limitStateLabel= lsd.shearResistance.label
argsBmEl=['CF','Vy']
report.checksReport(limitStateLabel,[],[],setsBmEl,argsBmEl)
