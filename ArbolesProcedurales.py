import maya.cmds as cmds
import maya.mel as mel
import random
from PySide2 import QtWidgets, QtCore, QtGui
from shiboken2 import wrapInstance
import maya.OpenMayaUI as omui

def tdfx_get_maya_main_window():
    main_window_ptr = omui.MQtUtil_mainWindow()
    return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)

def tdfx_launcher(cls):
    ui = cls
    ui.show()
    return ui

class TdFxProjectSetup(QtWidgets.QWidget):
    def __init__(self):
        super(TdFxProjectSetup, self).__init__(parent=tdfx_get_maya_main_window())
        window_type = QtCore.Qt.Dialog
        self.setWindowFlags(window_type)
        self.setWindowTitle('Arboles Procedurales')
        self.main_layout = QtWidgets.QGridLayout()
        self.main_layout.setSpacing(10)
        
        self.setLayout(self.main_layout)
        
        self.layout1 = QtWidgets.QGridLayout()
        self.labelSemilla = QtWidgets.QLabel("Semilla:", self)
        self.layout1.addWidget(self.labelSemilla, 0, 0)
        self.editSemilla = QtWidgets.QLineEdit("1", self)
        self.layout1.addWidget(self.editSemilla, 0, 1)
        self.checkAleatorio = QtWidgets.QCheckBox("Aleatorio", self)
        self.layout1.addWidget(self.checkAleatorio, 0, 2)
        self.main_layout.addLayout(self.layout1, 0, 0)
        
        self.layout2 = QtWidgets.QGridLayout()
        self.buttonCrear = QtWidgets.QPushButton("Crear", self)
        self.buttonCrear.clicked.connect(self.crear)
        self.layout2.addWidget(self.buttonCrear, 0, 0)
        self.buttonBorrar = QtWidgets.QPushButton("Borrar", self)
        self.buttonBorrar.clicked.connect(self.borrar)
        self.layout2.addWidget(self.buttonBorrar, 0, 1)
        self.main_layout.addLayout(self.layout2, 1, 0)
        
        self.setGeometry(200, 200, 400, 160)
    
    def crear(self):
        valorSemilla = 0
        if (self.checkAleatorio.checkState()):
            valorSemilla = random.randint(1,1000000)
        else:
            valorSemilla = self.editSemilla.text()
        semilla1 = int(valorSemilla)
        arbol1 = Arbol(semilla1)
        arbol1.crearArbol()
        print("Semilla: " + str(valorSemilla))
    
    def borrar(self):
        cmds.delete()

class Arbol():

    ruta = "C:/Users/edu_e/Desktop/Pipeline/ProyectoFinal Eduardo Delgado Soler/Texturas/"
    nombreDifuso = "TexturesCom_PineBark2_1024_albedo.tif"
    nombreRoughness = "TexturesCom_PineBark2_1024_roughness.tif"
    nombreNormal = "TexturesCom_PineBark2_1024_normal.tif"
    nombreDisplacement = "TexturesCom_PineBark2_1024_height.tif"
    hojaDifuso = "green_leaves_PNG3665.png"

    def __init__(self, semilla):
        self.semilla = semilla
        self.profundidadMax = 5
        self.nuevasRamasMax = 11
        self.curvasArbol = []
        self.grupoCurvasArbol = None
        self.geometriaArbol = []
        self.grupoGeometriasArbol = None
        self.bordePlano = None
        self.hoja = None
        self.hojas = []
        self.grupoHojas = None
        self.arbolCompleto = None

    def crearCurvas(self, posicionInicio, vectorInicio, magnitudVariacion, profundidadActual, ramaPadre, alturaCurva):
        estaRama = Rama(ramaPadre)
        valorInterpolado = 1.0
        if (ramaPadre!=None):
            valorInterpolado = self.linearMapping(2.0 - alturaCurva, 0.0, 2.0, 0.1, ramaPadre.escalaBase)
        else:
            valorInterpolado = random.uniform(0.8, 1.2)
        estaRama.escalaBase = valorInterpolado
        
        if (estaRama.escalaBase>0.2):
            posicionActual = posicionInicio
            vectorActual = vectorInicio
            cantidadPuntos = random.randint(4, 10)
            puntos = []
            variacionX = 0
            variacionY = 0
            variacionZ = 0
            empujeVertical = random.uniform(0, 0.1)
            for punto in range(0, cantidadPuntos):
                puntos.append(posicionActual)
                posicionActual = [posicionActual[0] + vectorActual[0] + variacionX, 
                                  posicionActual[1] + vectorActual[1] + variacionY + empujeVertical, 
                                  posicionActual[2] + vectorActual[2] + variacionZ]
                variacionX = random.uniform(-magnitudVariacion, magnitudVariacion)
                variacionY = random.uniform(-magnitudVariacion, magnitudVariacion)
                variacionZ = random.uniform(-magnitudVariacion, magnitudVariacion)
                empujeVertical = empujeVertical * random.uniform(1, 2)
    
            estaCurva = cmds.curve(point=puntos, n="curvaArbol")
            self.curvasArbol.append(estaCurva)
            
            posicionCurva = cmds.pointOnCurve(estaCurva, pr=0, p=True)
            cmds.select(clear=True)
            cmds.select(self.bordePlano, r=True)
            cmds.move(posicionCurva[0], posicionCurva[1], posicionCurva[2])
            escalaActual = estaRama.escalaBase
            cmds.scale(escalaActual, escalaActual, escalaActual)
            superficieNurb = cmds.extrude(self.bordePlano, estaCurva, ch=True, rn=False, po=0, et=2, ucp=1, fpt=1, upn=1, rotation=0, scale=0, rsp=1)[0]
            cmds.DeleteHistory()
            tangenteY = cmds.pointOnCurve(estaCurva, pr=0, nt=True)[1]
            geometriaActual = cmds.nurbsToPoly(superficieNurb, mnd=1, ch=1, f=2, pt=1, pc=200, chr=0.9, ft=0.01, mel=0.001, d=0.1, ut=3, un=1, vt=3, vn=6, uch=0, ucr=0, cht=0.2, es=0, ntr=0, mrt=0, uss=1)[0]
            if (tangenteY < 0):
                cmds.polyNormal(geometriaActual, normalMode=0, userNormalMode=1, ch=1)
            self.geometriaArbol.append(geometriaActual)
            cmds.DeleteHistory()
            cmds.delete(superficieNurb)
            cmds.select(clear=True)
            cmds.select(geometriaActual, r=True)
            cmds.displaySmoothness(divisionsU=3, divisionsV=3, pointsWire=16, pointsShaded=4, polygonObject=3)
            
            if (profundidadActual<self.profundidadMax):
                cantidadNuevasRamas = random.randint(0, self.nuevasRamasMax)
                for numeroNuevaRama in range(0, cantidadNuevasRamas):
                    if (random.randint(0, self.profundidadMax-profundidadActual)):
                        altura = random.uniform(0.5, 2.0)
                        nuevaPosicion = cmds.pointOnCurve(estaCurva, pr=altura, p=True)
                        nuevoVector = cmds.pointOnCurve(estaCurva, pr=altura, nt=True)
                        if (nuevaPosicion!=[0.0,0.0,0.0]):
                            self.crearCurvas(nuevaPosicion, nuevoVector, random.uniform(0, 2), profundidadActual+1, estaRama, altura)
            
            cantidadHojas = random.randint(30, 60)
            for nuevaHoja in range(0, cantidadHojas):
                altura = random.uniform(2.0, 5.0)
                nuevaPosicion = cmds.pointOnCurve(estaCurva, pr=altura, p=True)
                if (nuevaPosicion!=[0.0,0.0,0.0]):
                    cmds.select(clear=True)
                    cmds.select(self.hoja, r=True)
                    self.hojas.append(cmds.duplicate(self.hoja)[0])
                    cmds.move(nuevaPosicion[0], nuevaPosicion[1], nuevaPosicion[2])
                    cmds.rotate(str(random.randint(0,180))+"deg", str(random.randint(0,180))+"deg", str(random.randint(0,180))+"deg", r=True)
    
    def linearMapping(self, value, leftMin, leftMax, rightMin, rightMax):
        leftSpan = leftMax - leftMin
        rightSpan = rightMax - rightMin

        valueScaled = float(value - leftMin) / float(leftSpan)

        return rightMin + (valueScaled * rightSpan)

    def crearProfile(self):
        plano = cmds.polyPlane(w=1, h=1, sx=1, sy=1 ,ax=[0,1,0], cuv=2, ch=1)[0]
        cmds.select(clear=True)
        mel.eval("select -r " + str(plano) + ".e[0:3]")
        self.bordePlano = cmds.polyToCurve(form=2, degree=1, conformToSmoothMeshPreview=1)[0]
        cmds.DeleteHistory()
        cmds.delete(plano)

    def crearArbol(self):
        random.seed(self.semilla)
        posicion = (0,0,0)
        vector = (0,2,0)
        variacion = random.uniform(0, 1)
        
        self.crearProfile()
        self.crearHoja()
        self.crearCurvas(posicion, vector, variacion, 0, None, 0.0)
        cmds.select(clear=True)
        self.grupoCurvasArbol = cmds.group(self.curvasArbol, n="grupoCurvasArbol")
        cmds.select(clear=True)
        self.grupoGeometriasArbol = cmds.group(self.geometriaArbol, n="grupoGeometriasArbol")
        cmds.delete(self.grupoCurvasArbol)
        cmds.delete(self.bordePlano)
        self.crearMaterial()
        self.grupoHojas = cmds.group(self.hojas, n="grupoHojas")
        arbolFinal = [self.grupoGeometriasArbol, self.grupoHojas]
        self.arbolCompleto = cmds.group(arbolFinal, n="grupoArbolCompleto")
        cmds.delete(self.hoja)
        cmds.select(clear=True)
        cmds.select(self.arbolCompleto)
    
    def crearHoja(self):
        self.hoja = cmds.polyPlane(w=1, h=1, sx=1, sy=1 ,ax=[0,1,0], cuv=2, ch=1)[0]
        cmds.move(0,0, -0.5)
        cmds.move(0, 0, 0, self.hoja+".scalePivot", self.hoja+".rotatePivot", absolute=True)
        cmds.scale(0.5, 0.5, 0.5)
        cmds.makeIdentity(apply=True, t=1, r=1, s=1, n=0, pn=1)
        materialHoja = cmds.createNode("lambert")
        fileDifuso = cmds.shadingNode("file", asTexture=True)
        cmds.setAttr('%s.fileTextureName' %fileDifuso, Arbol.ruta + Arbol.hojaDifuso, type="string")
        shading_group = cmds.sets(renderable=True, noSurfaceShader=True, empty=True)
        cmds.connectAttr('%s.outColor' %materialHoja,'%s.surfaceShader' %shading_group)
        cmds.connectAttr('%s.outColor' %fileDifuso, '%s.color' %materialHoja)
        cmds.connectAttr('%s.outColor' %fileDifuso, '%s.transparency' %materialHoja)
        cmds.select(clear=True)
        cmds.select(self.hoja, r=True)
        cmds.hyperShade(assign=materialHoja)
    
    def crearMaterial(self):
        shader=cmds.shadingNode("aiStandardSurface", asShader=True)
        fileDifuso = cmds.shadingNode("file", asTexture=True)
        cmds.setAttr('%s.fileTextureName' %fileDifuso, Arbol.ruta + Arbol.nombreDifuso, type="string")
        shading_group = cmds.sets(renderable=True, noSurfaceShader=True, empty=True)
        cmds.connectAttr('%s.outColor' %shader,'%s.surfaceShader' %shading_group)
        cmds.connectAttr('%s.outColor' %fileDifuso, '%s.baseColor' %shader)
        fileRoughness = cmds.shadingNode("file", asTexture=True)
        cmds.setAttr('%s.fileTextureName' %fileRoughness, Arbol.ruta + Arbol.nombreRoughness, type="string")
        cmds.connectAttr('%s.outAlpha' %fileRoughness, '%s.specularRoughness' %shader)
        fileNormal = cmds.shadingNode("file", asTexture=True)
        cmds.setAttr('%s.fileTextureName' %fileNormal, Arbol.ruta + Arbol.nombreNormal, type="string")
        bump2d = cmds.shadingNode("bump2d", asTexture=True)
        cmds.connectAttr('%s.outNormal' %bump2d, '%s.normalCamera' %shader)
        cmds.connectAttr('%s.outAlpha' %fileNormal, '%s.bumpValue' %bump2d)
        fileDisplacement = cmds.shadingNode("file", asTexture=True)
        cmds.setAttr('%s.fileTextureName' %fileDisplacement, Arbol.ruta + Arbol.nombreDisplacement, type="string")
        displacementShader = cmds.shadingNode("displacementShader", asTexture=True)
        cmds.setAttr('%s.scale' %displacementShader, 0.05)
        cmds.connectAttr('%s.outAlpha' %fileDisplacement, '%s.displacement' %displacementShader)
        cmds.connectAttr('%s.displacement' %displacementShader, '%s.displacementShader' %shading_group)
        cmds.select(clear=True)
        cmds.select(self.geometriaArbol, r=True)
        cmds.hyperShade(assign=shader)

class Rama():
    def __init__(self, ramaPadre):
        self.ramaPadre = ramaPadre
        self.escalaBase = 1.0

ventana = TdFxProjectSetup()
tdfx_launcher(ventana)
