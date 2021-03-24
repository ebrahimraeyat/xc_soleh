# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function

from import_export import dxf_reader
from import_export import neutral_mesh_description as nmd

import sys

layerNamesToImport= ['xc_*']

inputFileName= sys.argv[1]
outputFileName= sys.argv[2]

def getRelativeCoo(pt):
    return [pt[0],pt[1],pt[2]] #No modification.

# There are some misplaced diagonals threshold= 0.05 is NEEDED.
dxfImport= dxf_reader.DXFImport(inputFileName, layerNamesToImport,getRelativeCoo, importLines= True, polylinesAsSurfaces= False, threshold= 0.05, tolerance= .001)

#Block topology
blocks= dxfImport.exportBlockTopology('test')

fileName= 'xc_model_blocks'
ieData= nmd.XCImportExportData()
ieData.outputFileName= outputFileName
ieData.problemName= 'FEcase'
ieData.blockData= blocks

ieData.writeToXCFile()
