from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, render_to_response
from django.http import HttpResponse
import json
from django.views.decorators.csrf import csrf_exempt
from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer
import nltk
from nltk.stem import WordNetLemmatizer
lemmatizer = WordNetLemmatizer()
import pickle
import numpy as np
import h5py
import os
THIS_FOLDER = os.getcwd()
my_file = os.path.join(THIS_FOLDER, 'chatbot_model.h5')
my_file1 = os.path.join(THIS_FOLDER, 'words.pkl')
my_file2 = os.path.join(THIS_FOLDER, 'classes.pkl')
my_file3 = os.path.join(THIS_FOLDER, 'intents.json')




from tensorflow.keras.models import load_model
model = load_model(my_file)
import json
import random
intents = json.loads(open(my_file3).read())
words = pickle.load(open(my_file1,'rb'))
classes = pickle.load(open(my_file2,'rb'))

def clean_up_sentence(sentence):
    # tokenize the pattern - split words into array
    sentence_words = nltk.word_tokenize(sentence)
    # stem each word - create short form for word
    sentence_words = [lemmatizer.lemmatize(word.lower()) for word in sentence_words]
    return sentence_words

# return bag of words array: 0 or 1 for each word in the bag that exists in the sentence

def bow(sentence, words, show_details=True):
    # tokenize the pattern
    sentence_words = clean_up_sentence(sentence)
    # bag of words - matrix of N words, vocabulary matrix
    bag = [0]*len(words)  
    for s in sentence_words:
        for i,w in enumerate(words):
            if w == s: 
                # assign 1 if current word is in the vocabulary position
                bag[i] = 1
                if show_details:
                    print ("found in bag: %s" % w)
    return(np.array(bag))

def predict_class(sentence, model):
    # filter out predictions below a threshold
    p = bow(sentence, words,show_details=False)
    res = model.predict(np.array([p]))[0]
    ERROR_THRESHOLD = 0.25
    results = [[i,r] for i,r in enumerate(res) if r>ERROR_THRESHOLD]
    # sort by strength of probability
    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    for r in results:
        return_list.append({"intent": classes[r[0]], "probability": str(r[1])})
    return return_list

def getResponse(ints, intents_json):
    tag = ints[0]['intent']
    list_of_intents = intents_json['intents']
    for i in list_of_intents:
        if(i['tag']== tag):
            result = random.choice(i['responses'])
            break
    return result

@csrf_exempt
def get_response(request):
	response = {'status': None}
	if request.method == 'POST':
		data = json.loads(request.body)
		message = data['message']
		ints = predict_class(message, model)
		res = getResponse(ints, intents)
		response['message'] = {'text': res, 'user': False, 'chat_bot': True}
		response['status'] = 'ok'
	else:
	  response['error'] = 'no post data found'
	return HttpResponse(
	  json.dumps(response),
	   content_type="application/json"
	  )
def home(request, template_name="chathome.html"):
 context = {'title': 'Chatbot Version 1.0'}
 return render_to_response(template_name, context)