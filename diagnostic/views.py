from django.shortcuts import render,redirect
from django.contrib import messages
from django.contrib.auth.models import User,auth
from .models import Diagnostic_test
import csv
import operator 
from django.db.models import F
import nltk
from nltk.stem import WordNetLemmatizer
lemmatizer = WordNetLemmatizer()
import pickle
import numpy as np
from diagnostic.views import *
import h5py

import os
THIS_FOLDER = os.getcwd()
my_file = os.path.join(THIS_FOLDER, 'chatbot_model.h5')
my_file1 = os.path.join(THIS_FOLDER, 'words.pkl')
my_file2 = os.path.join(THIS_FOLDER, 'classes.pkl')
my_file3 = os.path.join(THIS_FOLDER, 'intents.json')




from keras.models import load_model
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

def chatbot_response(msg):
    ints = predict_class(msg, model)
    res = getResponse(ints, intents)
    return res


#Creating GUI with tkinter
import tkinter
from tkinter import *


def send():
    msg = EntryBox.get("1.0",'end-1c').strip()
    EntryBox.delete("0.0",END)

    if msg != '':
        ChatLog.config(state=NORMAL)
        ChatLog.insert(END, "You: " + msg + '\n\n')
        ChatLog.config(foreground="#442265", font=("Calibre", 12 ))
    
        res = chatbot_response(msg)
        ChatLog.insert(END, "Bot: " + res + '\n\n')
            
        ChatLog.config(state=DISABLED)
        ChatLog.yview(END)
 

previous=0
add=1
flag=0
score2=0

# Create your views here.
def help(request):
    base = Tk()
    base.title("ChatBot")
    base.geometry("400x500")
    base.resizable(width=TRUE, height=TRUE)

    #Create Chat window
    ChatLog = Text(base, bd=0, bg="white", height="8", width="50", font="Calibre",)

    ChatLog.config(state=DISABLED)

    #Bind scrollbar to Chat window
    scrollbar = Scrollbar(base, command=ChatLog.yview, cursor="heart")
    ChatLog['yscrollcommand'] = scrollbar.set

    #Create Button to send message
    SendButton = Button(base, font=("Calibre",12), text="Send", width="12", height=5,
                        bd=0, bg="#32de97", activebackground="#3c9d9b",fg='#ffffff',
                        command= send )

    #Create the box to enter message
    EntryBox = Text(base, bd=0, bg="white",width="29", height="5", font="Calibre")
    #EntryBox.bind("<Return>", send)


    #Place all components on the screen
    scrollbar.place(x=376,y=6, height=386)
    ChatLog.place(x=6,y=6, height=386, width=370)
    EntryBox.place(x=128, y=401, height=90, width=265)
    SendButton.place(x=6, y=401, height=90)

    base.mainloop()
    return redirect("dynamic_test2")

def dynamic_test2(request):
   global previous
   global add
   global flag
   global score2
   score2=0
   flag=0
   previous=0
   add=1
   val=Diagnostic_test.objects.get(question_no=1)
   return render(request,'ad_test.html',{'question':val})
def dynamic_test(request):
    
    id_here=int(request.POST['id'])
    ans=request.POST[str(id_here)] 
    global previous
    global add
    global flag
    global score2
    score2+=id_here
    if id_here>=12:
        return render(request,'results.html',{'Score':score2})

        

    val=Diagnostic_test.objects.get(question_no=id_here)

    if ans==val.answer:
        previous=id_here
        add=add
        id_here+=add
        add+=1
        val=Diagnostic_test.objects.get(question_no=id_here)
        return render(request,'ad_test.html',{'question':val})

    else:
        flag += 1
        if flag==0:
            id_here=previous+1
        else:
            id_here+=1
        val=Diagnostic_test.objects.get(question_no=id_here)
        return render(request,'ad_test.html',{'question':val})


    
   
   
        
def score(request):
    all_ques = Diagnostic_test.objects.all()
    for ques in all_ques:
        questions=request.POST[ques.statement]
        if ques.answer == questions: 
            print(questions)   
            Diagnostic_test.objects.filter(id=ques.id).update(correct=F('correct')+1)

   
    return render(request,'success.html')

def delete(request):
 # if Diagnostic_test.objects.all().get() is not None:
     Diagnostic_test.objects.all().delete()
     return render(request,'success.html')  

def attend(request):
    all_ques = Diagnostic_test.objects.all()
    all_ques = sorted(all_ques,key=operator.attrgetter('correct'))
    i=0
    all_ques.reverse()
    for ques in all_ques:
        print(i,ques.correct)
        i+=1
    return render(request,'attend_test.html',{'Questions': all_ques})
def test(request):
    return render(request,'test.html')

def upload(request):
    
    question1=request.POST['question']
    choice1=request.POST['choice1']
    choice2=request.POST['choice2']
    choice3=request.POST['choice3']
    choice4=request.POST['choice4']
    answer=request.POST['answer']
    dv=0
    question_save=Diagnostic_test(question_no=dv,correct=0,probability=0,statement=question1,choice1=choice1,choice2=choice2,choice3=choice3,choice4=choice4,answer=answer,time="1999-02-02")
    question_save.save()

    return render(request,'test.html')

def store(request):
    filename=request.POST['myfile']
    l = []

    with open(filename) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            d = {"question_no":0,"question":"","choice1":"","choice2":"","choice3":"","choice4":"","answer":""}
            if line_count == 0:
                print(f'Column names are {", ".join(row)}')
                line_count += 1
            else:
                d["question_no"] = row[0]
                d["question"] = row[1]
                d["choice1"] = row[2]
                d["choice2"] = row[3]
                d["choice3"] = row[4]
                d["choice4"] = row[5]
                d["answer"] = row[6]
                l.append(d)
                line_count += 1

    for x in l:
        question_save=Diagnostic_test(question_no=x["question_no"],correct=0,probability=0,statement=x["question"],choice1=x["choice1"],choice2=x["choice2"],choice3=x["choice3"],choice4=x["choice4"],answer=x["answer"],time="1999-02-02")
        question_save.save()

    return render(request,'success.html')   

def upload2(request):

    l = []

    with open('forloop.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            d = {"question_no":0,"question":"","choice1":"","choice2":"","choice3":"","choice4":"","answer":""}
            if line_count == 0:
                print(f'Column names are {", ".join(row)}')
                line_count += 1
            else:
                d["question_no"] = row[0]
                d["question"] = row[1]
                d["choice1"] = row[2]
                d["choice2"] = row[3]
                d["choice3"] = row[4]
                d["choice4"] = row[5]
                d["answer"] = row[6]
                l.append(d)
                line_count += 1

    for x in l:
        question_save=Diagnostic_test(question_no=x["question_no"],correct=0,probability=0,statement=x["question"],choice1=x["choice1"],choice2=x["choice2"],choice3=x["choice3"],choice4=x["choice4"],answer=x["answer"],time="1999-02-02")
        question_save.save()

    return render(request,'success.html')   

def upload3(request):
    return render(request,'upload3.html')






