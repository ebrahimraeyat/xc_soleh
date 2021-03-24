# -*- coding: utf-8 -*-
from actions import combinations as cc
# Definition of USL and SLS

#    ***LIMIT STATE COMBINATIONS***
combContainer= cc.CombContainer()  #Container of load combinations


# COMBINATIONS OF ACTIONS FOR ULTIMATE LIMIT STATES
# DL = dead load
# LR = roof live load
# W_out_vertical = Vertical wind load
# W_out_parallel = Parallel wind load
# W_in_positive = Positive wind load inside
# W_in_negative = Negative wind load inside
# S_balanced= Balanced snow load
# S_unbalanced= Unbalanced snow load
# E= earthquaque load due to dead load
# according to mabhas6-98(Part 6-2-3-2)
combContainer.ULS.perm.add('ULS01', '1.4*DL + 1.4 * SELF_DL')

combContainer.ULS.perm.add('ULS02a', '1.2 * DL + 1.2 * SELF_DL+.5*s_balanced')
combContainer.ULS.perm.add('ULS02b', '1.2*DL + 1.2 * SELF_DL+.5*s_unbalanced_right')
combContainer.ULS.perm.add('ULS02c', '1.2*DL + 1.2 * SELF_DL+.5*s_unbalanced_left')

combContainer.ULS.perm.add('ULS03a', '1.2*DL + 1.2 * SELF_DL+1.6*s_balanced+0.8*wx_pos+0.8*win_pos')
combContainer.ULS.perm.add('ULS03b', '1.2 * DL + 1.2 * SELF_DL+1.6*s_balanced+0.8*wx_pos+0.8*win_neg')
# combContainer.ULS.perm.add('ULS03c', '1.2 * DL + 1.2 * SELF_DL+1.6*s_balanced+0.8*wy+0.8*win_pos')
# combContainer.ULS.perm.add('ULS03d', '1.2 * DL + 1.2 * SELF_DL+1.6*s_balanced+0.8*wy+0.8*win_neg')
combContainer.ULS.perm.add('ULS03e', '1.2 * DL + 1.2 * SELF_DL+1.6*s_unbalanced_right+0.8*wx_pos+0.8*win_pos')
combContainer.ULS.perm.add('ULS03f', '1.2 * DL + 1.2 * SELF_DL+1.6*s_unbalanced_right+0.8*wx_pos+0.8*win_neg')
combContainer.ULS.perm.add('ULS03g', '1.2 * DL + 1.2 * SELF_DL+1.6*s_unbalanced_left+0.8*wx_neg+0.8*win_pos')
combContainer.ULS.perm.add('ULS03h', '1.2 * DL + 1.2 * SELF_DL+1.6*s_unbalanced_left+0.8*wx_neg+0.8*win_neg')

combContainer.ULS.perm.add('ULS04a', '1.2 * DL + 1.2 * SELF_DL+.5*s_balanced+1.6*wx_pos+1.6*win_pos')
combContainer.ULS.perm.add('ULS04b', '1.2 * DL + 1.2 * SELF_DL+.5*s_balanced+1.6*wx_pos+1.6*win_neg')
# combContainer.ULS.perm.add('ULS04c', '1.2 * DL + 1.2 * SELF_DL+.5*s_balanced+1.6*wy+1.6*win_pos')
# combContainer.ULS.perm.add('ULS04d', '1.2 * DL + 1.2 * SELF_DL+.5*s_balanced+1.6*wy+1.6*win_neg')
combContainer.ULS.perm.add('ULS04e', '1.2 * DL + 1.2 * SELF_DL+.5*s_unbalanced_right+1.6*wx_pos+1.6*win_pos')
combContainer.ULS.perm.add('ULS04f', '1.2 * DL + 1.2 * SELF_DL+.5*s_unbalanced_right+1.6*wx_pos+1.6*win_neg')
combContainer.ULS.perm.add('ULS04g', '1.2 * DL + 1.2 * SELF_DL+.5*s_unbalanced_left+1.6*wx_neg+1.6*win_pos')
combContainer.ULS.perm.add('ULS04h', '1.2 * DL + 1.2 * SELF_DL+.5*s_unbalanced_left+1.6*wx_neg+1.6*win_neg')

combContainer.ULS.perm.add('ULS05a', '0.9 * DL + .9 * SELF_DL+1.6*wx_pos+1.6*win_neg')
combContainer.ULS.perm.add('ULS05b', '0.9 * DL + .9 * SELF_DL+1.6*wx_neg+1.6*win_neg')
# combContainer.ULS.perm.add('ULS05c', '0.9 * DL + .9 * SELF_DL+1.6*wy+1.6*win_neg')

# Dump combination definition into XC.
combContainer.dumpCombinations(preprocessor)




