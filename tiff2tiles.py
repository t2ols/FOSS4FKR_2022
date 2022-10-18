import os
import sys
import json
# gdal2tilesCommand = f"{os.environ['CONDA_PREFIX']}/Scripts/gdal2tiles.py"
gdal2tilesCommand = f"{os.environ['PYTHONHOME']}/Scripts/gdal2tiles.py"

def tiff2tiles(inputTiff, outputFolder, epsg) :

    tmpEPSG = f"EPSG:{epsg}"
    # _tileParam = { "VIEWER" : 0, "SOURCE_CRS" : tmpEPSG, 'INPUT' : inputTiff, "PROFILE" : 0, "RESAMPLING": 0, "OUTPUT" : outputFolder }
    _tileParam = { "VIEWER" : "all", "SOURCE_CRS" : tmpEPSG, 'INPUT' : inputTiff, "PROFILE" : "mercator", "RESAMPLING": "average", "OUTPUT" : outputFolder }
    
    #--processes=8
    cmd = f"python {gdal2tilesCommand} -s {_tileParam['SOURCE_CRS']} -w {_tileParam['VIEWER']} -r {_tileParam['RESAMPLING']} -p {_tileParam['PROFILE']} {_tileParam['INPUT']} {_tileParam['OUTPUT']}"                
    os.system(cmd)
        
    return True  

if __name__ == "__main__":    
    
    sys.argv = ['tiff2tiles', './data/output/d6a9ec52-2efd-42e8-a402-e912d9e3c6bf.tiff', './data/output/d6a9ec52-2efd-42e8-a402-e912d9e3c6bf', '5186']

    # argv = gdal.GeneralCmdLineProcessor(sys.argv)
    # print(argv)

    inputGPKG = sys.argv[1]
    outputFile = sys.argv[2]
    srs_epsg = sys.argv[3]

    # (_path, _filaName) = os.path.split(sys.argv[1])
    # tmp_tiff_filename =  os.path.splitext(_filaName)
    
    tiff2tiles(inputGPKG, outputFile, srs_epsg)

    # try:        
    #     pass
        
    #     if ( okYn ) : 
        
    # except Exception as e:  
    #     print( "Fehler: %s - %s." % (e.filename,e.strerror))     
