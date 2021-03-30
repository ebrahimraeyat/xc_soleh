# - * - coding: utf-8 - * -
from actions import combinations as cc
# Definition of USL and SLS

#    * *  * LIMIT STATE COMBINATIONS * * * 
combContainer= cc.CombContainer()  #Container of load combinations


# COMBINATIONS OF ACTIONS FOR ULTIMATE LIMIT STATES
# DL = dead load
# LR = roof live load
# W-out-vertical = Vertical wind load
# W-out-parallel = Parallel wind load
# W-inPositive = Positive wind load inside
# W-inNegative = Negative wind load inside
# SBalanced= Balanced snow load
# S-unbalanced= Unbalanced snow load
# E= earthquaque load due to dead load
# according to mabhas6-98(Part 6-2-3-2)
combContainer.ULS.perm.add('ULS01', '1.4 * DL')

combContainer.ULS.perm.add('ULS02a', '1.2 * DL + .5 * SBalanced')
combContainer.ULS.perm.add('ULS02b', '1.2 * DL + .5 * SUnbalancedRight')
combContainer.ULS.perm.add('ULS02c', '1.2 * DL + .5 * SUnbalancedLeft')

combContainer.ULS.perm.add('ULS03a', '1.2 * DL + 1.6 * SBalanced + 0.8 * wxPos + 0.8 * winPos')
combContainer.ULS.perm.add('ULS03b', '1.2 * DL + 1.6 * SBalanced + 0.8 * wxPos + 0.8 * winNeg')
combContainer.ULS.perm.add('ULS03c', '1.2 * DL + 1.6 * SBalanced + 0.8 * wyPos + 0.8 * winPos')
combContainer.ULS.perm.add('ULS03d', '1.2 * DL + 1.6 * SBalanced + 0.8 * wyPos + 0.8 * winNeg')
combContainer.ULS.perm.add('ULS03e', '1.2 * DL + 1.6 * SBalanced + 0.8 * wyNeg + 0.8 * winPos')
combContainer.ULS.perm.add('ULS03f', '1.2 * DL + 1.6 * SBalanced + 0.8 * wyNeg + 0.8 * winNeg')
combContainer.ULS.perm.add('ULS03g', '1.2 * DL + 1.6 * SUnbalancedRight + 0.8 * wxPos + 0.8 * winPos')
combContainer.ULS.perm.add('ULS03h', '1.2 * DL + 1.6 * SUnbalancedRight + 0.8 * wxPos + 0.8 * winNeg')
combContainer.ULS.perm.add('ULS03i', '1.2 * DL + 1.6 * SUnbalancedLeft + 0.8 * wxNeg + 0.8 * winPos')
combContainer.ULS.perm.add('ULS03j', '1.2 * DL + 1.6 * SUnbalancedLeft + 0.8 * wxNeg + 0.8 * winNeg')

combContainer.ULS.perm.add('ULS04a', '1.2 * DL + .5 * SBalanced + 1.6 * wxPos + 1.6 * winPos')
combContainer.ULS.perm.add('ULS04b', '1.2 * DL + .5 * SBalanced + 1.6 * wxPos + 1.6 * winNeg')
combContainer.ULS.perm.add('ULS04c', '1.2 * DL + .5 * SBalanced + 1.6 * wyPos + 1.6 * winPos')
combContainer.ULS.perm.add('ULS04d', '1.2 * DL + .5 * SBalanced + 1.6 * wyPos + 1.6 * winNeg')
combContainer.ULS.perm.add('ULS04e', '1.2 * DL + .5 * SBalanced + 1.6 * wyNeg + 1.6 * winPos')
combContainer.ULS.perm.add('ULS04f', '1.2 * DL + .5 * SBalanced + 1.6 * wyNeg + 1.6 * winNeg')
combContainer.ULS.perm.add('ULS04g', '1.2 * DL + .5 * SUnbalancedRight + 1.6 * wxPos + 1.6 * winPos')
combContainer.ULS.perm.add('ULS04h', '1.2 * DL + .5 * SUnbalancedRight + 1.6 * wxPos + 1.6 * winNeg')
combContainer.ULS.perm.add('ULS04i', '1.2 * DL + .5 * SUnbalancedLeft + 1.6 * wxNeg + 1.6 * winPos')
combContainer.ULS.perm.add('ULS04j', '1.2 * DL + .5 * SUnbalancedLeft + 1.6 * wxNeg + 1.6 * winNeg')

combContainer.ULS.perm.add('ULS05a', '0.9 * DL + 1.6 * wxPos + 1.6 * winNeg')
combContainer.ULS.perm.add('ULS05b', '0.9 * DL + 1.6 * wxNeg + 1.6 * winNeg')
combContainer.ULS.perm.add('ULS05c', '0.9 * DL + 1.6 * wyPos + 1.6 * winNeg')
combContainer.ULS.perm.add('ULS05c', '0.9 * DL + 1.6 * wyNeg + 1.6 * winNeg')

# Dump combination definition into XC.
combContainer.dumpCombinations(preprocessor)



