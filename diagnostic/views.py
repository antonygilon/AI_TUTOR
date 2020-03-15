from django.shortcuts import render,redirect
from django.contrib import messages
from django.contrib.auth.models import User,auth
from .models import Diagnostic_test
import csv
import operator 
from django.db.models import F
from diagnostic.views import *
import h5py





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






