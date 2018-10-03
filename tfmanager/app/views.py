from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from app.repo import FolderRepo, FileRepo, FileHistoryRepo


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
        context['id'] = folder_info['id']
        context['name'] = folder_info['name']
        context['parent_id'] = folder_info['parent_id']
        context['files'] = files_info
        context['folders'] = child_folders_info
    return render(request, 'app/folder.html', context)


def file(request, file_id):
    context = {}
    current_user = request.user
    if current_user:
        file_info = FileRepo.get_file(current_user.id, file_id)
        if not file_info:
            return redirect('index')
        context['id'] = file_info['id']
        context['name'] = file_info['name']
        context['content'] = file_info['content_text']
    return render(request, 'app/file.html', context)


def file_edit(request, file_id):
    context = {}
    current_user = request.user

    # TODO: Do this consistently across all of the views
    if not current_user:
        return render('login')

    # Save the file changes and get the updated file's information
    if request.method == "POST":
        new_content = request.POST.get('content')
        file_info = FileRepo.publish_new_version(
            current_user.id, file_id, new_content)
        err_cond = "File publish failed"
    # Get the file the user requested for edit
    else:
        file_info = FileRepo.get_file(current_user.id, file_id)
        err_cond = "File does not exist"

    # No file information to present...deal with the error
    if not file_info:
        context['error'] = err_cond
    # File contents for user to proceed with editing
    else:
        context['id'] = file_info['id']
        context['name'] = file_info['name']
        context['content'] = file_info['content_text']

    return render(request, 'app/file_edit.html', context)


def folder_create(request):
    current_user = request.user

    if not current_user:
        return render('login')

    if request.method == 'POST':
        folder_name = request.POST.get('folder_name')
        parent_id = request.POST.get('parent_id', None)
        new_folder = FolderRepo.create_folder(
            current_user.id, folder_name, parent_id)
        if not new_folder:
            response = render(request, 'app/folder_create.html',
                              {'error': 'Unable to create new folder'})
            response.status_code = 400
        else:
            response = redirect('folder', new_folder['id'])
        return response
    else:
        parent_id = request.GET.get('parent_id', None)
        return render(request, 'app/folder_create.html', {'parent_id': parent_id})


def file_ver(request, file_id, version_num):
    context = {}

    current_user = request.user
    if not current_user:
        return render('login')

    file_info = FileRepo.get_file_by_version(
        current_user.id, file_id, version_num)
    if not file_info:
        return redirect('index')

    context['id'] = file_info['id']
    context['name'] = file_info['name']
    context['content'] = file_info['content_text']
    return render(request, 'app/file.html', context)


def file_hist(request, file_id):
    context = {}

    current_user = request.user
    if not current_user:
        return render('login')

    history = FileHistoryRepo.get_history(current_user.id, file_id)

    if not history:
        return redirect('index')

    context['id'] = history['id']
    context['name'] = history['name']
    context['histories'] = history['histories']

    return render(request, 'app/file_history.html', context)


def file_create(request):
    current_user = request.user

    if not current_user:
        return render('login')

    if request.method == 'POST':
        # TODO
        pass
    else:
        parent_id = request.GET.get('parent_id', None)
        return render(request, 'app/file_create.html', {'parent_id': parent_id})
