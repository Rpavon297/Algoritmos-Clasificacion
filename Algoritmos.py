class Bayes:
    def getResult(self, muestra):
        return muestra


class Fuzzy:
    def __init__(self, tolerancia=0.01, peso=2):
        self.tolerancia = tolerancia
        self.peso = peso

    def getResult(self, muestra):
        return muestra


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

            if terminos[-1] not in self.tipos:
                self.tipos.append(terminos[-1])

            self.muestras.append(terminos)


    def loaded(self):
        return self.muestras is not None

    def go(self, algorithm):
        alg = None

        if algorithm.equals("Fuzzy"):
            alg = Fuzzy()
        elif algorithm.equals("Bayes"):
            alg = Bayes()

        return alg.getResult(self.muestras)


if __name__ == "__main__":
    controlador = Controlador()
    controlador.loadData("Iris2Clases")

    if controlador.loaded():
        clasificacion = controlador.go("Fuzzy")
        print(clasificacion)

