

#importamos librerias
import tensorflow as tf
import tensorflow_datasets as tfds #para descargar los datasets de zalando
import matplotlib.pyplot as plt
import math

datos,metadatos = tfds.load('fashion_mnist',as_supervised=True,with_info=True)#dataset de zalando

type(metadatos)

datos_train,datos_test = datos['train'],datos['test']#Cargamos los datos de train y test en sus variables

#cargamos las etiquetas de metadatos
nombre_labels = metadatos.features['label'].names
nombre_labels

#Queremos normalizar los datos que estan entre 0 y 255 --- a --- 0 y 1

def normalizar(imagenes,etiquetas):
  #casteamos con tensorflow a float
  imagenes = tf.cast(imagenes , tf.float32)
  #normalizamos
  imagenes/=255
  #retornamos imagenes y etiquetas
  return imagenes,etiquetas

#cogemos el conjunto de train y test y lo normalizamos
datos_train = datos_train.map(normalizar)
datos_test = datos_test.map(normalizar)

#vamos a mostrar unas imagenes redimensionandola
plt.figure(figsize=(10,10))#creamos la figura 10x10 para que se use en todo el bucle
for i,(imagen,etiqueta) in enumerate(datos_train.take(25)):
  imagen = imagen.numpy().reshape((28,28)) #aqui redimensionamos la imagen a 28x28 pixeles

  plt.subplot(5,5,i+1)
  plt.xticks([])
  plt.yticks([])
  plt.grid(False)
  plt.imshow(imagen,cmap=plt.cm.binary)
  plt.xlabel(nombre_labels[etiqueta])
plt.show()

#Creamos el modelo con flatten y una matriz de 28x28 con una salida en blanco y negro lo que hace Flatten es aplastar la matriz hasta convertirla en una sola dimension
#Añadimos dos capas con 50 neuronas densas(Dense) y la activacion relu(activacion que si el numero es negativo lo convierte a 0 y si es positivo lo deja tal cual)
#La ultima capa es la de salidad con 10 neuronas es decir las diez labels posibles y le añadimos softmax que es una funcion de activacion en la capa de salida
#la cual nos asegura que si predice que un pantalon tiene 0.8 lo aproxime  a 1
modelo = tf.keras.Sequential([
    tf.keras.layers.Flatten(input_shape=(28,28,1)),
    tf.keras.layers.Dense(50,activation=tf.nn.relu),
    tf.keras.layers.Dense(50,activation=tf.nn.relu),
    tf.keras.layers.Dense(10,activation=tf.nn.softmax)
])

#ahora compilamos el modelo

modelo.compile(
    optimizer='adam',
    loss=tf.keras.losses.SparseCategoricalCrossentropy(),
    metrics=['accuracy']
)

#para que el entrenamiento sea mas rapido lo vamos a hacer por lotes
NUM_LOTES=32 #sacamos el numero de lotes
num_total_train = metadatos.splits['train'].num_examples #sacamos el tamaño de train total
num_total_test = metadatos.splits['test'].num_examples #sacamos el tamaño de test total

datos_train = datos_train.repeat().shuffle(num_total_train).batch(NUM_LOTES)
datos_test = datos_test.batch(NUM_LOTES)

#Entrenamos
historial = modelo.fit(datos_train,epochs=5,steps_per_epoch=math.ceil(num_total_train/NUM_LOTES))#Entrenamos el modelo con los datos train y decimos cuantas cueltas queremos que de con epochs

#Pintar una cuadricula con varias predicciones, y marcar si fue correcta (azul) o incorrecta (roja)
import numpy as np

for imagenes_prueba, etiquetas_prueba in datos_test.take(1):
  imagenes_prueba = imagenes_prueba.numpy()
  etiquetas_prueba = etiquetas_prueba.numpy()
  predicciones = modelo.predict(imagenes_prueba)

def graficar_imagen(i, arr_predicciones, etiquetas_reales, imagenes):
  arr_predicciones, etiqueta_real, img = arr_predicciones[i], etiquetas_reales[i], imagenes[i]
  plt.grid(False)
  plt.xticks([])
  plt.yticks([])

  plt.imshow(img[...,0], cmap=plt.cm.binary)

  etiqueta_prediccion = np.argmax(arr_predicciones)
  if etiqueta_prediccion == etiqueta_real:
    color = 'blue'
  else:
    color = 'red'

  plt.xlabel("{} {:2.0f}% ({})".format(nombre_labels[etiqueta_prediccion],
                                100*np.max(arr_predicciones),
                                nombre_labels[etiqueta_real]),
                                color=color)

def graficar_valor_arreglo(i, arr_predicciones, etiqueta_real):
  arr_predicciones, etiqueta_real = arr_predicciones[i], etiqueta_real[i]
  plt.grid(False)
  plt.xticks([])
  plt.yticks([])
  grafica = plt.bar(range(10), arr_predicciones, color="#777777")
  plt.ylim([0, 1])
  etiqueta_prediccion = np.argmax(arr_predicciones)

  grafica[etiqueta_prediccion].set_color('red')
  grafica[etiqueta_real].set_color('blue')

filas = 5
columnas = 5
num_imagenes = filas*columnas
plt.figure(figsize=(2*2*columnas, 2*filas))
for i in range(num_imagenes):
  plt.subplot(filas, 2*columnas, 2*i+1)
  graficar_imagen(i, predicciones, etiquetas_prueba, imagenes_prueba)
  plt.subplot(filas, 2*columnas, 2*i+2)
  graficar_valor_arreglo(i, predicciones, etiquetas_prueba)
