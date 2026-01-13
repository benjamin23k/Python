import sys
import string

#print("Hi is my first time") Esto es lo que usamos para mostrar un mensaje en consola
#if 5>2:
 #   print("cinco es mas grande que dos") El if lo usamos para hacer una comparacion

# 1) Variables

#x = 5
#y = "ben"

#print (x)
#print (y)

#myvar = "john"

#x , y , z = "Naranja" , "Mango" , "Apple"

#print (x)
#print (y)
#print (x)

# Asignar multiple valores
#fruits = ["Orange", "Apple" , "Melon"]
#x ,y , z = fruits

#print (x)
#print (y)
#print (z)

#x = "Python"
#y = "Es"
#z =  "Increible"

#print (x, y , z)
#x = "Estoy afuera de"
#def myfunc():
 #x = "dentro de la funcion"
#print("Mi primera funcion global" + x)


#myfunc()

#print(x + " la funcion ")

# 2) Tipos de datos

#Tipo texto str --> Cadenas de texto "Ejemplo"
#Tipo numerico int --> Enteros 5  , float --> Deciamales 3.14 ,complex --> Numero complejos (2+3j)
#Tipo secuencia  list --> Listado ([1,2,3...etc]) , tuple--> Tubla inmutable((1,2,3..etc)) ,range --> (range)
#Tipo mapeado dict --> Diccionario con pares clave-valor ({"nombre": "Wilson"})
#Tipo Conjuntos 

#x = 2 #int
#y = 3.14#float
#n = 1j #complex

# diferent print

#print(type(x)) 
#a = "Hi wilson"
#print(a[1])


#b = "Hi wilson"
#print(b[3:5])

#c = "Hi wilson"
#print(c[:5])

#d = "Hi wilson"
#print(d[2:])


#a = "Hello world"        # print --> HELLO WORLD
#print(a.upper())

#b = "Hello world"        # print --> hello world
#print(b.lower())

#c = "Hello world"        # print --> Hello world 
#print(c.strip())  

#d = "Hello world"        # print --> jello world
#print(d.replace("H","j"))

#e = "Hello world"
#print(e.split(","))


# 3) String Concatenation


#a = "Hello"
#b = " Ben "
#c = a+b    # --> diferent form  c = a + " " + b
#print(c)


# 4) String Format


#age = 19
#txt = f"HI i am benjamin and i am {age} years old"
#print(txt)


#price = 59
#sold = f"The price is {price:2f} dollars"
#print(sold)

# txt = "We are the so-called \"Vikings\" from the north."


# 5) Booleans


#bool("abc")
#bool("1,2,3")
#bool(["Cherry", "Apple", "orange"])

#class myclass():

 #def __len__(self):

 # return 0 
 

#myobj = myclass()
#print(bool(myobj))

#def myfuntion() :

 #   return True

#if myfuntion():
# print("YES!!")
#else :
# print("No")


#  6) Operators


# +	Addition	x + y	
# -	Subtraction	x - y	
# *	Multiplication	x * y	
# /	Division	x / y	
# %	Modulus	x % y	
# **	Exponentiation	x ** y	
# //	Floor division	x // y

#==	Equal	x == y	
# !=	Not equal	x != y	
#>	Greater than	x > y	
#<	Less than	x < y	
#>=	Greater than or equal to	x >= y	
#<=	Less than or equal to	x <= y

#=	x = 5	x = 5	
#+=	x += 3	x = x + 3	
#-=	x -= 3	x = x - 3	
#*=	x *= 3	x = x * 3	
#/=	x /= 3	x = x / 3	
#%=	x %= 3	x = x % 3	
#//=	x //= 3	x = x // 3	
#**=	x **= 3	x = x ** 3	
#&=	x &= 3	x = x & 3	
#|=	x |= 3	x = x | 3	
#^=	x ^= 3	x = x ^ 3	
#>>=	x >>= 3	x = x >> 3	
#<<=	x <<= 3	x = x << 3	
#:=	print(x := 3)	x = 3
#print(x)

#()	Parentheses	
#**	Exponentiation	
#+x  -x  ~x	Unary plus, unary minus, and bitwise NOT	
#*  /  //  %	Multiplication, division, floor division, and modulus	
#+  -	Addition and subtraction	
#<<  >>	Bitwise left and right shifts	
#&	Bitwise AND	
#^	Bitwise XOR	
#|	Bitwise OR	
#==  !=  >  >=  <  <=  is  is not  in  not in 	Comparisons, identity, and membership operators	
#not	Logical NOT	
#and	AND	
#or	OR


# Lists

#mylist = ["Apple ", "SUGAR" , "GOLDEN APPLE"]
#print(mylist)


Newlist = ["PLAY 5" , "NINTENDO " , "SMARTPHONE"  ] 
print(len(Newlist))

list1 = ["tomato" , "Potatoes" , "CHerry"]
list2 = [ 1, 5 , 7, 9]
list3 = [True , False , False]

newlist = ["abc", 34 , True , 40 , "Benjamin"]

mylist = ["Apple ", "SUGAR" , "GOLDEN APPLE"]
print(type(mylist))