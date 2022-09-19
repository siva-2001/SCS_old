from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from SCSapp.forms import SignUpUser
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth.forms import  AuthenticationForm

def signUpUserView(request):
    userAuth = request.user.is_authenticated
    form = SignUpUser()
    if request.method == 'GET':
        return render(request, 'signUpUser.html', {'form':form})
    else:
        if request.POST['password1'] == request.POST['password2'] and len(request.POST["email"]):
            try:

                user = User.objects.create_user(username=request.POST['username'], email=request.POST['email'],
                    first_name=request.POST['first_name'], last_name=request.POST['last_name'])
                user.set_password(request.POST['password1'])
                user.save()
                login(request, user)
                return redirect('homePage')
            except:
                return render(request, 'signUpUser.html', {'form':form, "userAuth":userAuth,
                    'error':'Имя пользователя занято. Выберите другое'})
        else:
            return render(request, 'signUpUser.html', {'form':form,
                'error':'Пароли не совпадают или не введён e-mail', "userAuth":userAuth})

def logInUserView(request):
    userAuth = request.user.is_authenticated
    if request.method == "GET":
        return render(request, 'logInUser.html', {'form':AuthenticationForm()})
    else:
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user is not None:
            login(request, user)
            return redirect('homePage')
        else:
            return render(request, 'logInUser.html', {"form":AuthenticationForm(), "userAuth":userAuth,
                                                      "error":'Данные введены неверно'})

@login_required
def logoutUser(request):
    logout(request)
    return redirect('homePage')