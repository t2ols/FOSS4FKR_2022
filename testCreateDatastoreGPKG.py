from geo.Geoserver import Geoserver

geo = Geoserver('http://127.0.0.1:8080/geoserver', username='admin', password='geoserver')

gpkgFilePath = "sample/test.gpkg"
#(Name, path, workspace(opt), overwrite(opt))

result = geo.create_datastore('pyTestDS5', gpkgFilePath, 'testPY', False)

print( result )
