import math
import random
import sys
import time

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar)

import numpy as np
from PyQt5 import uic, QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QSizePolicy, QPushButton, QCheckBox, QButtonGroup, QSpinBox, \
    QLabel, QVBoxLayout, QFileDialog


class Algoritmo:
    def __init__(self, muestras, plot, tolerancia=0.01, peso=2):
        self.plot = plot
        self.centros = []
        self.clases = []
        self.tolerancia = tolerancia
        self.peso = peso
        self.muestras = muestras

    def bayes(self, muestras, clases):

        m = []

        for clase in muestras:
            arr = []
            for i in range(len(clase[0])):
                cont = 0
                for caso in clase:
                    cont = cont + caso[i]
                arr.append(cont / len(clase[0]))
            m.append(arr)

        restas = []
        for clase in muestras:
            c = []
            for muestra in clase:
                arr = []
                for elem in muestra:
                    print("")

    def kmedias(self):
        eps = self.tolerancia + 1
        centrosv = []
        muestrast = []
        # Sacamos los centros semi al azar (1 por clase) y metemos todas las muestras en el mismo array
        for clase in self.muestras:
            self.centros.append(clase[random.randint(0, len(clase) - 1)])
            for elem in clase:
                muestrast.append(elem)

        # Actualizamos centros y clases
        while eps > self.tolerancia:
            centrosv = self.centros.copy()

            self.clases = self.actClases(muestrast, self.centros)
            self.centros = self.actCentros(self.clases, self.centros)

            sumd = 0
            for i in range(len(centrosv)):
                sumd = sumd + self.distEuc(centrosv[i], self.centros[i])

            eps = sumd

        return self.centros

    def actClases(self, muestras, centros):
        clases = []

        for i in range(len(centros)):
            aux = []
            clases.append(aux)

        for i in range(len(muestras)):
            index = 0
            dist = math.inf

            for j, centro in enumerate(centros):
                ndist = self.distEuc(muestras[i], centro)
                if ndist < dist:
                    index = j
                    dist = ndist

            clases[index].append(muestras[i])

        return clases

    def actCentros(self, clases, centros):
        c = []
        for i in range(len(centros)):
            c.append(np.mean(clases[i], axis=0))

        return c

    def distEuc(self, x, y, eje=1):
        res = 0
        for i in range(len(x)):
            res = res + ((x[i] - y[i]) ** 2)

        return math.sqrt(res)

    def clasificar(self, data):
        index = 0
        dist = math.inf

        for j, centro in enumerate(self.centros):
            ndist = self.distEuc(data, centro)
            if ndist < dist:
                index = j
                dist = ndist

        return [index, dist]


class MyApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.left = 10
        self.top = 10
        self.title = 'Clasificador múltiple-Roberto Pavón Benítez'
        self.width = 1000
        self.height = 700

        self.indx = 0
        self.indy = 1

        self.file = "Iris2Clases.txt"
        self.file2 = "TestIris01.txt"
        self.muestras = []
        self.tipos = []
        self.centros = []

        self.initUI()

    def initUI(self):
        fuente = QtGui.QFont("Times", 10, QtGui.QFont.Bold)
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.spx = QSpinBox(self)
        self.spx.setMinimum(1)
        self.spx.setMaximum(4)
        self.spx.setValue(1)
        self.spx.move(850, 100)
        self.spx.resize(40, 20)
        self.spx.valueChanged.connect(self.changeX)

        self.spy = QSpinBox(self)
        self.spy.setMinimum(1)
        self.spy.setMaximum(4)
        self.spy.setValue(2)
        self.spy.move(900, 100)
        self.spy.resize(40, 20)
        self.ly = QLabel("Atributos en los ejes: ", self)
        self.ly.move(730, 95)
        self.spy.valueChanged.connect(self.changeY)

        self.button = QPushButton('Mostrar', self)
        self.button.setToolTip('Carga los datos en la tabla')
        self.button.move(770, 125)
        self.button.resize(140, 30)
        self.button.clicked.connect(self.initPlot)

        self.button = QPushButton('Cargar', self)
        self.button.setToolTip('Carga los datos en la tabla')
        self.button.move(700, 500)
        self.button.resize(140, 40)
        self.button.clicked.connect(self.fileCargar)

        self.button2 = QPushButton('Clasificar', self)
        self.button2.setToolTip('Ejecuta el programa')
        self.button2.move(850, 500)
        self.button2.resize(140, 40)
        self.button2.clicked.connect(self.fileClasificar)

        self.loadData()
        self.m = PlotCanvas(self, width=7, height=6, muestras=self.muestras, index1=0, index2=1, tipos=self.tipos)
        self.m.move(0, 0)


        self.resultado = QLabel("Resultado: ", self)
        self.resultado.move(720,580)
        self.resultado.resize(90,40)

        self.output = QLabel("", self)
        self.output.move(800, 580)
        self.output.resize(200, 40)

        self.pertenencia = QLabel("Grado de pertenencia:", self)
        self.pertenencia.move(720, 620)
        self.pertenencia.resize(200, 40)

        self.output2 = QLabel("", self)
        self.output2.move(870, 620)
        self.output2.resize(200, 40)

        self.output.setFont(fuente)
        self.output2.setFont(fuente)
        self.resultado.setFont(fuente)
        self.pertenencia.setFont(fuente)

        self.show()

    def fileCargar(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        nombre, _ = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()", "",
                                                "Normal text file (*.txt)", options=options)
        if nombre:
            self.file = nombre
            self.loadData()
            self.initPlot()
            self.button2.setEnabled(True)

    def fileClasificar(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        nombre, _ = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()", "",
                                                "Normal text file (*.txt)", options=options)
        if nombre:
            self.file2 = nombre
            self.go()

    def changeX(self):
        self.indx = self.spx.value() - 1

    def changeY(self):
        self.indy = self.spy.value() - 1

    def initPlot(self):
        self.m.resetPlot(self.indx, self.indy)
        self.m.plotC(self.centros)

        self.show()

    def loadData(self):
        self.muestras = []
        self.tipos = []
        file = open(self.file, "r")
        lineas = file.readlines()

        for linea in lineas:
            terminos = linea.strip('\n').split(',')

            clase = terminos[-1]
            del terminos[-1]

            arr = []
            for item in terminos:
                arr.append(float(item))

            if clase not in self.tipos:
                self.tipos.append(clase)
                self.muestras.append([arr])
            else:
                self.muestras[self.tipos.index(clase)].append(arr)

    def actualizar(self, clases, centros, pred):
        self.m.plot(clases)
        self.m.plotC(centros)

    def mostrarSol(self, clases, centros, pred):
        self.m.plot(clases)
        self.m.plotC(centros)
        self.m.plotS(pred)

        self.output.setText(self.tipos[self.res[0]])
        self.output2.setText(str(round(self.res[1],4)))

    def loadInput(self):
        file = open(self.file2, "r")
        linea = file.readline()

        terminos = linea.strip('\n').split(',')

        del terminos[-1]

        prediccion = []
        for item in terminos:
            prediccion.append(float(item))

        return prediccion

    def loaded(self):
        return self.muestras is not None

    def getClass(self, algorithm, filename):
        file = open(filename, "r")
        data = file.read().strip('\n').split(',')

        try:
            return self.go(algorithm, data)
        except Exception as e:
            print(e)

    def go(self):
        algorithm = "K-medias"
        alg = Algoritmo(self.muestras, self)

        if algorithm == "K-medias":
            self.centros = alg.kmedias()

        pred = self.loadInput()
        self.res = alg.clasificar(pred)
        self.mostrarSol(self.muestras, self.centros, pred)



class PlotCanvas(FigureCanvas):

    def __init__(self, parent=None, width=5, height=4, dpi=100, muestras=None, index1=0, index2=1, tipos=[]):
        self.ax = None
        self.muestras = muestras
        self.index1 = index1
        self.index2 = index2
        self.tipos = tipos
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)

        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                                   QSizePolicy.Expanding,
                                   QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

        clases = []

        for linea in self.muestras:
            clase = []
            for caso in linea:
                clase.append([caso[index1], caso[index2]])
            clases.append(clase)

        self.plot(clases)

    def resetPlot(self, index1, index2):
        self.index1 = index1
        self.index2 = index2
        clases = []

        for linea in self.muestras:
            clase = []
            for caso in linea:
                clase.append([caso[index1], caso[index2]])
            clases.append(clase)

        self.plot(clases)

    def plotC(self, centros):
        for centro in centros:
            self.ax.scatter(centro[self.index1], centro[self.index2], marker="x", c='#050505')
        self.draw()

    def plotS(self, prediccion):
        self.ax.scatter(prediccion[self.index1], prediccion[self.index2], c='b')

        self.ax.set_title('Muestras')
        if len(self.tipos) == 2:
            self.ax.legend((self.tipos[0], self.tipos[1], "Centros"))
        if len(self.tipos) == 3:
            self.ax.legend((self.tipos[0], self.tipos[1], self.tipos[2], "Centros"))
        if len(self.tipos) == 4:
            self.ax.legend((self.tipos[0], self.tipos[1], self.tipos[2], self.tipos[3], "Centros"))
        if len(self.tipos) == 5:
            self.ax.legend(
                (self.tipos[0], self.tipos[1], self.tipos[2], self.tipos[3], self.tipos[4], "Centros"))
        self.draw()

    def plot(self, clases):
        colores = ['r', 'g', 'b', 'c', 'm', 'y']

        if self.ax is not None:
            self.ax.remove()
        self.ax = self.figure.add_subplot(111)

        for i, clase in enumerate(clases):
            x = []
            y = []
            for caso in clase:
                x.append(caso[0])
                y.append(caso[1])

            self.ax.scatter(x, y, c=colores[i])
        self.ax.set_title('Muestras')
        self.ax.legend(("Setosa", "Versicolor"))
        self.draw()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyApp()
    sys.exit(app.exec_())
