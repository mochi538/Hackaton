import random 
import json 
import pickle
import numpy as np

import nltk
from nltk.stem import WordNetLemmatizer

from keras.models import Sequential
from keras.layers import Dense, Dropout
from keras.optimizers import SGD  
from keras.optimizers.schedules import ExponentialDecay

lemmatizer = WordNetLemmatizer()
data_file = open('intentsNew.json','r',encoding='utf-8').read()
intents = json.loads(data_file) 



nltk.download('punkt')  
nltk.download('punkt_tab')
nltk.download('wordnet')
nltk.download('omw-1.4')

words = []
classes = []
documents = []
ignore_letters = ['?', '!', '¿', '.', ',']


for intent in intents['intents']:
    for pattern in intent['patterns']:
        word_list = nltk.word_tokenize(pattern)
        words.extend(word_list)  
        documents.append((word_list, intent["tag"]))
        if intent["tag"] not in classes:
            classes.append(intent["tag"])


words = [lemmatizer.lemmatize(word_list.lower()) for word_list in words if word_list not in ignore_letters]
words = sorted(list(set(words)))  
classes = sorted(list(set(classes)))

pickle.dump(words, open('words.pkl', 'wb'))
pickle.dump(classes, open('classes.pkl', 'wb'))


training = []
output_empty = [0] * len(classes)  


for document in documents:
    bag = []
    word_patterns = document[0]
    word_patterns = [lemmatizer.lemmatize(word.lower()) for word in word_patterns]
    
    for word in words:
        bag.append(1) if word in word_patterns else bag.append(0)

    output_row = list(output_empty)
    output_row[classes.index(document[1])] = 1
    training.append([bag, output_row])


random.shuffle(training)

train_x = [row[0] for row in training]
train_y = [row[1] for row in training]

model = Sequential()

model.add(Dense(128, input_shape = (len(train_x[0]),), activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(64, activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(len(train_y[0]), activation='softmax'))


lr_schedule = ExponentialDecay(
    initial_learning_rate = 0.01,
    decay_steps = 10000,
    decay_rate =0.9
)

sgd = SGD(learning_rate=lr_schedule, momentum=0.9, nesterov=True)
model.compile(loss='categorical_crossentropy', optimizer= sgd, metrics = ['accuracy'])

train_process = model.fit(np.array(train_x), np.array(train_y),epochs=100, batch_size=5, verbose=1)
model.save('chatbot_model.h5', train_process)


print("model created")
