REM 환경 변수 설정 스크립트

REM QGIS Setup
SET OSGEO4W_ROOT=C:\OSGeo4W
SET QGISNAME=qgis
SET QGIS=%OSGEO4W_ROOT%\apps\%QGISNAME%
set QGIS_PREFIX_PATH=%QGIS%

REM Gdal Setup
set GDAL_DATA=%OSGEO4W_ROOT%\share\gdal\
set GDAL_FILENAME_IS_UTF8=YES
set USE_PATH_FOR_GDAL_PYTHON=YES

REM Python Setup
SET PYTHONHOME=%OSGEO4W_ROOT%\apps\Python39
set PYTHONPATH=%QGIS%\python;%PYTHONHOME%

rem Qt Setup Set VSI cache to be used as buffer, see #6448
rem from C:\OSGeo4W\etc\ini\qt5.bat

path %OSGEO4W_ROOT%\bin;%QGIS%\bin;%PYTHONPATH%;%OSGEO4W_ROOT%\apps\qt5\bin;%PATH%

set QT_PLUGIN_PATH=%OSGEO4W_ROOT%\apps\Qt5\plugins

set O4W_QT_PREFIX=%OSGEO4W_ROOT:\=/%/apps/Qt5
set O4W_QT_BINARIES=%OSGEO4W_ROOT:\=/%/apps/Qt5/bin
set O4W_QT_PLUGINS=%OSGEO4W_ROOT:\=/%/apps/Qt5/plugins
set O4W_QT_LIBRARIES=%OSGEO4W_ROOT:\=/%/apps/Qt5/lib
set O4W_QT_TRANSLATIONS=%OSGEO4W_ROOT:\=/%/apps/Qt5/translations
set O4W_QT_HEADERS=%OSGEO4W_ROOT:\=/%/apps/Qt5/include
set O4W_QT_DOC=%OSGEO4W_ROOT:\=/%/apps/Qt5/doc

set VSI_CACHE=TRUE
set VSI_CACHE_SIZE=1000000

REM Launch python job
rem python [[]]].py
