from geo.Geoserver import Geoserver

geo = Geoserver('http://127.0.0.1:8080/geoserver', username='admin', password='geoserver')

def fnPrintJson(jsonObj) :
    # for item in jsonObj :
    print(jsonObj)

# get geoserver version
version = geo.get_version()
fnPrintJson(version['about'])


# get ststem info
# status = geo.get_status()

# fnPrintJson( status )

# system_status = geo.get_system_status()
# fnPrintJson( system_status )

# get workspace
# workspace = geo.get_workspaces(workspace='workspace_name')

# get default workspace
# dw = geo.get_default_wokspace(workspace='workspace_name')

# get all the workspaces
# workspaces = geo.get_workspaces()
# fnPrintJson( workspaces )


# get datastore
# datastore = geo.get_datastores(store_name='foss4g')

# get all the datastores
# datastores = geo.get_datastores()
# fnPrintJson( datastores )

# get coveragestore
# cs = geo.get_coveragestore(coveragestore_name='cs')

# get all the coveragestores
# css = geo.get_coveragestores()

# get layer
# layer = geo.get_layer(layer_name='layer_name')

# get all the layers
# layers = geo.get_layers()
# fnPrintJson( layers )

# get layergroup
# layergroup = geo.get_layergroup('layergroup_name')

# get all the layers
# layergroups = geo.get_layergroups()

# get style
# style = geo.get_style(style_name='foss4g_dxf_point_style')
# fnPrintJson( style )

# get all the styles
# styles = geo.get_styles()
# fnPrintJson( styles )

# get featuretypes
# featuretypes = geo.get_featuretypes(store_name='store_name')

# get feature attribute
# fa = geo.get_feature_attribute(feature_type_name='ftn', workspace='ws', store_name='sn')

# get feature store
# fs = geo.get_featurestore(store_name='sn', workspace='ws')