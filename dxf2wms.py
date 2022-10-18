import sys
import os
import json

def cleanTempFiles(output):
    file_list = os.listdir(output)
    file_list_py = [file for file in file_list if not (file.endswith(".gpkg") or file.endswith(".tiff") or file.endswith(".html") or file.endswith(".xml") )]
    
    for file in file_list_py :
        try:
            print(os.path.join(output,file) )
            os.remove( os.path.join( output, file ) )
        except Exception:
            pass
    
    os.rmdir(output)


def cleanTempDir(distDir) :

    for root, dirs, files in os.walk(distDir, topdown=False):
        print(root, dirs, files)
        for name in files:
            os.remove(os.path.join(root, name))
        for name in dirs:
            os.rmdir(os.path.join(root, name))
    
    os.rmdir(distDir)
         


if __name__ == "__main__":    
    
    # sys.argv = ['dxf2wms', './data/target_87_20220328_original.dxf', './wms_87_20220328', '5186']
    # sys.argv = ['dxf2wms', './data/Plan(GRS80).dxf', './wms_87_20220328', '5186']
    sys.argv = ['dxf2wms', './data/sample.dxf', './data/sample', '5186']

    inputDXF = sys.argv[1]
    outputFolder = sys.argv[2]
    workFolder = outputFolder + "_work"
    srs_epsg = sys.argv[3]

    try: 
        if not os.path.exists(outputFolder): 
            os.makedirs(outputFolder)             
    except OSError:
        pass

    try: 
        if not os.path.exists(workFolder): 
            os.makedirs(workFolder)             
    except OSError:
        pass


    from dxf2gpkg import loadDXF
    
    # loadDXF(listDXFDatNam, ZielPfad,_epsg) 
    # print(f"{inputDXF}, {outputFolder}, {workFolder}, {srs_epsg}")

    # okYn, _ProjektName, _projectOrgName, _projectTranceName  = loadDXF( inputDXF, outputFolder,srs_epsg) 
    okYn, _ProjektName, _projectOrgName, _projectTranceName  = loadDXF( inputDXF, workFolder,srs_epsg) 
    
    if ( okYn ) : 
        # print ( _ProjektName )
        # print( _projectOrgName )
        # print( _projectTranceName )

        # inputGPKG = f"{outputFolder}/{_projectTranceName}.gpkg"
        inputGPKG = f"{workFolder}/{_projectTranceName}.gpkg"
        # print( inputGPKG )
        # outputTiffFile = f"{outputFolder}/{_projectTranceName}.tiff"
        outputTiffFile = f"{workFolder}/{_projectTranceName}.tiff"
        # print(outputTiffFile)

        from gpkg2tiff import gpkg2tiff
        okYn = gpkg2tiff(inputGPKG, outputTiffFile, srs_epsg)

        if ( okYn ) :
            from tiff2tiles import tiff2tiles                
            tiff2tiles(outputTiffFile, outputFolder, srs_epsg)

    #cleanTempFiles(sys.argv[2])

    try: 
        if os.path.exists(workFolder): 
            #print('delete work dir')
            import shutil
            shutil.rmtree(workFolder, ignore_errors=True)          
            #cleanTempDir(workFolder)

    except OSError as err:
        print('del error' + err)

    # except Exception as e:  
    #     print( e )     
