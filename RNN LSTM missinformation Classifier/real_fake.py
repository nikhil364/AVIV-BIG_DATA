#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 25 20:44:19 2021

@author: nikhilsaini
"""



import warnings
import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)

from sklearn.feature_extraction.text import CountVectorizer
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
from keras.models import Sequential
from keras.layers import Dense, Embedding, LSTM
from sklearn.model_selection import train_test_split
from keras.utils.np_utils import to_categorical

import re



data = pd.read_csv("/Users/nikhilsaini/Downloads/read_fake_dat.csv", encoding="latin-1")

#data.columns = ["ids", "target", "id", "date", "flag", "user", "text"]

data = data[['title','label']]

#data = data[data.sentiment != "Neutral"
data['title'] = data['title'].apply(lambda x: x.lower())
data['title'] = data['title'].apply((lambda x: re.sub('[^a-zA-z0-9\s]','',x)))


size = data.label.value_counts(0)

for idx,row in data.iterrows():
   # print(row)
    #print("-----------------------------")
    #print(row[0])
    #print("-----------------------------")
    row[0] = row[0].replace('rt',' ')
    #print(row[0])                        

max_fatures = 2000
tokenizer = Tokenizer(num_words=max_fatures, split=' ')
tokenizer.fit_on_texts(data['title'].values)
X = tokenizer.texts_to_sequences(data['title'].values)
X = pad_sequences(X)    

embed_dim = 128
lstm_out = 196

model = Sequential()
model.add(Embedding(max_fatures, embed_dim,input_length = X.shape[1], dropout=0.2))
model.add(LSTM(lstm_out, dropout_U=0.2, dropout_W=0.2))
model.add(Dense(2,activation='softmax'))
model.compile(loss = 'categorical_crossentropy', optimizer='adam',metrics = ['accuracy'])
print(model.summary())

Y = pd.get_dummies(data['label']).values
X_train, X_test, Y_train, Y_test = train_test_split(X,Y, test_size = 0.33, random_state = 0)
print(X_train.shape,Y_train.shape)
print(X_test.shape,Y_test.shape)

batch_size = 32
#fitting = model.fit(X_train, Y_train, nb_epoch = 7, batch_size=batch_size, verbose = 2)
fitting = model.fit(X_train, Y_train, nb_epoch = 5, batch_size=batch_size, verbose=1, validation_split=0.33 )

validation_size = 15

X_validate = X_test[-validation_size:]
Y_validate = Y_test[-validation_size:]
X_test = X_test[:-validation_size]
Y_test = Y_test[:-validation_size]
score,acc = model.evaluate(X_test, Y_test, verbose = 2, batch_size = batch_size)
print("score: %.2f" % (score))
print("acc: %.2f" % (acc))


pos_cnt, neg_cnt, pos_correct, neg_correct = 0, 0, 0, 0
for x in range(len(X_validate)):
    
    result = model.predict(X_validate[x].reshape(1,X_test.shape[1]),batch_size=1,verbose = 2)[0]
   
    if np.argmax(result) == np.argmax(Y_validate[x]):
        if np.argmax(Y_validate[x]) == 0:
            neg_correct += 1
        else:
            pos_correct += 1
       
    if np.argmax(Y_validate[x]) == 0:
        neg_cnt += 1
    else:
        pos_cnt += 1

print(pos_cnt, neg_cnt, pos_correct, neg_correct)

#print("pos_acc", pos_correct/pos_cnt*100, "%")
#print("neg_acc", neg_correct/neg_cnt*100, "%")


import matplotlib.pyplot as plt

plt.plot(fitting.history['acc'])
plt.plot(fitting.history['val_acc'])

plt.title('model accuracy')
plt.ylabel('accuracy')
plt.xlabel('epoch')
plt.legend(['train','test'], loc='upper left')
plt.show()

plt.plot(fitting.history['loss'])
plt.plot(fitting.history['val_loss'])

plt.title('model loss')
plt.ylabel('loss')
plt.xlabel('epoch')
plt.legend(['train','test'], loc='upper left')
plt.show()



