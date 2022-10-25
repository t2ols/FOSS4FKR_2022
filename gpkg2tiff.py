import os
import sys
import json

# sys.path.append('C:/OSGeo4W/apps/qgis/python/plugins')
sys.path.append( f"{os.environ['QGIS_PLUGIN']}" )

from qgis.core import QgsApplication, QgsProcessingFeedback, QgsProject, QgsVectorLayer
import PyQt5.QtCore
import qgis.PyQt.QtCore
from qgis.analysis import QgsNativeAlgorithms

from processing.core.Processing import Processing
import processing

from osgeo import ogr    

def gpkg2tiff(gpkg, outputFile, epsg) :
    feedback = QgsProcessingFeedback()
    QgsApplication.setPrefixPath('', True)
    qgs = QgsApplication([], False)
    qgs.initQgis()

    Processing.initialize()
    QgsApplication.processingRegistry().addProvider(QgsNativeAlgorithms())
    
    gpkg_layers = [l.GetName() for l in ogr.Open(gpkg )]

    tl = []
    allex = None

    for _l in gpkg_layers:
        gpkg_layer = gpkg + "|layername="+_l
        tl.append(gpkg_layer)
        vlayer = QgsVectorLayer(gpkg_layer, _l, "ogr")

        if not vlayer.isValid():
            print("Layer failed to load!")
        else:
            QgsProject.instance().addMapLayer(vlayer)
            ex = vlayer.extent()
            if allex == None :
                allex = ex

            allex.combineExtentWith(ex)

    _extent = f'{allex.xMinimum()}, {allex.xMaximum()}, {allex.yMinimum()}, {allex.yMaximum()} [EPSG:{epsg}]' 

    _param  = { 'EXTENT' : _extent, 'EXTENT_BUFFER' : 256, 'LAYERS' : tl, 'MAKE_BACKGROUND_TRANSPARENT' : True, 'MAP_THEME' : None, 'MAP_UNITS_PER_PIXEL' : 0.1, 'OUTPUT' : outputFile, 'TILE_SIZE' : 20480 }
    processing.run('qgis:rasterize',_param) 

    qgs.exitQgis()

    return True

if __name__ == "__main__":    
    
    sys.argv = ['gpkg2tiff', './data/output/a77bbd12-7ed9-45cd-b862-6610bc894348.gpkg', './data//output/a77bbd12-7ed9-45cd-b862-6610bc894348.tiff', '5186']

    inputGPKG = sys.argv[1]
    outputFile = sys.argv[2]
    srs_epsg = sys.argv[3]

    # (_path, _filaName) = os.path.split(sys.argv[1])
    # tmp_tiff_filename =  os.path.splitext(_filaName)
    
    gpkg2tiff(inputGPKG, outputFile, srs_epsg)

    # try:        
    #     pass
        
    #     if ( okYn ) : 
        
    # except Exception as e:  
    #     print( "Fehler: %s - %s." % (e.filename,e.strerror))     
