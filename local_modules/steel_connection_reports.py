# -*- coding: utf-8 -*-
import os.path
from postprocess import output_handler
import steel_connection
from solution import predefined_solutions


def gen_report_files(modelSpace,genDescr,specDescr,loadCaseNames,reportPath,rltvResPath,grWidth,texfileNm,boltSets2Check=[],welds2Check=[],baseMetal=None,meanShearProc=True,genGrULSs=True,linear=True,warningsFile=None,Phi=0.75):
    '''Generates the graphics corresponding to loads and displacements for each load case,
    together with the tex file to include them in a report.

    :param genDescr: general description
    :param specDescr: specific description
    :param loadCaseNames: list of load case names
    :param reportPath: directory where report is to be generated
    :param rltvResPath: directory where to place the text file relative to reportPath
    :param grWidth: with to insert the graphics
    :param texfileNm: name of the tex file.
    :param boltSets2Check: list of pairs (bolt set, bolt type) with the
          set of bolts and bolt material (instance of class
          astm.BoltFastener) to be analyzed. (Defaults to [])
    :param welds2Check: welds (instances of classes FilletWeld or multiFilletWeld) to check
    :param baseMetal: steel of the plate (only used when welds are checked). Defaults to None
    :param meanShearProc: if True, each bolt is verified using the mean shear of 
                          the set of bolts (defaults to True)
    :param genGrULSs: generate graphics of loads and displacements for all
                      the load cases. (Defaults to True)
    :param linear: if linear analysis (default) = True, else nonlinear analysis.
    :param warningsFile: name of the file of warnings (defaults to None)
    :param Phi: resistance factor (defaults to 0.75)
    '''
    oh= output_handler.OutputHandler(modelSpace)
    resPath=reportPath+rltvResPath
    if not os.path.isdir(resPath): os.mkdir(resPath)
    grPath=resPath+'graphics/'
    if not os.path.isdir(grPath): os.mkdir(grPath)
    texPath=reportPath+rltvResPath ; grPath=texPath+'graphics/'; rltvGrPath=rltvResPath+'graphics/'
    # Initialize properties of bolts and welds
    steel_connection.init_prop_checking_bolts(boltSets2Check)
    singlWelds=steel_connection.init_prop_checking_welds(welds2Check)
    # load cases
    lcNm=[str(ULS) for ULS in loadCaseNames]
    lcNm.sort()
    if genGrULSs: f=open(texPath+texfileNm+'_load_disp.tex','w')
    cont=0
    if linear:
#        modelSpace.solutionProcedureType= predefined_solutions.simple_static_linear(modelSpace.getProblem())
        modelSpace.solutionProcedureType=  predefined_solutions.SimpleStaticLinear
    else:
        modelSpace.solutionProcedureType=  predefined_solutions.PenaltyModifiedNewton(modelSpace.getProblem(), maxNumIter=25, convergenceTestTol= 5.0e-2, printFlag= 2)
    for ULS in lcNm:
        txtDescr=genDescr+' '+specDescr+' '+ULS + ': '
        modelSpace.removeAllLoadPatternsFromDomain()
        modelSpace.revertToStart()
        modelSpace.addLoadCaseToDomain(ULS)
        result= modelSpace.analyze(calculateNodalReactions= True)
        if genGrULSs:
            #loads
            captFig=specDescr+' '+ ULS + ': loads [kN]'
            graphNm=texfileNm+'_'+ULS+'_loads'
            oh.displayLoads(caption=captFig,fileName=grPath+graphNm+'.jpg')
            captTxt=txtDescr+ 'loads [kN]'
            addGraph2Tex(f,rltvGrPath+graphNm,captTxt,grWidth)
            #displacements
            graphNm=texfileNm+'_'+ULS+'_uX'
            oh.displayDispRot(itemToDisp='uX',fileName=grPath+graphNm+'.jpg')
            captTxt=txtDescr+ 'displacement in global X direction [mm]'
            addGraph2Tex(f,rltvGrPath+graphNm,captTxt,grWidth)
            graphNm=texfileNm+'_'+ULS+'_uY'
            oh.displayDispRot(itemToDisp='uY',fileName=grPath+graphNm+'.jpg')
            captTxt=txtDescr+ 'displacement in global Y direction [mm]'
            addGraph2Tex(f,rltvGrPath+graphNm,captTxt,grWidth)
            graphNm=texfileNm+'_'+ULS+'_uZ'
            oh.displayDispRot(itemToDisp='uZ',fileName=grPath+graphNm+'.jpg')
            captTxt=txtDescr+ 'displacement in global Z direction [mm]'
            addGraph2Tex(f,rltvGrPath+graphNm,captTxt,grWidth)
            cont+=3
            if cont>20:
                f.write('\\clearpage \n')
                cont=0
        #Bolts checking
        steel_connection.set_bolt_check_resprop_current_LC(ULS,boltSets2Check,meanShearProc)
        #Welds checking
        steel_connection.set_welds_check_resprop_current_LC(ULS,singlWelds,baseMetal,Phi)
    if genGrULSs: f.close()
    #generate graphics of internal forces in welds
    cont=0
    for w in  singlWelds:
        weld=w[0]
        par=w[1]
        ULS=par[0]
        modelSpace.removeAllLoadPatternsFromDomain()
        modelSpace.addLoadCaseToDomain(ULS)
        result= modelSpace.analyze(calculateNodalReactions= True)
        graphNm=texfileNm+'weld'+str(cont)
        w[1].append(rltvGrPath+graphNm)
        oh.displayIntForcDiag('N',weld.weldSet,fileName=grPath+graphNm+'_N.jpg')
        oh.displayIntForcDiag('Vy',weld.weldSet,fileName=grPath+graphNm+'_Vy.jpg')
        oh.displayIntForcDiag('Vz',weld.weldSet,fileName=grPath+graphNm+'_Vz.jpg')
        cont+=1
    #print results of bolt checking
    if len(boltSets2Check)>0:
        Lres=print_bolt_results(boltSets2Check)
        f=open(texPath+texfileNm+'_bolts.tex','w')
        f.writelines(Lres)
        f.close()
    #print results of weld checking
    if len(welds2Check)>0:
        Lres=print_welds_results(singlWelds)
        f=open(texPath+texfileNm+'_welds.tex','w')
        f.writelines(Lres)
        f.close()
    if warningsFile:
        steel_connection.write_check_warnings(warningsFile,boltSets2Check,singlWelds)

def addGraph2Tex(texFile,graph2add,caption,grWidth):
    lhead=['\\begin{figure} \n','\\begin{center} \n']
    texFile.writelines(lhead)
    texFile.write('\\includegraphics[width='+grWidth+']{'+graph2add+'} \n')
    texFile.write('\\caption{'+caption+'} \n')
    lfoot=['\\end{center} \n','\\end{figure} \n','\n']
    texFile.writelines(lfoot)

    
def print_bolt_results(boltSets2Check):
    '''return a list with the results to print in a latex file

    :param boltSets2Check: list of pairs (bolt set, bolt type) with the
          set of bolts and bolt material (instance of class
          astm.BoltFastener) to print results.
    '''
    retval=list()
    retval.append('\\begin{center} \n')
    retval.append('\\begin{longtable}{|c|c|c|c|c|} \n')
    retval.append('\\endfirsthead \n')
    retval.append('\\multicolumn{5}{l}{\\textit{\\ldots(continued from previous page)}} \\\\ \n')
    retval.append('\\hline \n')
    retval.append('\\endhead \n')
    retval.append('\\hline \n')
    retval.append('\\multicolumn{5}{r}{\\textit{(continued on next page)\\ldots }} \\\\ \n')
    retval.append('\\endfoot \n')
    retval.append('\\endlastfoot \n')
    for checkIt in  boltSets2Check:
        bset=checkIt[0]
        btype=checkIt[1]  #bolt type
        retval.append('\\hline \n')
        retval.append('\\multicolumn{5}{|l|}{\\textsc{Bolt set: ' + bset.description +'}} \\\\ \n')
        retval.append('\\multicolumn{1}{|l}{bolt steel = ' + btype.steelType.name + '} & \\multicolumn{2}{l}{bolt diam. = ' + str(btype.diameter*1e3) +' mm} & \\multicolumn{2}{l|}{bolt area = ' + str(round(btype.getArea()*1e4,2)) +  ' $cm^2$}  \\\\  \n')
        retval.append('\\multicolumn{1}{|l}{\\small{nominal tensile and shear strength:}} & \\multicolumn{2}{l}{$F_{nt}$ = ' + str(round(btype.getNominalTensileStrength()*1e-3,2)) + ' kN/bolt} & \\multicolumn{2}{l|}{$F_{nv}$ = ' + str(round(btype.getNominalShearStrength()*1e-3,2)) + ' kN/bolt}  \\\\  \n')
        retval.append('\\multicolumn{1}{|l}{\\small{design tensile and shear strength:}} & \\multicolumn{2}{l}{$\Phi F_{nt}$ = ' + str(round(btype.getDesignTensileStrength()*1e-3,2)) + ' kN/bolt} & \\multicolumn{2}{l|}{$\Phi F_{nv}$ = ' + str(round(btype.getDesignShearStrength()*1e-3,2)) + ' kN/bolt}  \\\\  \n')
        retval.append('\\hline \n')
        retval.append('\\textbf{Bolt coord.} [m] & \\textbf{ULS} & \\textbf{N} [kN] & \\textbf{V} [kN] & \\textbf{CF} \\\\ \n')
        retval.append('\\hline \n')
        CFmax=0
        for e in bset.elements:
            CF=e.getProp('CF')
            if CF>CFmax: CFmax=CF
            eCoord=e.getCooCentroid(True)
            retval.append('(' +  str(round(eCoord[0],3)) +  ',' + str(round(eCoord[1],3)) +  ',' + str(round(eCoord[2],3)) +  ') & ' +  str(e.getProp('LS')) +  ' & ' +  str(round((e.getProp('N')*1e-3),2)) +  ' & ' +  str(round((e.getProp('V')*1e-3),2)) + ' & ' +  str(round(CF,3))  +  '\\\\ \n')
        retval.append('\\hline \n')
        retval.append('\\multicolumn{4}{|r|}{Maximum capacity factor:} & ' +  str(round(CFmax,3))  +  '\\\\ \n')
        retval.append('\\hline \n')
    retval.append('\\end{longtable} \n')
    retval.append('\\end{center} \n')
    return retval

def print_welds_results(singlWelds):
    '''return a list with the results to print in a latex file

    :param singlWelds: list of welds and results generated during 
          weld checking
    '''
    retval=list()
    retval.append('\\begin{center} \n')
    retval.append('\\begin{longtable}{|c|c|c|c|c|c|} \n')
    retval.append('\\hline \n')
    retval.append('\\endfirsthead \n')
    retval.append('\\multicolumn{6}{l}{\\textit{\\ldots(continued from previous page)}} \\\\ \n')
    retval.append('\\hline \n')
    retval.append('\\endhead \n')
    retval.append('\\hline \n')
    retval.append('\\multicolumn{6}{r}{\\textit{(continued on next page)\\ldots }} \\\\ \n')
    retval.append('\\endfoot \n')
    retval.append('\\endlastfoot \n')
    for w in  singlWelds:
        weld=w[0]
        par=w[1]
        retval.append('\\hline \n')
        retval.append('\\multicolumn{6}{|l|}{\\textsc{Weld: ' + weld.descr + '}} \\\\ \n')
        retval.append('\\multicolumn{6}{|l|}{filler metal: ' + weld.weldMetal.name + '}\\\\ \n')
        retval.append('\\multicolumn{1}{|l}{weld size limits:} & \\multicolumn{2}{l}{$t_{plate1}$=' + str(round(weld.tWS1*1e3,1)) + ' mm} &   \\multicolumn{3}{l|}{$t_{plate2}$=' + str(round(weld.tWS2*1e3,1)) + ' mm } \\\\ \n')
        retval.append('\\multicolumn{1}{|l}{} &  \\multicolumn{2}{l}{$w_{min}$=' + str(round(weld.minSz*1e3,1)) + ' mm} &   \\multicolumn{3}{l|}{$w_{max}$=' + str(round(weld.maxSz*1e3,1)) + ' mm}  \\\\ \n')
        retval.append('\\multicolumn{1}{|l}{weld size: \\textbf{w=' + str(round(weld.weldSz*1e3,1)) +  ' mm}} & \\multicolumn{2}{l}{actual throat: a=' + str(round(weld.weldThroat*1e3,1)) + ' mm} & \\multicolumn{3}{l|}{weld length: L=' + str(round(weld.length*1e3,0)) + ' mm} \\\\ \n')  
        retval.append('\\hline \n')
#        retval.append( '\\textbf{Extr. point coord. [m]} & \\textbf{ULS} & \\textbf{$F_{par}$} [kN] &  \\textbf{$F_{perp}$} [kN]&   \\textbf{$\Phi R_n$} [kN]&   \\textbf{CF} \\\\ \n')
#        retval.append('\\hline \n')
#        retval.append( '(' + str(round(weld.weldP1[0],3)) + ',' + str(round(weld.weldP1[1],3)) + ',' + str(round(weld.weldP1[2],3)) + ')  & ' +  par[0]  +  ' & ' +  str(round(par[1]*1e-3,2))  +  ' & ' +  str(round(par[2]*1e-3,2))  +  ' & ' +  str(round(par[3]*1e-3,2))  +  ' & ' + str(round(par[-1],3)) +  '\\\\ \n')
#        retval.append( '(' + str(round(weld.weldP2[0],3)) + ',' + str(round(weld.weldP2[1],3)) + ',' + str(round(weld.weldP2[2],3)) + ')  & & & & & \\\\ \n')
        retval.append('\\multicolumn{6}{|l|}{CF=' + str(round(par[1],2)) + '   in load case:' + par[0]+'} \\\\')
        retval.append('\\hline \n')
        retval.append('\\multicolumn{3}{|c|}{\includegraphics[height=50mm]{'+par[2]+'_N}} & \\multicolumn{3}{|c|}{\includegraphics[height=50mm]{'+ par[2]+'_Vy}} \\\\')
        retval.append('\\hline \n')
    retval.append('\\end{longtable} \n')
    retval.append('\\end{center} \n')
    return retval



def display_weld_results(modelSpace,welds2Check,ULS,set2displ=None):
    '''Calculate limit state ULS and display internal forces
    in welds. Print the total internal forces for each weld seam.
    set2displ is the set to display displacements (defaults to None)
    '''
    singlWelds=steel_connection.init_prop_checking_welds(welds2Check)
    lstWEldSets=[w[0].weldSet for w in singlWelds]
    oh= output_handler.OutputHandler(modelSpace)
    # weldsSet=modelSpace.setSum('weldsSet',lstWEldSets)
    # oh.displayFEMesh(weldsSet)
    modelSpace.removeAllLoadPatternsFromDomain()
    modelSpace.addLoadCaseToDomain(ULS)
    modelSpace.analyze(calculateNodalReactions=True)
    for w in singlWelds:
        descr=w[0].descr
        st=w[0].weldSet
        if set2displ:
            oh.displayDispRot('uX',set2displ)
            oh.displayDispRot('uY',set2displ)
            oh.displayDispRot('uZ',set2displ)
        oh.displayIntForcDiag('N',st)
        oh.displayIntForcDiag('Vy',st)
        oh.displayIntForcDiag('Vz',st)
        N=0
        Vper=0
        Vpar=0
        for e in st.elements:
            N+=e.getN()
            Vper+=e.getVy()
            Vpar+=e.getVz()
        print(descr,' N=',round(N*1e-3),' Vper=',round(Vper*1e-3), ' Vpar=',round(Vpar*1e-3))

from postprocess.xcVtk import vtk_graphic_base
from postprocess import limit_state_data as lsd
from postprocess.control_vars import VonMisesControlVars

def gen_baseplates_vonmises_results(sets2disp,modelSpace,genDescr,specDescr,reportPath,rltvResPath,grWidth,texfileNm,resVMfile='./results/verifications/verifRsl_VonMisesStressULS.py'):
    '''Generates the graphics corresponding to loads and displacements for each load case,
    together with the tex file to include them in a report.

    :param genDescr: general description
    :param specDescr: specific description
    :param loadCaseNames: list of load case names
    :param reportPath: directory where report is to be generated
    :param rltvResPath: directory where to place the text file relative to reportPath
    :param grWidth: with to insert the graphics
    :param texfileNm: name of the tex file.
    :param resVMfile: file containing results from Von Mises verification (defaults 
                      to './results/verifications/verifRsl_VonMisesStressULS.py')
    '''
    preprocessor=modelSpace.preprocessor
    limitState= lsd.vonMisesStressResistance
    exec(open(resVMfile).read())
    oh= output_handler.OutputHandler(modelSpace)
    resPath=reportPath+rltvResPath
    if not os.path.isdir(resPath): os.mkdir(resPath)
    grPath=resPath+'graphics/'
    if not os.path.isdir(grPath): os.mkdir(grPath)
    texPath=reportPath+rltvResPath ; grPath=texPath+'graphics/'; rltvGrPath=rltvResPath+'graphics/'
    f=open(texPath+texfileNm+'_vonmises.tex','w')
    camD1=vtk_graphic_base.CameraParameters('+X+Y+Z')  #camera dihedral 1
    camD3=vtk_graphic_base.CameraParameters('-X-Y+Z')   #camera dihedral 3
    txtDescr='ULS Von Mises stress check. ' + genDescr+' '+specDescr + ' '
    for st in sets2disp:
        setdescr=st.name.replace('Set',' ')
        setdescr=setdescr.replace('Gusset',' '+ 'gusset')
        setdescr=setdescr.capitalize()
        oh.setCameraParameters(camD1)
        graphNm=texfileNm+'_vonmisesStress'+st.name
        captTxt=txtDescr+ setdescr + '. Envelope of Von Misses stress (MPa)'
        oh.displayField(limitStateLabel= limitState.label, section= None, argument='vm_stress', component= None, setToDisplay= st, fileName= grPath+graphNm+'.jpg')
        addGraph2Tex(f,rltvGrPath+graphNm,captTxt,grWidth)
        graphNm=texfileNm+'_vonmisesCF'+st.name
        captTxt=txtDescr+ setdescr + '. Efficiency'
        oh.displayField(limitStateLabel= limitState.label, section= None, argument='CF', component= None, setToDisplay= st, fileName= grPath+graphNm+'.jpg')
        addGraph2Tex(f,rltvGrPath+graphNm,captTxt,grWidth)
    if 'gusset' in st.name.lower():
        oh.setCameraParameters(camD3)
        graphNm=texfileNm+'_vonmisesStress_view2'+st.name
        captTxt=txtDescr+ setdescr + '. Envelope of Von Misses stress (MPa)'
        oh.displayField(limitStateLabel= limitState.label, section= None, argument='vm_stress', component= None, setToDisplay= st, fileName= grPath+graphNm+'.jpg')
        addGraph2Tex(f,rltvGrPath+graphNm,captTxt,grWidth)
        graphNm=texfileNm+'_vonmisesCF_view2'+st.name
        captTxt=txtDescr+ setdescr + '. Efficiency'
        oh.displayField(limitStateLabel= limitState.label, section= None, argument='CF', component= None, setToDisplay= st, fileName= grPath+graphNm+'.jpg')
        addGraph2Tex(f,rltvGrPath+graphNm,captTxt,grWidth)
    f.close()
