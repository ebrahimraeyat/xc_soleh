# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import division


__author__= "Luis C. Pérez Tato (LCPT) Ana Ortega (AO_O)"
__copyright__= "Copyright 2020, LCPT, AO_O"
__license__= "GPL"
__version__= "3.0"
__email__= "l.pereztato@gmail.com, ana.ortega.ort@gmail.com"

import xc_base
import geom
import xc
from misc_utils import log_messages as lmsg
from solution import predefined_solutions

class VonMisesSolutionProcedure(predefined_solutions.SolutionProcedure):

    def __init__(self, maxNumIter= 10, convergenceTestTol= 1e-9):
        ''' Constructor.

        :param maxNumIter: maximum number of iterations (defauts to 10)
        :param convergenceTestTol: convergence tolerance (defaults to 1e-9)
        '''
        super(VonMisesSolutionProcedure,self).__init__(maxNumIter, convergenceTestTol)
            
    def testKrylovNewton(self,prb, maxDim= 6):
        ''' Return a static solution procedure with a modified Newton
            solution algorithm with a plain constraint handler.

        See appendix C. Analysis model script of the document
        "Finite Element Modeling of Gusset Plate Failure Using Opensees"
        Andrew J. Walker. Oregon State University
        '''
        self.solu= prb.getSoluProc
        self.solCtrl= self.solu.getSoluControl
        solModels= self.solCtrl.getModelWrapperContainer
        self.sm= solModels.newModelWrapper("sm")
        self.numberer= self.sm.newNumberer("default_numberer")
        self.numberer.useAlgorithm("simple")
        self.cHandler= self.getConstraintHandler('transformation') # works!
        #self.cHandler= self.getConstraintHandler('lagrange') # segmentation fault!
        #self.cHandler= self.getConstraintHandler('penalty') # too slow!
        solutionStrategies= self.solCtrl.getSolutionStrategyContainer
        self.solutionStrategy= solutionStrategies.newSolutionStrategy("solutionStrategy","sm")
        self.solAlgo= self.solutionStrategy.newSolutionAlgorithm("krylov_newton_soln_algo")
        self.solAlgo.maxDimension= maxDim
        self.integ= self.solutionStrategy.newIntegrator("load_control_integrator",xc.Vector([]))
        self.ctest= self.solutionStrategy.newConvergenceTest("energy_inc_conv_test")
        self.ctest.tol= self.convergenceTestTol
        self.ctest.maxNumIter= 150 #Make this configurable
        self.ctest.printFlag= self.printFlag
        self.soe= self.solutionStrategy.newSystemOfEqn("sparse_gen_col_lin_soe")
        self.solver= self.soe.newSolver("super_lu_solver")
        #self.soe= self.solutionStrategy.newSystemOfEqn("band_gen_lin_soe")
        #self.solver= self.soe.newSolver("band_gen_lin_lapack_solver")
        #self.soe= self.solutionStrategy.newSystemOfEqn("umfpack_gen_lin_soe")
        #self.solver= self.soe.newSolver("umfpack_gen_lin_solver")
        self.analysis= self.solu.newAnalysis("static_analysis","solutionStrategy","")
        return self.analysis
      

def test_krylov_newton(prb, mxNumIter= 300, convergenceTestTol= 1e-9, printFlag= 0):
    ''' Return a penalty Krylov Newton solution procedure.

    :ivar maxNumIter: maximum number of iterations (defauts to 300)
    :ivar convergenceTestTol: convergence tolerance (defaults to 1e-9)
    :ivar printFlag: print message on each iteration
    '''
    solution= VonMisesSolutionProcedure()
    solution.maxNumIter= mxNumIter
    solution.convergenceTestTol= convergenceTestTol
    solution.printFlag= printFlag
    return solution.testKrylovNewton(prb)

