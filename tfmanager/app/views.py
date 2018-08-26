from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm


def index(request):
    return render(request, 'app/index.html')

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('index')
    else:
        form = UserCreationForm()
    context = {'form': form}
    return render(request, 'auth/register.html', context)

def auth_login(request):
    context = {}
    form = AuthenticationForm()
    context = {'form': form}
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('index')
        else:
            context['error'] = 'Invalid credentials'
            return render(request, "auth/login.html", context)
    else:
        return render(request, 'auth/login.html', context)

def auth_logout(request):
    if request.method == 'POST':
        logout(request)
        return redirect('login')
