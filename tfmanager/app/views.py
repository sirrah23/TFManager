from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from app.repo import FolderRepo, FileRepo


def index(request):
    context = {}
    current_user = request.user
    if current_user:
        context['folders'] = FolderRepo.get_all_folder_for_user_with_parent(
            current_user.id, parent_id=None)
    return render(request, 'app/index.html', context)


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


def folder(request, folder_id):
    context = {}
    current_user = request.user
    if current_user:
        folder_info = FolderRepo.get_folder(current_user.id, folder_id)
        child_folders_info = FolderRepo.get_all_folder_for_user_with_parent(
            current_user.id, folder_id)
        files_info = FileRepo.get_files_within_folder(
            current_user.id, folder_id)
        if not folder_info:
            return redirect('index')
        context['name'] = folder_info['name']
        context['parent_id'] = folder_info['parent_id']
        context['files'] = files_info
        context['folders'] = child_folders_info
    return render(request, 'app/folder.html', context)
