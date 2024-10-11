from flask import Flask, request, jsonify, render_template

import json
import nltk
from nltk.stem.lancaster import LancasterStemmer
import numpy as np
import tflearn
import tensorflow as tf
import os

app = Flask(__name__)

with open('static/dataset.json') as file:
    data = json.load(file)

stemmer = LancasterStemmer()

words = []
labels = []
docs_x = []
docs_y = []

for intent in data['intents']:
    for pattern in intent['patterns']:
        wrds = nltk.word_tokenize(pattern)
        words.extend(wrds)
        docs_x.append(wrds)
        docs_y.append(intent['tag'])

    if intent['tag'] not in labels:
        labels.append(intent['tag'])

words = [stemmer.stem(w.lower()) for w in words if w != '?']
words = sorted(list(set(words)))

labels = sorted(labels)

training = []
output = []

out_empty = [0] * len(labels)

for x, doc in enumerate(docs_x):
    bag = []

    wrds = [stemmer.stem(w) for w in doc]

    for w in words:
        if w in wrds:
            bag.append(1)
        else:
            bag.append(0)
 
    output_row = out_empty[:]
    output_row[labels.index(docs_y[x])] = 1

    training.append(bag)
    output.append(output_row)

training = np.array(training)
output = np.array(output)

tf.compat.v1.reset_default_graph()
net = tflearn.input_data(shape=[None, len(training[0])])
net = tflearn.fully_connected(net, 8)
net = tflearn.fully_connected(net, 8)
net = tflearn.fully_connected(net, len(output[0]), activation='softmax')
net = tflearn.regression(net,learning_rate=0.01 )

model = tflearn.DNN(net)
model.load('model94.tflearn')
# model.fit(training, output, n_epoch=500, batch_size=32, show_metric=True)

def bag_of_words(s, words):
    bag = [0] * len(words)

    s_words = nltk.word_tokenize(s)
    s_words = [stemmer.stem(word.lower()) for word in s_words]

    for se in s_words:
        for i, w in enumerate(words):
            if w == se:
                bag[i] = 1

    return np.array(bag)
# routing
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/botchat")
def botchat():
    return render_template("botchat.html")

@app.route('/chat', methods=['POST'])
def chat():
    message = request.form['message']
    results = model.predict([bag_of_words(message, words)])[0]
    results_index = np.argmax(results)
    tag = labels[results_index]
    
    # Check if the confidence level is below a certain threshold
    threshold = 0.5  # Set your desired threshold here
    if results[results_index] < threshold:
        response = "Sorry, I didn't understand that."
    else:
        for intent in data['intents']:
            if intent['tag'] == tag:
                response = intent['responses']
                break
    
    # Returning response as JSON
    return jsonify(response)


if __name__ == '__main__':
    app.run(debug=True)
# end routing