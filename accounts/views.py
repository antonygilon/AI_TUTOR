from django.shortcuts import render,redirect
from django.contrib import messages
from django.contrib.auth.models import User,auth
from tutor_v2.models import Student

# Create your views here.
def home2(request):
    return render(request,'home2.html')

def register(request):
    if request.method=='POST':
        email=request.POST['email']
        password=request.POST['psw']
        username=request.POST['username']
        if User.objects.filter(username=username).exists():
            messages.info(request,"username taken")
            return redirect("register")
        elif User.objects.filter(email=email).exists():
            messages.info(request,"email taken")
            return redirect("register")
        else:   
            user =User.objects.create_user(email=email,password=password,username=username)
            student = Student(user =user)
        
            user.save()
            student.save()
            print("user created")
        return redirect('/')

    else:
        return render(request,'register.html')

def login(request):
    if request.method=='POST':
        username=request.POST['uname']
        password=request.POST['psw']

        user=auth.authenticate(username=username,password=password)

        if user is not None:
            auth.login(request,user)
            student = Student.objects.get(user = user)
            request.session['student'] = student.id
            return redirect("/")
        else:
            messages.info(request,"wrong credentials")
            return redirect("login")


    else:
       return render(request,'login.html')

def logout(request):
    auth.logout(request)
    return redirect('/')

