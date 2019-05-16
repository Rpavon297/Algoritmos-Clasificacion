import random
import sys

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar)

import numpy as np
from PyQt5 import uic, QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QSizePolicy, QPushButton, QCheckBox, QButtonGroup


class Bayes:
    def __init__(self, muestras, clases):
        self.muestras = muestras
        self.clases = clases
        self.m = []

        for clase in muestras:
            arr = []
            for i in range(len(clase[0])):
                cont = 0
                for caso in clase:
                    cont = cont + caso[i]
                arr.append(cont / len(clase[0]))
            self.m.append(arr)

        restas = []
        for clase in muestras:
            c = []
            for muestra in clase:
                arr = []
                for elem in muestra:
                    print("")

    def getResult(self, datos):
        return datos


class Kmedias:
    def __init__(self, muestra, tolerancia=0.01, peso=2):
        self.tolerancia = tolerancia
        self.peso = peso
        self.muestra = muestra

    def distEuc(self, x, y):
        res = 0

        for i in range(len(x)):
            res = res + (x[i] - y[i])

        return res ** 2

    def getResult(self, datos):
        return datos


qtCreatorFile = "plot.ui"

Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)


class MyApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.left = 10
        self.top = 10
        self.title = 'Clasificador múltiple-Roberto Pavón Benítez'
        self.width = 1000
        self.height = 650

        self.file = "Iris2Clases.txt"
        self.muestras = None
        self.tipos = []

        self.loadData()
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        button = QPushButton('Cargar', self)
        button.setToolTip('Carga los datos en la tabla')
        button.move(780, 100)
        button.resize(140, 100)
        button.clicked.connect(self.initPlot)

        self.bg = []
        for i, clase in enumerate(self.muestras[0][0]):
            self.cb = QCheckBox("Atributo {}".format(str(i)), self)
            self.bg.append(self.cb)
            self.cb.stateChanged.connect(self.changeAtt)
            self.cb.move(760, 220 + i*20)
            self.cb.resize(320, 40)

        self.m = PlotCanvas(self, width=7, height=6, muestras=self.muestras, index1=0, index2=1)
        self.m.move(0, 0)

        self.show()

    def changeAtt(self,state):
        print("boop")

    def initPlot(self):

        index1 = 1
        index2 = 2

        self.m.resetPlot(index1,index2)

        self.show()

    def hello(self):
        print("Hello world")

    def loadData(self):
        self.muestras = []
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

    def loaded(self):
        return self.muestras is not None

    def getClass(self, algorithm, filename):
        file = open(filename, "r")
        data = file.read().strip('\n').split(',')

        try:
            return self.go(algorithm, data)
        except Exception as e:
            print(e)

    def go(self, algorithm, data):
        alg = None

        if algorithm == "Fuzzy":
            alg = Kmedias(self.muestras, self.tipos)
        elif algorithm == "Bayes":
            alg = Bayes(self.muestras, self.tipos)

        return alg.getResult(data)


class PlotCanvas(FigureCanvas):

    def __init__(self, parent=None, width=5, height=4, dpi=100, muestras=None, index1=0, index2=1):
        self.ax = None
        self.muestras = muestras
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
        clases = []

        for linea in self.muestras:
            clase = []
            for caso in linea:
                clase.append([caso[index1], caso[index2]])
            clases.append(clase)

        self.plot(clases)


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

"""
if __name__ == "__main__":
    controlador = Controlador()
    controlador.loadData("Iris2Clases.txt")

    if controlador.loaded():
        clasificacion = controlador.getClass("Fuzzy", "TestIris01.txt")
        print(clasificacion)
"""
