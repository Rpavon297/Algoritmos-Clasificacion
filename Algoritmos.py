import numpy as np


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
                arr.append(cont/len(clase[0]))
            self.m.append(arr)

        restas = []
        for clase in muestras:
            c = []
            for muestra in clase:
                arr = []
                for elem in muestra:



    def getResult(self, datos):
        return datos


class Fuzzy:
    def __init__(self, muestra, tolerancia=0.01, peso=2):
        self.tolerancia = tolerancia
        self.peso = peso
        self.muestra = muestra

    def getResult(self, datos):
        return datos


class Controlador:
    def __init__(self, vista=None):
        self.vista = vista
        self.muestras = None
        self.tipos = []

    def loadData(self, filename):
        self.muestras = []
        file = open(filename, "r")
        lineas = file.readlines()

        for linea in lineas:
            terminos = linea.strip('\n').split(',')

            clase = terminos[-1]
            del terminos[-1]

            arr = []
            for item in terminos:
                arr.append(int(item))

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
            alg = Fuzzy(self.muestras, self.tipos)
        elif algorithm == "Bayes":
            alg = Bayes(self.muestras, self.tipos)

        return alg.getResult(data)


if __name__ == "__main__":
    controlador = Controlador()
    controlador.loadData("Iris2Clases.txt")

    if controlador.loaded():
        clasificacion = controlador.getClass("Fuzzy", "TestIris01.txt")
        print(clasificacion)
