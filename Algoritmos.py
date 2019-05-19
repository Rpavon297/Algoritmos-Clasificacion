import math
import random
import sys
import time

import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar)

import numpy as np
from PyQt5 import uic, QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QSizePolicy, QPushButton, QCheckBox, QButtonGroup, QSpinBox, \
    QLabel, QVBoxLayout, QFileDialog, QComboBox, QDoubleSpinBox, QFrame


class Algoritmo:
    def __init__(self, muestras, plot):
        self.plot = plot
        self.centros = []
        self.clases = []
        self.C = None

        self.muestras = muestras

    def setK(self, tolerancia, peso):
        self.tolerancia = 10**(tolerancia)
        self.peso = peso

    def setL(self, tolerancia, iteraciones, razon):
        self.tolerancia = 10**(tolerancia)
        self.iteraciones = iteraciones
        self.razon = razon

    def bayes(self):
        self.C = []
        for clase in self.muestras:
            self.C.append(self.resumir(clase))


        return self.centros

    def lloyd(self):
        eps = self.tolerancia + 1
        cont = 0
        centrosv = []
        muestrast = []
        # Sacamos los centros semi al azar (1 por clase) y metemos todas las muestras en el mismo array
        for clase in self.muestras:
            self.centros.append(clase[random.randint(0, len(clase) - 1)])
            for elem in clase:
                muestrast.append(elem)

        while eps > self.tolerancia and cont < self.iteraciones:
            centrosv = self.centros.copy()

            self.clases = self.actClases(muestrast, self.centros)
            self.centros = self.actCentrosL(muestrast, self.centros)

            sumd = 0
            for i in range(len(centrosv)):
                sumd = sumd + self.distEuc(centrosv[i], self.centros[i])

            eps = sumd
            cont = cont + 1

        return self.centros

    def kmedias(self):
        eps = self.tolerancia + 1
        muestrast = []
        # Sacamos los centros semi al azar (1 por clase) y metemos todas las muestras en el mismo array
        for clase in self.muestras:
            self.centros.append(clase[random.randint(0, len(clase) - 1)])
            for elem in clase:
                muestrast.append(elem)

        # Actualizamos centros y clases
        while eps > self.tolerancia:
            centrosv = self.centros.copy()

            try:
                self.plot.actualizar(self.clases, self.centros)
            except Exception as e:
                print(e)

            self.clases = self.actClases(muestrast, self.centros)
            self.centros = self.actCentros(self.clases, self.centros)

            sumd = 0
            for i in range(len(centrosv)):
                sumd = sumd + self.distEuc(centrosv[i], self.centros[i])

            eps = sumd

        return self.centros

    def resumir(self, data):
        return [(self.media(attribute), self.stdev(attribute)) for attribute in zip(*data)]


    def actCentrosL(self, muestras, centros):
        for i, linea in enumerate(muestras):
            index = 0
            dist = math.inf

            for j, centro in enumerate(centros):
                ndist = self.distEuc(muestras[i], centro)
                if ndist < dist:
                    index = j
                    dist = ndist

            # Index es el centro que tenemos que actualizar
            nuevo_centro = np.add(self.centros[index],
                                  np.multiply(self.razon, np.subtract(muestras[i], centros[index])))
            centros[index] = nuevo_centro

        return centros

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

    def media(self, numbers):
        return sum(numbers) / float(len(numbers))

    def stdev(self, numbers):
        avg = self.media(numbers)
        variance = sum([pow(x - avg, 2) for x in numbers]) / float(len(numbers) - 1)
        return math.sqrt(variance)

    def distEuc(self, x, y, eje=1):
        res = 0
        for i in range(len(x)):
            res = res + ((x[i] - y[i]) ** 2)

        return math.sqrt(res)

    def densProb(self, x, media, stdev):
        exponente = math.exp(-(math.pow(x - media, 2) / (2 * math.pow(stdev, 2))))
        return (1 / (math.sqrt(2 * math.pi) * stdev)) * exponente

    def clasificar(self, data):
        if self.C is not None:
            probabilidades = []
            for n, clase in enumerate(self.C):
                probabilidades.append(1)
                for i in range(len(clase)):
                    #Sacamos los datos para el att i, en la clase "clase"
                    media = clase[i][0]
                    stdev = clase[i][1]
                    att = data[i]
                    probabilidades[n] *= self.densProb(att, media, stdev)

            index = 0
            grad = 0
            for i, prob in enumerate(probabilidades):
                if prob > grad:
                    grad = prob
                    index = i
            return [index,grad]

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
        self.left = 200
        self.top = 200
        self.title = 'Clasificador múltiple-Roberto Pavón Benítez'
        self.width = 1000
        self.height = 620

        self.indx = 0
        self.indy = 1

        self.file = "Iris2Clases.txt"
        self.file2 = "TestIris01.txt"
        self.muestras = []
        self.tipos = []
        self.centros = []
        self.sol = None

        self.initUI()

    def initUI(self):
        fuente = QtGui.QFont("Times", 10, QtGui.QFont.Bold)
        self.setWindowTitle(self.title)
        #self.setGeometry(self.left, self.top, self.width, self.height)
        self.setFixedSize(self.width,self.height)

        self.back = QFrame(self)
        self.back.move(0,0)
        self.back.resize(self.width, self.height)
        self.back.setStyleSheet("background-color: #DFDFDF;")

        self.panel1 = QFrame(self)
        self.panel1.move(720,60)
        self.panel1.resize(260,110)
        self.panel1.setStyleSheet("border-style: solid;"
                                  "border-width: 2px;"
                                  "border-color: #A0A0A0;"
                                  "background-color: #DFDFDF;")

        self.panel2 = QFrame(self)
        self.panel2.move(720, 180)
        self.panel2.resize(260, 170)
        self.panel2.setStyleSheet("border-style: solid;"
                                  "border-width: 2px;"
                                  "border-color: #A0A0A0;"
                                  "background-color: #DFDFDF;")


        self.titulo = QLabel("Clasificador", self)
        self.titulo.move(820,20)

        self.spx = QSpinBox(self)
        self.spx.setMinimum(1)
        self.spx.setMaximum(4)
        self.spx.setValue(1)
        self.spx.move(870, 70)
        self.spx.resize(40, 20)
        self.spx.valueChanged.connect(self.changeX)

        self.spy = QSpinBox(self)
        self.spy.setMinimum(1)
        self.spy.setMaximum(4)
        self.spy.setValue(2)
        self.spy.move(920, 70)
        self.spy.resize(40, 20)
        self.ly = QLabel("Observar atributos: ", self)
        self.ly.move(740, 65)
        self.spy.valueChanged.connect(self.changeY)

        self.algoritmos = QComboBox(self)
        self.algoritmos.addItems(["K-medias", "Lloyd", "Bayes"])
        self.algoritmos.resize(70,30)
        self.algoritmos.move(880, 195)

        self.algoritmos.currentTextChanged.connect(self.actualizarInputs)

        labelAlg = QLabel("Algoritmo de clasificacion: ", self)
        labelAlg.resize(150, 20)
        labelAlg.move(740, 200)

        self.param1 = QLabel("Tolerancia (10^):", self)
        self.param2 = QLabel("Peso exponencial:", self)
        self.param3 = QLabel("", self)
        self.param1.move(740, 240)
        self.param2.move(740, 270)
        self.param3.move(740, 300)
        self.param3.resize(120,35)

        self.input1 = QSpinBox(self)
        self.input2 = QSpinBox(self)
        self.input3 = QDoubleSpinBox(self)

        self.input1.setMinimum(-20)
        self.input1.setMaximum(-1)
        self.input1.setValue(-2)
        self.input1.move(900, 245)
        self.input1.resize(60, 20)

        self.input2.setMinimum(1)
        self.input2.setMaximum(10)
        self.input2.setValue(2)
        self.input2.move(900, 275)
        self.input2.resize(60, 20)

        self.solucion = QFrame(self)
        self.solucion.move(750, 370)
        self.solucion.resize(220,115)
        self.solucion.setStyleSheet("background-color: #D5D5D5")

        self.button = QPushButton('Mostrar', self)
        self.button.setToolTip('Carga los datos en la tabla')
        self.button.move(790, 125)
        self.button.resize(140, 30)
        self.button.clicked.connect(self.initPlot)

        self.button = QPushButton('Cargar muestras', self)
        self.button.setToolTip('Carga los datos en la tabla')
        self.button.move(720, 500)
        self.button.resize(130, 40)
        self.button.clicked.connect(self.fileCargar)

        self.button2 = QPushButton('Clasificar', self)
        self.button2.setToolTip('Ejecuta el programa')
        self.button2.move(850, 500)
        self.button2.resize(130, 40)
        self.button2.clicked.connect(self.fileClasificar)

        self.loadData()
        self.m = PlotCanvas(self, width=7, height=6, muestras=self.muestras, index1=0, index2=1, tipos=self.tipos)
        self.m.move(0, 0)

        self.resultado = QLabel("Resultado: ", self)
        self.resultado.move(770, 380)
        self.resultado.resize(90, 40)

        self.output = QLabel("", self)
        self.output.move(860, 380)
        self.output.resize(200, 40)

        self.pertenencia = QLabel("Grado de \npertenencia:", self)
        self.pertenencia.move(770, 420)
        self.pertenencia.resize(200, 40)

        self.output2 = QLabel("", self)
        self.output2.move(860, 428)
        self.output2.resize(200, 40)

        self.output.setFont(fuente)
        self.output2.setFont(fuente)
        self.resultado.setFont(fuente)
        self.pertenencia.setFont(fuente)
        self.titulo.setFont(fuente)

        self.show()

    def actualizarInputs(self, value):
        if value == "K-medias":
            self.param1.setText("Tolerancia (10^):")
            self.param2.setText("Peso exponencial:")
            self.param3.setText("")

            self.input1.setMinimum(-20)
            self.input1.setMaximum(-1)
            self.input1.setValue(-2)
            self.input1.move(900, 245)
            self.input1.resize(60, 20)

            self.input2.setMinimum(1)
            self.input2.setMaximum(10)
            self.input2.setValue(2)
            self.input2.move(900, 275)
            self.input2.resize(60, 20)

            self.input1.setVisible(True)
            self.input2.setVisible(True)
            self.input3.setVisible(False)

        if value == "Lloyd":
            self.param1.setText("Tolerancia (10^):")
            self.param2.setText("Iteraciones máximas:")
            self.param3.setText("Razón de aprendizaje:")

            self.input1.setMinimum(-20)
            self.input1.setMaximum(-1)
            self.input1.setValue(-10)
            self.input1.move(900, 245)
            self.input1.resize(60, 20)

            self.input2.setMinimum(5)
            self.input2.setMaximum(20)
            self.input2.setValue(10)
            self.input2.move(900, 275)
            self.input2.resize(60, 20)

            self.input3.setDecimals(2)
            self.input3.setMinimum(0.05)
            self.input3.setMaximum(0.95)
            self.input3.setValue(0.1)
            self.input3.setSingleStep(0.05)
            self.input3.move(900, 305)
            self.input3.resize(60, 20)

            self.input1.setVisible(True)
            self.input2.setVisible(True)
            self.input3.setVisible(True)

        if value == "Bayes":
            self.param1.setText("")
            self.param2.setText("")
            self.param3.setText("")

            self.input1.setVisible(False)
            self.input2.setVisible(False)
            self.input3.setVisible(False)

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
        if self.sol is not None:
            self.m.plotS(self.sol)

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

    def actualizar(self, clases, centros):
        self.m.plot(clases)
        self.m.plotC(centros)
        self.m.actPlot()

    def mostrarSol(self, clases, centros, pred):
        extrac = []

        for linea in clases:
            aux = []
            for caso in linea:
                aux.append([caso[self.indx], caso[self.indy]])
            extrac.append(aux)

        self.m.plot(extrac)
        self.m.plotC(centros)
        isbayes = True
        if self.centros:
            isbayes = False
        self.m.plotS(pred,isbayes)

        self.output.setText(self.tipos[self.res[0]])
        self.output2.setText(str(round(self.res[1], 4)))

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
        try:
            alg = Algoritmo(self.muestras, self)

            if str(self.algoritmos.currentText()) == "K-medias":
                alg.setK(self.input1.value(), self.input2.value())
                self.centros = alg.kmedias()
            if str(self.algoritmos.currentText()) == "Lloyd":
                alg.setL(self.input1.value(), self.input2.value(), self.input3.value())
                self.centros = alg.lloyd()
            if str(self.algoritmos.currentText()) == "Bayes":
                self.centros = alg.bayes()

            pred = self.loadInput()
            self.sol = pred
            self.res = alg.clasificar(pred)
            self.mostrarSol(self.muestras, self.centros, pred)
        except Exception as e:
            print(e)


class PlotCanvas(FigureCanvas):

    def __init__(self, parent=None, width=5, height=4, dpi=100, muestras=None, index1=0, index2=1, tipos=[]):
        self.ax = None
        self.muestras = muestras
        self.index1 = index1
        self.index2 = index2
        self.tipos = tipos

        plt.ion()
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)

        FigureCanvas.__init__(self, self.fig)
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

    def actPlot(self):
        self.fig.canvas.draw_idle()

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

    def plotS(self, prediccion, isbayes):
        self.ax.scatter(prediccion[self.index1], prediccion[self.index2], c='b')

        self.ax.set_title('Muestras')
        if isbayes:
            if len(self.tipos) == 2:
                self.ax.legend((self.tipos[0], self.tipos[1]))
            if len(self.tipos) == 3:
                self.ax.legend((self.tipos[0], self.tipos[1], self.tipos[2]))
            if len(self.tipos) == 4:
                self.ax.legend((self.tipos[0], self.tipos[1], self.tipos[2], self.tipos[3]))
            if len(self.tipos) == 5:
                self.ax.legend(
                    (self.tipos[0], self.tipos[1], self.tipos[2], self.tipos[3], self.tipos[4]))

        else:
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

            self.ax.scatter(x, y, marker=".", c=colores[i])
        self.ax.set_title('Muestras')
        self.ax.legend(("Setosa", "Versicolor"))
        self.draw()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyApp()
    sys.exit(app.exec_())
