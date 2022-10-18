import sys
import os
import uuid
from shutil import copyfile, move
from osgeo import ogr

from qgis.core import QgsApplication, QgsProject, QgsProcessingFeedback, QgsVectorLayer, QgsVectorFileWriter,QgsSymbol,QgsSingleSymbolRenderer, QgsSymbolLayerRegistry, QgsRuleBasedRenderer, QgsCoordinateTransform, QgsCoordinateTransformContext

from clsDXFTools import ProjDaten4Dat, ifAscii, tr, attTableEdit,  DecodeDXFUTF

qgs = QgsApplication([], False)
qgs.initQgis()

sys.path.append('C:/OSGeo4W/apps/qgis/python/plugins')
import processing
from processing.core.Processing import Processing

listDXFDatNam = './data/sample2.dxf'
outputDir = './output/'
_epsg = '5186'

out="GPKG"
projectOrgName = ""
projectTranceName = ""
gpkgdat = ""

##############################################
myqtVersion = 5
bZielSave = True
sOutForm ='GPKG'
sCharSet = 'euc-kr'
# sCharSet = 'utf-8'
delZielDat=[]

bFormatText = False
bUseColor4Point = True
bUseColor4Line = True
bUseColor4Poly = True
dblFaktor = 1.3 
bGen3D = False
################################################


_tmpFileNames = []

def EditQML (datname):
    with open(datname, 'r') as file :
      filedata = file.read()

    filedata = filedata.replace('labelsEnabled="0"', 'labelsEnabled="1"')

    with open(datname, 'w') as file:
      file.write(filedata)


def labelingDXF (qLayer, bFormatText, bUseColor4Point, dblFaktor):       
    qLayer.setCustomProperty("labeling","pal")
    qLayer.setCustomProperty("labeling/displayAll","true")
    qLayer.setCustomProperty("labeling/enabled","true")
    if bFormatText:
        qLayer.setCustomProperty("labeling/fieldName","plaintext")
        qLayer.setCustomProperty("labeling/dataDefined/Underline","1~~1~~\"underline\"~~")
        qLayer.setCustomProperty("labeling/dataDefined/Bold","1~~1~~\"bold\"~~")  
        qLayer.setCustomProperty("labeling/dataDefined/Italic","1~~1~~\"italic\"~~")           
    else:
        qLayer.setCustomProperty("labeling/fieldName","Text")
    
    if bUseColor4Point:
        qLayer.setCustomProperty("labeling/dataDefined/Color","1~~1~~\"color\"~~")   

    sf = "%.1f" % dblFaktor
    sf = "1~~1~~" + sf + " * \"size\"~~"

    qLayer.setCustomProperty("labeling/dataDefined/Size",sf) 
    qLayer.setCustomProperty("labeling/dataDefined/Family","1~~1~~\"font\"~~")   
    qLayer.setCustomProperty("labeling/fontSizeInMapUnits","True")
    
    qLayer.setCustomProperty("labeling/fontSizeUnit","MapUnit") 
    qLayer.setCustomProperty("labeling/dataDefined/Rotation","1~~1~~\"angle\"~~")
    qLayer.setCustomProperty("labeling/dataDefined/OffsetQuad", "1~~1~~\"anchor\"~~")

    qLayer.setCustomProperty("labeling/obstacle","false")
    qLayer.setCustomProperty("labeling/placement","1")
    qLayer.setCustomProperty("labeling/placementFlags","0")

    qLayer.setCustomProperty("labeling/textTransp","0")
    qLayer.setCustomProperty("labeling/upsidedownLabels","2")
    qLayer.removeCustomProperty("labeling/ddProperties")


def convertDXFtoGPKG(listDXFDatNam, outputDir, epsg) :

    geomList =("eP:POINT:LIKE \'%POINT%\'",
            "eL:LINESTRING:LIKE \'LINESTRING\'",
            "eML:MULTILINESTRING:LIKE \'MULTILINESTRING\'",
            "eF:POLYGON:LIKE \'%POLYGON%\'"
            # ,"cP:POINT:= 'GEOMETRYCOLLECTION'",
            # "cL:LINESTRING:= 'GEOMETRYCOLLECTION'",
            # "cF:POLYGON:= 'GEOMETRYCOLLECTION'"
            )

    cmdOpt = " --config DXF_TRANSLATE_ESCAPE_SEQUENCES FALSE --config DXF_MERGE_BLOCK_GEOMETRIES TRUE --config DXF_INLINE_BLOCKS TRUE -dim 2 "
    (dummy,dxfFileName) = os.path.split(listDXFDatNam)
    projectOrgName = dxfFileName[0:-4] #~.dxf
    
    projectTranceName = ProjectName = str(uuid.uuid4())

    gpkgdat=outputDir+"/"+ProjectName+'.gpkg'
    
    outputDirOrDatei=outputDir+"/"+ProjectName
    
    if os.path.exists(gpkgdat):
        print('gpkg exist')
        os.remove(gpkgdat)

    #LineString Geometry Shape
    mLay=QgsVectorLayer('LineString?crs=EPSG:'+ epsg,'' , 'memory')
    # mem0Dat= outputDir+"/"+ProjectName + '.shp'

    # options = QgsVectorFileWriter.SaveVectorOptions()
    # options.driverName = "ESRI Shapefile"
    # Antw=QgsVectorFileWriter.writeAsVectorFormatV2(mLay,mem0Dat, QgsCoordinateTransformContext(), options)

    try:
        Processing.initialize()
        qPrjDatName = ProjectName

        okTransform=False
        root = QgsProject.instance().layerTreeRoot()

        grpProjekt = root.addGroup( ProjectName)
        grpProjekt.setExpanded(True)
            
        Antw = gpkgLayerStyler(mLay.crs(), bZielSave, sOutForm, grpProjekt, geomList, ProjectName, cmdOpt, listDXFDatNam, outputDirOrDatei, qPrjDatName, sCharSet, bFormatText, bUseColor4Point,bUseColor4Line,bUseColor4Poly, dblFaktor, bGen3D, gpkgdat, outputDir)            
        

    except OSError as e:  
        print( "Fehler: %s - %s." % (e.filename,e.strerror)) 
        return False

    return True, ProjectName, projectOrgName, projectTranceName 


def convertDateFormat(ArtDaten):
    sDaten = ""
    sArt = ""
    inDaten = False
    for c in ArtDaten[:-1]:
        if c == '(' and not inDaten:
            inDaten = True
            c = ''
        if inDaten:
            sDaten = sDaten + c
        else:
            sArt = sArt + c
    return sArt, sDaten
    

def csvSplit(csvZeile, trenn=',', tKenn='"', tKennDel = True, bOnlyFirst = False):    
    inString = False
    mask = ""
    s = ''
    sb = False
    for c in csvZeile: 
        if c == tKenn and not sb:
            inString = not inString
        if c == trenn and inString  and not sb:
            if mask == "":
                mask = "$$"
                while mask in csvZeile:
                    mask = mask + '$'
            s=s+mask
        else:
            if not (tKennDel and (not sb) and c == tKenn): 
                s=s+c
        if c == "\\":
            sb = True
        else:
            sb = False
            
    arr = s.split(trenn)
    if mask != "":
        for i in range(0,len(arr)):
            arr[i] = arr[i].replace(mask,trenn)
    if bOnlyFirst and len(arr)>2:
        arr=[arr[0],trenn.join(arr[1:])]
    return arr


def fnctxtOGRtoQGIS(cArt):
    if cArt == 1:
        return 2
    if cArt == 2:
        return 1
    if cArt == 3:
        return 0
    if cArt == 4:
        return 5
    if cArt == 5:
        return 4
    if cArt == 6:
        return 3
    if cArt == 7:
        return 8
    if cArt == 8:
        return 7 
    if cArt == 9:
        return 6 
    if cArt == 10:
        return 2 
    if cArt == 11:
        return 1 
    if cArt == 12:
        return 0  

def sizeTextSplit(zt):
    try:
        z="";t="";f=-1
        isText = False
        for c in zt:
            if not c in "01234567890.-":
                isText=True
            if isText:
                t=t+c
            else:
                z=z+c
        f=float(z)
    except:
        pass
    return f,t  

def splitText (fText,TxtType):
    underline = False
    bs = False
    uText = r""
    ignor = False
    font = ""
    color = ""
    delSemi = False
    inFont = False
    inColor = False
    inHText = False
    aktText=fText
    FlNum = False
    aktSize = None
    
    if TxtType == "TEXT" or TxtType == "UNDEF":
        if "%%u".upper() in aktText.upper():
            underline=True
            aktText = aktText.replace('%%u','').replace('%%U','')
        aktText = aktText.replace('%%c','Ø') 
    
    if TxtType == "MTEXT" or TxtType == "UNDEF":
        aktText=DecodeDXFUTF(aktText)

        for c in aktText:

            if bs and c.upper() == 'H': 
                c=''
                ignor = True
                inHText = True 
                delSemi = True
            if bs and c.upper() == 'O': 
                c=''
                ignor = True
            if bs and c.upper() == 'L': 
                c=''
                underline = True
                ignor = True
            if bs and c == 'S': 
                c=''
                ignor = True
                delSemi = True
                FlNum = True

            if bs and c.upper() == 'F': 
                ignor = True
                inFont = True 
                delSemi = True
            
            if bs and c.upper() == 'C': 
                ignor = True
                inColor = True 
                delSemi = True

            if bs and c.upper() == 'P': 
                ignor = True
                c="\n"  
                
            if c == ';' and delSemi:
                c= ''
                inFont=False
                inColor=False
                inHText=False
                delSemi = False
            
            if not bs and (c == '{' or c == '}'): 
                c = ''
            else:
                ignor = True
            if c == '\\':
                if bs:

                    uText = uText + '\\\\'
                    bs=False
                else:
                    bs = True
            else:
                if not ignor:
                    if bs:
                        uText = uText + '\\'
                if inFont:
                    font = font + c
                else:
                    if inColor:
                        color = color + c
                    else:
                        if inHText:
                            if aktSize is None:
                                aktSize = c
                            else:
                                aktSize = aktSize + c
                        else:
                            uText = uText  + c
                bs = False
            ignor = False
        aktText = uText
    return aktText, underline, font, FlNum, aktSize, color
 
def tryDecode(txt,sCharset):
    if myqtVersion == 5: 
        try:
            return str(bytes(txt,"utf8").decode(sCharset) )
        except:
            return txt
    try:
        re=txt.decode( sCharset) 
        return re
    except:
        return '#decodeerror4#'    

def attTableEdit (sOutForm, inpDat,bFormat,sCharSet,gpkgTable=None):
    # if sCharSet == "System":
    #     sCharSet=locale.getdefaultlocale()[1]

    source = ogr.Open(inpDat, update=True)
    if source is None:
        print( ('ogr: can not open: ') + inpDat)
        return
    

    layer = source.GetLayerByName( gpkgTable )
    if layer is None:
        source.Destroy()
        print(('ogr: layer not found: ') + inpDat + '(' + gpkgTable + ')')
        return
            
    laydef = layer.GetLayerDefn()
    if laydef is None:
        source.Destroy()
        print(('ogr: laydef not found: ') + inpDat)
        return

    Found = False
    for i in range(laydef.GetFieldCount()):
        if laydef.GetFieldDefn(i).GetName() == 'ogr_style':
            Found = True

    if not Found:
        print(("missing field 'ogr_style': ") + inpDat)
        return
    
    layer.CreateField(ogr.FieldDefn('font', ogr.OFTString))
    layer.CreateField(ogr.FieldDefn('angle', ogr.OFTReal))    
    layer.CreateField(ogr.FieldDefn('size', ogr.OFTReal))
    layer.CreateField(ogr.FieldDefn('size_u', ogr.OFTString))
    layer.CreateField(ogr.FieldDefn('anchor', ogr.OFTString))
    layer.CreateField(ogr.FieldDefn('color', ogr.OFTString))
    layer.CreateField(ogr.FieldDefn('underline', ogr.OFTInteger))
    layer.CreateField(ogr.FieldDefn('plaintext', ogr.OFTString))
    layer.CreateField(ogr.FieldDefn('fcolor', ogr.OFTString))
    layer.CreateField(ogr.FieldDefn('flnum', ogr.OFTInteger))
    layer.CreateField(ogr.FieldDefn('bold', ogr.OFTInteger))
    layer.CreateField(ogr.FieldDefn('italic', ogr.OFTInteger))

    i=1
    layer.StartTransaction()
    feature = layer.GetNextFeature()
    while feature:
        try:
            TxtType = "UNDEF"
            SubClass = feature.GetField('SubClasses')
            if SubClass is None:
                if sOutForm=="SHP":
                    print(("missing field 'SubClasses' in: ") + inpDat)
            else:
                if SubClass.find("AcDbMText")>=0:
                    TxtType = "MTEXT" 
                if SubClass.find("AcDbText")>=0:
                    TxtType = "TEXT"
            att=feature.GetField('ogr_style') 
          
            try:
                aktHandle=feature.GetField('EntityHand') 
            except:
                aktHandle=feature.GetField('EntityHandle') 
                
            if att is None:
                print(("missing field 'ogr_style' in: ") + inpDat)            
            elif att[-1] != ')':
                if aktHandle == None:
                    print(("incomplete field 'ogr_style' at EntityHandle: ") )
                else:
                    print(("incomplete field 'ogr_style' at EntityHandle: ") + (aktHandle)) 

            else:
                sArt,sDaten = convertDateFormat(att)
                
                params = csvSplit (sDaten)
                for param in params:
                    arr=csvSplit(param,":",None,None,True)
                    if len(arr) == 2:
                        f = arr[0] 
                        w = arr[1]
                        if f == "c":
                            if w == "#ffffff": w="#f0f0f0"
                            feature.SetField('color', w)
                        if f == "fc":
                            if w == "#000000": w="#f0f0f0"
                            feature.SetField('fcolor', w)
                        if f == "f":
                            feature.SetField('font', w)
                        if f == "a":
                            dWin = float(w)
                            if dWin >=360:
                                dWin = dWin - 360 
                            feature.SetField('angle', dWin)
                        if f == "p":
                            if sArt == "LABEL":
                                feature.SetField('anchor', fnctxtOGRtoQGIS(int(w)))
                        if f == "s":
                            z,t=sizeTextSplit(w)

                            feature.SetField('size', z)
                            feature.SetField('size_u', t)
                        if f == "t":
                            dummy = 1
                    else:
                        print(("incomplete field 'ogr_style': ") + tryDecode(param,sCharSet))
                    
                    if sArt == "LABEL":
                        AktText = feature.GetField('Text')
                        if AktText is None:
                            print(('missing Text: ') + inpDat)
                        else:
                            dummy=AktText
                            AktText="";bDecodeError=False

                            for c in dummy:
                                if ord(c) > 54000:  #where from ord
                                    c="?"; bDecodeError=True
                                AktText=AktText + c
                            if bDecodeError:
                                if aktHandle == None:
                                    print(("Wrong char in  'ogr_style' at EntityHandle: ") +  (" (Check your choose charset)") + tryDecode(dummy,sCharSet)) 
                                else:
                                    print(("Wrong char in  'ogr_style' at EntityHandle: ") + aktHandle + (" (Check your choose charset)") + tryDecode(dummy,sCharSet)) 


                            if bFormat:
                                t,underline,font, FlNum, aktSize, color = splitText(AktText,TxtType)
                                feature.SetField('plaintext', t)
                               
                                if not aktSize is None:
                                    feature.SetField('size', aktSize)
                                

                                if (color != ""):
                                    try:
                                        color=hex(int(color[1:])).replace('0x','#') 

                                        if color == "#ffffff": color="#f0f0f0"                                        
                                        feature.SetField('color',color)
                                    except:
                                        feature.SetField('color','#FEHLER#')
                                


                                if (font != ""):
                                    afont = font.split('|')
                                    for p in afont:
                                        if p[:1] == 'f':
                                            feature.SetField('font', p[1:])
                                        if p[:1] == 'b':
                                            feature.SetField('bold', p[1:])
                                        if p[:1] == 'i':
                                            feature.SetField('italic', p[1:])
                                feature.SetField('underline', underline)
                                feature.SetField('flnum', FlNum)
                            else:
                                feature.SetField('plaintext', AktText)
                                feature.SetField('underline', False)
                layer.SetFeature(feature)
            feature = layer.GetNextFeature()
        except:
            if att is None:
                print ()
            else:
                print ('ogr_style:' + att)
                
            feature = layer.GetNextFeature()
    layer.CommitTransaction()
    source.Destroy()

#From AnotherDXFImport
#Load DXF to QGIS Layer
def gpkgLayerStyler(mLay_crs, bZielSave, sOutForm, grpProjekt,geomList, Kern, cmdOpt, DXFDatNam, outputDirOrDatei, qPrjDatName, sOrgCharSet, bFormatText, bUseColor4Point,bUseColor4Line,bUseColor4Poly, dblFaktor, bGen3D, gpkgdat, outputDir ):
    sCharSet=sOrgCharSet
    myGroups={}
    
    korrDXFDatNam=DXFDatNam
    
    layCnt=0
    
    optGCP = ""
    korrGPKGDatNam=gpkgdat    
     
    for p in geomList:
        layCnt=layCnt+1       
        v = p.split(":")
                
        qmldat =  outputDir + '/'+ Kern + '.qml'
        gpkgTable=Kern+v[0]

        bKonvOK=False

        try:
            
            if sCharSet == "System":
                ogrCharSet=locale.getdefaultlocale()[1]
            else:
                ogrCharSet=sCharSet

            ogrCharSet=ogrCharSet.upper()              

            opt = '-append -update --config DXF_ENCODING "' + ogrCharSet + '" '
            
            opt = opt + '--config DXF_INCLUDE_RAW_CODE_VALUES TRUE '
            opt = opt + ('%s -nlt %s %s -sql "select *, ogr_style from entities where OGR_GEOMETRY %s" -nln "%s"') % (cmdOpt,v[1],optGCP,v[2], gpkgTable)      
            if bGen3D:
                opt = opt + ' -dim 3 '
            
            pList={'INPUT':korrDXFDatNam,'OPTIONS':opt,'OUTPUT': korrGPKGDatNam}

            """
            ogr2ogr -append -update ^
                ".\\output\\sample.gpkg" ".\\data\\sample.dxf" ^
                --config DXF_ENCODING "UTF-8" ^
                --config DXF_INCLUDE_RAW_CODE_VALUES TRUE ^
                --config DXF_TRANSLATE_ESCAPE_SEQUENCES FALSE ^
                --config DXF_MERGE_BLOCK_GEOMETRIES TRUE ^
                --config DXF_INLINE_BLOCKS TRUE -dim 2 ^
                -nlt POINT ^
                -sql "select *, ogr_style from entities where OGR_GEOMETRY LIKE '%POINT%' " ^
                -nln "e986663f-065e-4f25-aaed-d3238a8ca41eeP"
            """

            pAntw=processing.run('gdal:convertformat',pList) 

            if os.path.exists(korrGPKGDatNam):
                bKonvOK = True 
               
        except OSError as e:  
            print( "%s" % e)     
            return False

        if pAntw is None:
            print(("process 'gdalogr:convertformat' could not start please restart QGIS"))
        else:
            if bKonvOK:
                
                attTableEdit(sOutForm,korrGPKGDatNam,bFormatText,sCharSet,gpkgTable)

                sLayer="%s|layername=%s" %(korrGPKGDatNam,gpkgTable) 
                Layer = QgsVectorLayer(sLayer, "entities"+v[0],"ogr") 
                Layer.setCrs(mLay_crs)
                if Layer.featureCount() < 0: Layer=None 

                if Layer:
                    if Layer.featureCount() > 0:
                       
                        fni = Layer.dataProvider().fieldNameIndex('Layer')

                        unique_values = Layer.dataProvider().uniqueValues(fni)
                        zL=0
                        for layerName in unique_values:
                                 
                            layerName = DecodeDXFUTF(layerName)
                            zL=zL+1
                            Layer = QgsVectorLayer(sLayer, layerName+'('+v[0]+')',"ogr") 
                            Layer.setCrs(mLay_crs)

                            Layer.setSubsetString( "Layer = '" + layerName + "'" )

                            if Layer.featureCount() < 0: Layer=None 

                            Layer = QgsProject.instance().addMapLayer(Layer, False) 

                            if layerName not in myGroups:
                                gL = grpProjekt.addGroup( layerName)
                                myGroups[layerName]=gL
                                gL.addLayer(Layer)
                                gL.setExpanded(False)
                            else:
                                myGroups[layerName].addLayer(Layer)
                                
                            if Layer.geometryType() == 0: #Point
                                symbol = QgsSymbol.defaultSymbol(Layer.geometryType())
                                Layer.setRenderer(QgsSingleSymbolRenderer( symbol ) )
                                                                        
                                symbol.setSize( 0.1 )
                                labelingDXF (Layer, bFormatText, bUseColor4Point, dblFaktor)

                                Layer.saveNamedStyle (qmldat)
                                EditQML (qmldat)
                                Layer.loadNamedStyle(qmldat)
                                # Layer.loadNamedStyle('templateStyle.qml')

                            if Layer.geometryType() == 1 and bUseColor4Line: #Line
                                registry = QgsSymbolLayerRegistry()
                                lineMeta = registry.symbolLayerMetadata("SimpleLine")
                                symbol = QgsSymbol.defaultSymbol(Layer.geometryType())
                                renderer = QgsRuleBasedRenderer(symbol)
                                    
                                root_rule = renderer.rootRule()
                                rule = root_rule.children()[0].clone()
                                symbol.deleteSymbolLayer(0)
                                qmap={}
                                qmap["color_dd_active"]="1"
                                qmap["color_dd_expression"]="\"color\""
                                qmap["color_dd_field"]="color"
                                qmap["color_dd_useexpr"]="0"
                                lineLayer = lineMeta.createSymbolLayer(qmap)
                                symbol.appendSymbolLayer(lineLayer)
                                rule.setSymbol(symbol)
                                rule.appendChild(rule) 
                                Layer.setRenderer(renderer)

                            if Layer.geometryType() == 2 and bUseColor4Poly: #Polygon
                                registry = QgsSymbolLayerRegistry()
                                fillMeta = registry.symbolLayerMetadata("SimpleFill")
                                symbol = QgsSymbol.defaultSymbol(Layer.geometryType())
                                renderer = QgsRuleBasedRenderer(symbol)

                                root_rule = renderer.rootRule()
                                rule = root_rule.children()[0].clone()
                                symbol.deleteSymbolLayer(0)
                                qmap={}
                                qmap["color_dd_active"]="1"
                                qmap["color_dd_expression"]="\"fccolor\""
                                qmap["color_dd_field"]="fcolor"
                                qmap["color_dd_useexpr"]="0"
                                lineLayer = fillMeta.createSymbolLayer(qmap)
                                symbol.appendSymbolLayer(lineLayer)
                                rule.setSymbol(symbol)
                                rule.appendChild(rule) 

                                Layer.setRenderer(renderer)
                                Layer.setOpacity(0.5)                        

                        Layer.saveStyleToDatabase(gpkgTable, gpkgTable, True, "")

                    else:
                        Layer=None 
                    
                else:
                    print (("Option '%s' could not be executed")%  opt )
            else:
                print(("Creation '%s' failed. Please look to the QGIS log message panel (OGR)") % korrGPKGDatNam )
    
    return True


def cleanTempFiles(output):
    file_list = os.listdir(output)
    file_list_py = [file for file in file_list if not file.endswith(".gpkg")]
    
    for file in file_list_py :
        try:
            # print(output+file)
            os.remove( output+file ) 
        except Exception:
            pass


if __name__ == "__main__":        
    sys.argv = ['dxf2wms', './sample/kintex1.dxf', './data/output', '5186']

    inputDXF = sys.argv[1]
    outputFolder = sys.argv[2]
    srs_epsg = sys.argv[3]

    try:
       
        # loadDXF(listDXFDatNam, outputDir,_epsg) 
        okYn, _ProjectName, _projectOrgName, _projectTranceName  = convertDXFtoGPKG( inputDXF, outputFolder,srs_epsg) 
        
        if ( okYn ) : 
            # print ( _ProjectName )
            print( "From {projectOrgName}.dxf To {_projectTranceName}.gpkg" )
            print( _projectTranceName )
        else :
            print("{projectOrgName}.dxf Convert Failed")
            # from gpkg2tiffQD import makeTIFF
            # print( outputFolder+_projectTranceName+'.gpkg', outputFolder+_projectTranceName+'.tif' )
            # makeTIFF(outputFolder+_projectTranceName+'.gpkg', outputFolder+_projectTranceName+'.tif', '')

        # yn = makeTiff()
        # if ( yn ) :
        #     makeTiles()

        # cleanTempFiles(sys.argv[2])
    except Exception as e:  
        print( "Fehler: %s - %s." % (e.filename,e.strerror))     
