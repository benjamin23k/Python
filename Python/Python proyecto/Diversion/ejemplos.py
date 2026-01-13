
#funciones con numeros ejemplos

def suma(a , b):
    print(a+b)

suma(2 , 3)

def resta(a , b):
    print(a-b)

resta( 8 , 3)
 

def multiplicar( a , b):
    print(a*b)

multiplicar (7 , 3)         



#strings utilizan doble comillas o comilla simple

nombre = "wilson"
print(nombre)

#enteros
edad = 18
edad = 20
print(edad)

#floats o flotantes
cantidad_a_pagar = 100.50
print(cantidad_a_pagar)

#un boolean es true o false
pagado  = False
print(pagado)

#la importancia del orden y espacio
#como se crea un arreglo

meses = ["enero" , "febrero", "marzo"]

print(meses)

#los arrays (lists) comienzan en la posicion 0
print (meses[0]) #enero

#Ordenar los elementos
meses.sort()
print(meses)

#acceder a un elemento de un texto
aprendiendo = f'Estoy aprendiendo sobre {meses[3]}'
print(aprendiendo)

#modificando valores de un arreglo (list)

meses[3] = 'abril'
print(meses)

#agregar elementos a un arreglo (list)

meses.append('abril')
print(meses)


#Eliminar de un arreglo (list)
del  meses[0]
print(meses)

#Eliminar de un arreglo (list)
meses.pop() #Elimina el ultimo elemento

print(meses)

# eliminar con pop una posicion en especifico
meses.pop(1)
print(meses)

# Eliminar por nombre
meses.remove('enero')
print(meses)


#Iterador

lenguajes = ['python' , 'hotlin', 'java', 'javaScript', 'php']


#Iterador 
for lenguaje in lenguajes:
    print(lenguaje)

#Iterador  Variante

for lenguaje in lenguajes:
    print(f'Estoy aprendiendo {lenguaje}')



# For que escriba numeros 
for numero in range(0, 30, 3):
    print(numero)




# Condicional


balance = 500


if balance >0:
  print("Puedes pagar")


#Operadores que se pueden evaluar para una condiocion
# == Igual a
#!= Diferente a
#> Mayor a
#>= Mayor o igual a
#< Menor a
#<= menor o igual a

#Revisar si una concidion es mayor a 
balance = 500
if balance > 0:
    print('puedes pagar')


# If....else...

balance = 500
if balance > 0:
    print('puedes pagar')
else:
    print('No tienes saldo')


#likes 
likes = 300
if likes== 300:
    print('Excelente, 300 likes')


#IF con texto
lenguaje = 'python'
if lenguaje == 'python':
  print('Excelente decision')

#Variante
lenguaje = 'Php'
if not lenguaje == 'python':
  print('Excelente decision')


#Evaluar un Boolean
usuario_autenticado = True

if usuario_autenticado == True:
    print('Acceso al sistema')
else:
    print('Debes iniciar sesion')


#Evaluar un elemento de una lista
lenguajes = ['python' , 'hotlin', 'java', 'javaScript', 'php']
if 'Ruby' in lenguajes:
    print('Esta en la lista ')
else:
    print('no esta en la lista ')


#If Anidados
usuario_autenticado = True
usuario_admin = True

if usuario_autenticado == True:
    if usuario_admin:
        print('Acceso total al sistema')
    else:
        print('Acceso al sistema')
else:
    print('Debes iniciar sesion')


#If...elif...else... en python

ocupacion = 'Estudiante'


if ocupacion == 'Estudiante':
    print('Tienes 50% de descuento')
elif ocupacion == 'jubilado':
    print('Tienes 75% de Descuento')
else:
    print('Debes pagar el 100%')





#while condición:
    # Código a ejecutar
    # No olvides modificar algo dentro del bucle para que termine en algún momento.

contador = 1

while contador <= 5:
    print(f"Número: {contador}")
    contador += 1  # Incrementamos el contador para evitar un bucle infinito


# Lista para registrar las actividades paso a paso
actividades = []

def registrar_actividad(paso):
    actividades.append(paso)
    print(f"Registrado: {paso}")

def mostrar_ultima_actividad():
    if actividades:
        print(f"La última actividad que hiciste fue: {actividades[-1]}")
    else:
        print("No hay actividades registradas.")

# Ejemplo de uso
registrar_actividad("Abriste el programa.")
registrar_actividad("Escribiste tu nombre.")
registrar_actividad("Presionaste Enter.")
mostrar_ultima_actividad()


#Ejemplo de como im
def saludar_usuario(nombre):
    print(f"¡Hola, {nombre}! Espero que tengas un gran día.")

# Ejemplo de uso:
usuario = input("Por favor, ingresa tu nombre: ")
saludar_usuario(usuario)
