import requests
import json
from urllib.parse import urljoin

# Thanks
# https://gist.github.com/jgomo3/73f38cc5a91d85146ccf
#

api_entry = 'http://localhost:8080/geoserver/rest/'
credential = ('admin', 'geoserver')
# credential = ('user1', 'user1')

def addNewWorkspace (workspaceName) :
    resource = 'workspaces'
    payload = {'workspace': {'name':workspaceName}}
    headers = {'content-type': 'application/json'}

    request_url = urljoin(api_entry, resource)

    r = requests.post(
        request_url,
        data=json.dumps(payload),
        headers=headers,
        auth=credential
    )

    r.raise_for_status()

def getWorkspace(workspaceName) :
    resource = 'workspaces/{}'.format(workspaceName)
    headers = {'Accept' : 'application/json'}

    request_url = urljoin(api_entry, resource)

    r = requests.get(
        request_url,
        headers=headers,
        auth=credential
    )

    print(r.json)

def newStoreGPKG(workspaceName, storeName, uploadFilePath) :
    #storeName의 gpkg 파일이 생성 됨
    #GeoServer data 디렉토리

    #URL 형식 중요~~~!!!! file.gpkg
    resource = 'workspaces/{workspaceName}/datastores/{storeName}/file.gpkg'.format(workspaceName=workspaceName, storeName=storeName)
    
    # headers = {'content-type': 'application/zip'}
    headers = {'content-type': 'application/x-sqlite3'}

    request_url = urljoin(api_entry, resource)
    try:
        with open(uploadFilePath, 'rb') as f:       
            r = requests.put(
                request_url,
                data=f,
                headers=headers,
                auth=credential
            )

        print(r.status_code)
        print(r.content)

    except Exception as e:
        print(e)
        return "Error: {}".format(e)
    

def newStoreGeoTiff(workspaceName, storeName, filePath, ext) :
    resource = 'workspaces/{workspaceName}/coveragestores/{storeName}/file.{ext}'.format(workspaceName=workspaceName, storeName=storeName,ext=ext)
    file_name = filePath
    # headers = {'content-type': 'application/zip'}
    headers = {'content-type': 'application/geotiff'}

    request_url = urljoin(api_entry, resource)

    with open(file_name, 'rb') as f:
        r = requests.put(
            request_url,
            data=f,
            headers=headers,
            auth=credential
        )

    print(r.content)


def getStore(workspaceName, storeName) :
    resource = 'workspaces/{workspaceName}/datastores/{storeName}.json'.format(workspaceName=workspaceName, storeName=storeName)
    headers = {'content-type': 'application/json'}
    request_url = urljoin(api_entry, resource)

    r = requests.get(
        request_url,
        headers=headers,
        auth=credential
    )

    print(r.json())


def createLayerFontStyle(workspaceName, styleName) :
        
    styleTxt ="""* {
  mark: symbol(circle);
  mark-size: 0.1px;
  label: [Text];
  font-fill: [color];
  font-family: [font];
  font-size: [size * 3];
  font-weight: bold;
  label-anchor: 0.5 0;
  label-offset: 0 25;
  label-rotation: [angle];
  :mark {
    fill: red;
  }
}"""

    resource = 'workspace/{workspaceName}/styles/{styleName}'.format(workspaceName=workspaceName, styleName=styleName)    
    headers = {'conten-type': 'application/vnd.geoserver.geocss+css'}

    request_url = urljoin(api_entry, resource)

    print( "aaaa")

    try:
        r = requests.put(
            request_url,
            data=styleTxt,
            headers=headers,
            auth=credential
        )
        
        print(r.status_code)

        if r.status_code not in [200, 201]:
            return "{}: Data can not be published! {}".format(
                r.status_code, r.content
            )

    except Exception as e:        
        print(e)
        return "Error: {}".format(e)

    # with open(file_name, 'rb') as f:

    print( r )

def getStylesInWorkspace(workspaceName) :
    resource = 'workspaces/{workspaceName}/styles'.format(workspaceName=workspaceName )
    headers = {'content-type': 'application/json'}
    request_url = urljoin(api_entry, resource)

    r = requests.get(
        request_url,
        headers=headers,
        auth=credential
    )

    print(r.content)

def getStyle(workspaceName, styleName) :
    resource = 'workspaces/{workspaceName}/styles/{styleName}.json'.format(workspaceName=workspaceName, styleName=styleName)
    headers = {'content-type': 'application/json'}
    request_url = urljoin(api_entry, resource)

    r = requests.get(
        request_url,
        headers=headers,
        auth=credential
    )

    print(r.content)

def getLayer(workspaceName, layerName) :
    resource = 'workspaces/{workspaceName}/layers/{layerName}.xml'.format(
        workspaceName=workspaceName, 
        layerName=layerName)

    headers = {'content-type': 'application/json'}

    request_url = urljoin(api_entry, resource)

    try:
        r = requests.get(
            request_url,
            headers=headers,
            auth=credential
        )

        if r.status_code not in [200, 201]:
            return "{}: can not get layer! {}".format(
                r.status_code, r.content
            )

        print(r.content)

    except Exception as e:
        return "Error: {}".format(e)



def layer_publish(workspaceName, datastoreName, epsg, layerName):
    # print ("Publishing Layer. wait..")
    # url = "http://localhost:8080/geoserver/rest/workspaces/foss4g/datastores/80_gpkg/featuretypes"
          #  http://localhost:8080/geoserver/rest/workspaces/foss4g/datastores/80_gpkg/featureTypes
    resource = "workspaces/{workspaceName}/datastores/{datastoreName}/featuretypes".format(
        workspaceName=workspaceName, datastoreName=datastoreName
    )

    request_url = urljoin(api_entry, resource)

    layer_xml ="""
            <featureType>
             <name>{layerName}</name>
             <srs>EPSG:{epsg}</srs>
             <projectionPolicy>FORCE_DECLARED</projectionPolicy>
             <enabled>true</enabled>
             <resource class='featureType'>
                 <name>{layerName}</name>
             </resource>
            </featureType>""".format(layerName=layerName, epsg=epsg)

    headers = {'Content-Type': 'text/xml'} 

    try:
        r = requests.post(
            request_url,
            data=layer_xml,
            auth=credential,
            headers=headers,
        )

        if r.status_code not in [200, 201]:
            print ("{}: Data can not be published! {}".format(
                r.status_code, r.content
            ))
            return

        print(r.content)

    except Exception as e:
        print("Error: {}".format(e))
        return "Error: {}".format(e)


def updateLayerStyle(workspaceName, layerName, styleName) : 
    resource = "workspaces/{workspaceName}/layers/{layerName}".format(
        workspaceName=workspaceName, layerName=layerName
    )

    request_url = urljoin(api_entry, resource)

    layer_xml ="""
            <layer>
             <defaultStyle>
             <name>{workspaceName}:{styleName}</name>
             </defaultStyle>
            </layer>""".format(workspaceName=workspaceName, styleName=styleName)

    headers = {'Content-Type': 'text/xml'} 

    try:
        r = requests.put(
            request_url,
            data=layer_xml,
            auth=credential,
            headers=headers,
        )

        if r.status_code not in [200, 201]:
            print ("{}: Data can not be update style! {}".format(
                r.status_code, r.content
            ))
            return

        print(r.content)

    except Exception as e:
        print("Error: {}".format(e))
        return "Error: {}".format(e)


def createLayerGroup(workspaceName, layerGroupName, layerNamePrefix) : 
    resource = "workspaces/{workspaceName}/layergroups".format(
        workspaceName=workspaceName, layerGroupName=layerGroupName
    )

    request_url = urljoin(api_entry, resource)
    layer_xml ="""
<layerGroup>
   <name>{layerGroupName}</name>
   <mode>SINGLE</mode>
   <title>{layerGroupName}</title>
   <workspace>
      <name>{workspaceName}</name>
   </workspace>
   <layers>
      <layer>
         <name>{workspaceName}:{layerNamePrefix}L</name>
      </layer>
      <layer>
         <name>{workspaceName}:{layerNamePrefix}ML</name>
      </layer>
      <layer>
         <name>{workspaceName}:{layerNamePrefix}P</name>
      </layer>
   </layers>
</layerGroup>
""".format(workspaceName=workspaceName, layerGroupName=layerGroupName, layerNamePrefix=layerNamePrefix)

    print( layer_xml )

    headers = {'Content-Type': 'text/xml'} 

    try:

        r = requests.post(
            request_url,
            data=layer_xml,
            auth=credential,
            headers=headers,
        )

        if r.status_code not in [200, 201]:
            print ("{}: Data can not create Layer Group ! {}".format(
                r.status_code, r.content
            ))

            print (r.status_code, r.content ) 
            return

        print("complete")
        print(r.content)

    except Exception as e:
        # print("Error: {}".format(e))
        return "Error: {}".format(e)






#신규 작업공간 생성
# - # addNewWorkspace('foss4g2')

#작업공간 조회
# - # getWorkspace('foss4g2')


#저장소 생성
#(workspaceName, storeName, uploadFilePath, serverFilename)
#data dir
#store dir
#newStoreGPKG('foss4g_pre', 'foss4g2_kin3', r'data/output/4097f6ad-2322-47a0-b335-d649e4e8022d.gpkg')

# - #newStoreGeoTiff('foss4g_pre', 'test2', r'data/test2.tif', 'geotiff')

#getStore('foss4g_pre', 'foss4g2_kin3')

# - #createLayerFontStyle('foss4g_pre', 'kin1_text_font_style')


# 작업공간의 스타일 목록 조회
# getStylesInWorkspace('foss4g_pre')

# 스타일 정의 조회
# getStyle('foss4g_pre', 'kin_text_css')



# - # getLayer('foss4g_pre', '57953d87-8f21-4ac9-9585-214ae11ca339eP')

#저장소에서 레이어 생성 하기
# - #newLayer('foss4g_pre', 'foss4g2_kin3', '4097f6ad-2322-47a0-b335-d649e4e8022dL', 'test1')

#저장소 내 레이어 발행
#레이어 이름 오타 주의
#ML 레이어 발행
#layer_publish('foss4g_pre', 'foss4g2_kin3', '5186', '4097f6ad-2322-47a0-b335-d649e4e8022deL')
#layer_publish('foss4g_pre', 'foss4g2_kin3', '5186', '4097f6ad-2322-47a0-b335-d649e4e8022deML')
#작업공간 레이어 스타일 적용 (선)
#updateLayerStyle('foss4g_pre', '4097f6ad-2322-47a0-b335-d649e4e8022deL', 'kin_ml_css')
# updateLayerStyle('foss4g_pre', '4097f6ad-2322-47a0-b335-d649e4e8022deML', 'kin_ml_css')

#문자 레이어 발행
#layer_publish('foss4g_pre', 'foss4g2_kin3', '5186', '4097f6ad-2322-47a0-b335-d649e4e8022deP')
#작업공간 레이어 스타일 적용 (점, 문자)
#updateLayerStyle('foss4g_pre', '4097f6ad-2322-47a0-b335-d649e4e8022deP', 'kin_text_css')

#발행한 레이어 이름 사용
# createLayerGroup(workspaceName, layerGroupName, layerNamePrefix)
createLayerGroup('foss4g_pre', 'layergrp2', '4097f6ad-2322-47a0-b335-d649e4e8022de' )
