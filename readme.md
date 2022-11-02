DXF(2D) GeoServer 배포 자동화

FOSS4G KR 2022 ('22.11. 3 ~ 4 , 킨텍스 )

기술 워크샾 session 2 15:00 ~ 17:00 전종수

[2022.11.03 까지만 사용 가능]
https://drive.google.com/drive/folders/1BIXVoG6vlnGGg_KsAifsUrBAqTHHVHjF?usp=sharing

----------------- DOWNLOAD LINK -------------------------------
QGIS Desktop 실행환경
    QGIS https://qgis.org/ko/site/forusers/download.html
    OSGEO4W : https://trac.osgeo.org/osgeo4w/


GeoServer : https://geoserver.org/release/stable/
    CSS Extensions : https://sourceforge.net/projects/geoserver/files/GeoServer/2.21.2/extensions/geoserver-2.21.2-css-plugin.zip/download
주의) GeoServer 버젼과 CSS Extention 버젼 일치


GeoServer 지원 JDK
jdk 1.8 : https://github.com/ojdkbuild/ojdkbuild
----------------------------------------------------------------

dxf2wms
     AnotherDXF(QGIA Plugin)
         https://github.com/EZUSoft/AnotherDXF2Shape
     qgis
     osgeoLive, osgeo4w
     conda qgis ( gdal, ogr )
     
     GeoServer
        workspace, dataStore, style, Layer


실행환경 셋팅
   OSGEO4W : C:\OSGeo4W

   osgeorun.bat
      PYTHON, QGIS, GDAL, QT

   GeoServer

샘플 DXF 출처
    국토정보플랫폼-국토정보맵 ( EPSG:5186 )


DXF 2 GPKG ( All layer Point(Text), Line, Poly )


