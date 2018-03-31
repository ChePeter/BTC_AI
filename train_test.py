from keras.models import Model # basic class for specifying and training a neural network
from keras.utils import np_utils # utilities for one-hot encoding of ground truth values
from keras.layers import Dense, Input
from keras.layers import Bidirectional, GRU
from keras.models import Model
from keras.optimizers import RMSprop

import numpy as np
import keras as ks

num_classes = 2

length = 32
length_8 = length<<3
num_train = 50000
num_test = 10000


X_train = np.zeros(shape=(num_train, length_8), dtype='uint8')
y_train = np.zeros(shape=(num_train), dtype='uint8')

X_test = np.zeros(shape=(num_test, length_8), dtype='uint8')
y_test = np.zeros(shape=(num_test), dtype='uint8')

bx_train = np.zeros(shape=(num_train, length), dtype='uint8')
bx_test = np.zeros(shape=(num_test, length), dtype='uint8')

f_x = open("./input/x600_btc_32_LH.bin", 'rb')
for k in xrange(num_train):
    for i in xrange(32):
        bx_train[k, i] = ord(f_x.read(1))

for k in xrange(num_test):
    for i in xrange(32):
        bx_test[k, i] = ord(f_x.read(1))

f_x.close()

f_y = open("./input/y600_btc_32_LH.bin", 'rb')
for i in xrange(num_train):
    y_train[i] = ord(f_y.read(1))

for i in xrange(num_test):
    y_test[i] = ord(f_y.read(1))


f_y.close()
y_train -= 48
y_test -= 48


tab = np.zeros((256,8),dtype='int8')
for i in xrange(256):
    mask = 1
    for j in xrange(8):
        if i & mask == 0:
            tab[i,j] = 0
        else:
            tab[i,j] = 1
        mask<<1

for k in xrange(num_train):
    for i in xrange(length):
        for j in xrange(8):
            X_train[k,i*8+j] = tab[bx_train[k,i],j]

for k in xrange(num_test):
    for i in xrange(length):
        for j in xrange(8):
            X_test[k,i*8+j] = tab[bx_test[k,i],j]


X_train = X_train.astype('float32') 
X_test = X_test.astype('float32')
X_train /= 255.
X_test /= 255.

Y_train = np_utils.to_categorical(y_train, num_classes) # One-hot encode the labels
Y_test = np_utils.to_categorical(y_test, num_classes)

import math
from keras import backend as K
from keras.utils.generic_utils import get_custom_objects
from keras.layers import Activation

def gaussian(x):
    mu = 64.
    sigma = 10.
    xx = -0.5*((x-mu)/sigma)**2 / sigma / math.sqrt(2*math.pi)
    return K.exp(xx)

get_custom_objects().update({'gaussian': Activation(gaussian)})

batch_size = 32
num_epochs = 16
hidden_size_1 = 1024
hidden_size_2 = 1024

X_train = X_train.reshape(num_train,16,16)
X_test = X_test.reshape(num_test,16,16)

inp = Input(shape=(16,16,))
x = Bidirectional(GRU(1024, return_sequences=True))(inp)
x = Bidirectional(GRU(1024, return_sequences=False))(x)
x = Dense(hidden_size_1, activation='sigmoid')(x)
x = Dense(hidden_size_2, activation='gaussian')(x)

out = Dense(num_classes, activation='gaussian')(x)
#adam = ks.optimizers.adam(lr=0.0001, beta_1=0.9, beta_2=0.9999, epsilon=1e-16, decay=0.1)

model = Model(inputs=inp, outputs=out)
model.compile(loss='binary_crossentropy',
#              optimizer='adam',
              optimizer=RMSprop(lr=0.0001,clipvalue=1, clipnorm=1),
              metrics=['accuracy'])

mod = model.fit(X_train, Y_train,
          batch_size=batch_size, epochs=2,
          verbose=1, validation_data=(X_test, Y_test))

eva = model.evaluate(X_test, Y_test,  verbose=1)
print(eva)
