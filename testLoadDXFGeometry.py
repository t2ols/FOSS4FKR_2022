from osgeo import gdal
from osgeo import ogr
import os

os.environ['DXF_ENCODING'] = "UTF-8"

driver = ogr.GetDriverByName('DXF')
# datasource = driver.Open('data/Plan(GRS80).dxf', 0)
datasource = driver.Open('sample/kintex1.dxf', 0)
# datasource.setEncoding('CP949')


# list to store layers'names
featsClassList = []

# parsing layers by index
for featsClass_idx in range(datasource.GetLayerCount()):
    featsClass = datasource.GetLayerByIndex(featsClass_idx)
    featsClassList.append(featsClass.GetName())
    print( "idx : {idx} name : {layerName}".format( idx=featsClass_idx, layerName=featsClass.GetName() ) )

# sorting
featsClassList.sort()

# printing
for featsClass in featsClassList:
    print (featsClass )


# layers=datasource.ExecuteSQL( "SELECT DISTINCT Layer FROM entities" )
# layer=datasource.GetLayerByIndex(0)

# for i in range(0, layers.GetFeatureCount()):
#         # layerName = layers.GetFeature(i).GetFieldAsString(0)
#         # whatisthis(layerName)

#         # print( str(return_utf(layerName), 'utf-8') )

#         # layer.SetAttributeFilter( f"Layer='{layerName}'".format(layerName=layerName) )
#         # print ( 'Layer={layerName}|Features={features}'.format(layerName = layerName, features = layer.GetFeatureCount() ) )

#         layer=datasource.GetLayer(layerName)

#         for feature in layer:
#                 feature.SetField('SOMETHING',1)