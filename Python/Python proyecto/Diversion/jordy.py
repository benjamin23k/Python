# Nodo de la lista doblemente ligada
class Nodo:
    def __init__(self, dato):
        self.dato = dato
        self.siguiente = None
        self.anterior = None

# Lista doblemente ligada
class ListaDoble:
    def __init__(self):
        self.cabeza = None
        self.cola = None

    # Método para verificar si la lista está vacía
    def esta_vacia(self):
        return self.cabeza is None

    # Insertar al inicio
    def insertar_inicio(self, dato):
        nuevo = Nodo(dato)
        if self.esta_vacia():
            self.cabeza = self.cola = nuevo
        else:
            nuevo.siguiente = self.cabeza
            self.cabeza.anterior = nuevo
            self.cabeza = nuevo

    # Insertar al final
    def insertar_final(self, dato):
        nuevo = Nodo(dato)
        if self.esta_vacia():
            self.cabeza = self.cola = nuevo
        else:
            self.cola.siguiente = nuevo
            nuevo.anterior = self.cola
            self.cola = nuevo

    # Buscar un valor
    def buscar(self, dato):
        actual = self.cabeza
        while actual:
            if actual.dato == dato:
                return True
            actual = actual.siguiente
        return False

    # Eliminar un nodo por valor
    def eliminar(self, dato):
        actual = self.cabeza
        while actual:
            if actual.dato == dato:
                if actual.anterior:
                    actual.anterior.siguiente = actual.siguiente
                else:
                    self.cabeza = actual.siguiente
                if actual.siguiente:
                    actual.siguiente.anterior = actual.anterior
                else:
                    self.cola = actual.anterior
                return True  # Eliminado
            actual = actual.siguiente
        return False  # No encontrado

    # Recorrer desde la cabeza
    def recorrer_inicio(self):
        elementos = []
        actual = self.cabeza
        while actual:
            elementos.append(actual.dato)
            actual = actual.siguiente
        return elementos

    # Recorrer desde la cola
    def recorrer_final(self):
        elementos = []
        actual = self.cola
        while actual:
            elementos.append(actual.dato)
            actual = actual.anterior
        return elementos

# Ejemplo de uso
if __name__ == "__main__":
    lista = ListaDoble()
    lista.insertar_inicio(10)
    lista.insertar_final(20)
    lista.insertar_inicio(5)
    print("Recorrido desde inicio:", lista.recorrer_inicio())
    print("Recorrido desde final:", lista.recorrer_final())
    print("Buscar 20:", lista.buscar(20))
    lista.eliminar(10)
    print("Recorrido después de eliminar 10:", lista.recorrer_inicio())
