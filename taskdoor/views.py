from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django import forms
from django.template.defaultfilters import register
from django.http import JsonResponse

# Filtre personnalisé pour accéder aux éléments d'un dictionnaire
@register.filter
@user_passes_test(lambda u: u.niveau == 'admin')
def get_item(dictionary, key):
    return dictionary.get(key)

# Pour utiliser le filtre dans les templates
from django.template import Library
register = Library()

@register.filter
@user_passes_test(lambda u: u.niveau == 'admin')
def get_item(dictionary, key):
    return dictionary.get(key, '')

from .models import Task, Door, STATUS_CHOICES, IMPORTANCE_CHOICES
from .forms import LoginForm, TaskForm, TaskAdminForm, DoorCreationForm

def is_admin(user):
    return user.niveau == 'admin'

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                if user.niveau == 'admin':
                    return redirect('taskdoor:admin_dashboard')
                return redirect('taskdoor:user_dashboard')
        else:
            messages.error(request, 'Email ou mot de passe invalide')
    else:
        form = LoginForm()
    return render(request, 'taskdoor/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('taskdoor:login')

@login_required
@user_passes_test(lambda u: u.niveau == 'user-simple')
def user_dashboard(request):
    tasks = Task.objects.filter(assigne_a=request.user)
    return render(request, 'taskdoor/user_dashboard.html', {'tasks': tasks})

@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    if request.user.niveau != 'admin':
        return redirect('taskdoor:user_dashboard')

    # Récupérer tous les utilisateurs pour le filtre
    users = Door.objects.all()
    
    # Initialiser les filtres pour les tâches non archivées
    filter_kwargs = {'archived': False}
    
    # Filtrer par utilisateur si spécifié
    user_id = request.GET.get('user')
    if user_id:
        filter_kwargs['assigne_a__id'] = user_id
    
    # Récupérer toutes les tâches correspondant aux filtres
    all_tasks = Task.objects.filter(**filter_kwargs)
    
    # Grouper les tâches par statut
    tasks_by_status = {status[0]: [] for status in STATUS_CHOICES}
    for task in all_tasks:
        tasks_by_status[task.status].append(task)
    
    # Compter les tâches par statut
    status_counts = {status[0]: len(tasks) for status, tasks in tasks_by_status.items()}

    context = {
        'tasks_by_status': tasks_by_status,  # Tâches groupées par statut
        'tasks': all_tasks,  # Toutes les tâches (pour la rétrocompatibilité)
        'users': users,
        'STATUS_CHOICES': STATUS_CHOICES,
        'IMPORTANCE_CHOICES': IMPORTANCE_CHOICES,
        'status_counts': status_counts,
    }
    return render(request, 'taskdoor/kanban_admin.html', context)

@login_required
@user_passes_test(is_admin)
def edit_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    
    if request.method == 'POST':
        form = TaskAdminForm(request.POST, instance=task)
        if form.is_valid():
            task = form.save()
            return redirect('taskdoor:admin_dashboard')
    else:
        form = TaskAdminForm(instance=task)
    
    context = {
        'task': task,
        'form': form,
        'STATUS_CHOICES': STATUS_CHOICES,
        'IMPORTANCE_CHOICES': IMPORTANCE_CHOICES,
    }
    return render(request, 'taskdoor/edit_task.html', context)

@login_required
def create_user(request):
    if request.method == 'POST':
        form = DoorCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Utilisateur créé avec succès')
            return redirect('taskdoor:admin_dashboard')
    else:
        form = DoorCreationForm()
    return render(request, 'taskdoor/create_user.html', {'form': form})

@login_required
def create_task(request):
    if request.method == 'POST':
        if request.user.niveau == 'admin':
            form = TaskAdminForm(request.POST)
        else:
            form = TaskForm(request.POST)
            form.fields['assigne_a'].initial = request.user.id
            form.fields['assigne_a'].widget = forms.HiddenInput()
            form.fields['assigne_a'].required = False
        
        if form.is_valid():
            task = form.save(commit=False)
            task.cree_par = request.user
            if request.user.niveau != 'admin':
                task.assigne_a = request.user
            task.save()
            messages.success(request, 'Tâche créée avec succès')
            return redirect('taskdoor:user_dashboard' if request.user.niveau == 'user-simple' else 'taskdoor:admin_dashboard')
        else:
            messages.error(request, 'Veuillez corriger les erreurs dans le formulaire')
    else:
        if request.user.niveau == 'admin':
            form = TaskAdminForm()
        else:
            form = TaskForm()
            form.fields['assigne_a'].initial = request.user.id
            form.fields['assigne_a'].widget = forms.HiddenInput()
            form.fields['assigne_a'].required = False
    return render(request, 'taskdoor/create_task.html', {'form': form})

@login_required
def update_task_status(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    
    if request.method == 'POST':
        if request.user.niveau == 'admin' or task.assigne_a == request.user:
            status = request.POST.get('status')
            if status in [choice[0] for choice in STATUS_CHOICES]:
                task.status = status
                task.save()
                return JsonResponse({'success': True})
    return JsonResponse({'success': False})

@login_required
def update_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    
    if request.method == 'POST':
        if request.user.niveau == 'admin' or task.assigne_a == request.user:
            form = TaskForm(request.POST, instance=task)
            if form.is_valid():
                task = form.save(commit=False)
                task.save()
                return JsonResponse({'success': True})
    return JsonResponse({'success': False})

@login_required
def update_task_info(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    
    if request.method == 'POST':
        if request.user.niveau == 'admin' or task.assigne_a == request.user:
            form = TaskAdminForm(request.POST, instance=task)
            if form.is_valid():
                task = form.save()
                return redirect('taskdoor:admin_dashboard')
    return redirect('taskdoor:admin_dashboard')

@login_required
def delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    
    if request.method == 'POST':
        if request.user.niveau == 'admin' or task.assigne_a == request.user:
            task.delete()
            return JsonResponse({'success': True})
    return JsonResponse({'success': False})

@login_required
@user_passes_test(lambda u: u.niveau == 'admin')
def delete_task_admin(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    task.delete()
    return redirect('admin_dashboard')

@login_required
@user_passes_test(lambda u: u.niveau == 'admin')
def reassign_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    if request.method == 'POST':
        user_id = request.POST.get('user')
        if user_id:
            try:
                new_user = get_object_or_404(Door, id=user_id)
                task.assigne_a = new_user
                task.save()
                messages.success(request, f"La tâche a été réassignée à {new_user.email}")
                return redirect('admin_dashboard')
            except Door.DoesNotExist:
                messages.error(request, "Utilisateur invalide")
        else:
            messages.error(request, "Veuillez sélectionner un utilisateur")
    users = Door.objects.all()
    return render(request, 'taskdoor/reassign_task.html', {
        'task': task,
        'users': users
    })

@login_required
@user_passes_test(is_admin)
def archived_tasks(request):
    """View to display all archived tasks."""
    tasks = Task.objects.filter(archived=True).order_by('-date_mise_a_jour')
    users = Door.objects.all()
    
    # Filter by user if specified
    user_id = request.GET.get('user')
    if user_id:
        tasks = tasks.filter(assigne_a__id=user_id)
    
    context = {
        'tasks': tasks,
        'users': users,
        'STATUS_CHOICES': STATUS_CHOICES,
        'IMPORTANCE_CHOICES': IMPORTANCE_CHOICES,
        'is_archived_view': True,  # Flag to indicate this is the archived tasks view
    }
    return render(request, 'taskdoor/archived_tasks.html', context)

@login_required
@user_passes_test(is_admin)
def unarchive_task(request, task_id):
    """View to unarchive a task."""
    if request.method == 'POST':
        task = get_object_or_404(Task, id=task_id)
        task.archived = False
        task.save()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)

@login_required
@user_passes_test(is_admin)
def archive_task(request, task_id):
    """View to archive a task."""
    if request.method == 'POST':
        task = get_object_or_404(Task, id=task_id)
        task.archived = True
        task.save()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)

@login_required
@user_passes_test(is_admin)
def archive_all_done_tasks(request):
    # View to archive all tasks with status 'done'.
    if request.method == 'POST':
        tasks = Task.objects.filter(status='done', is_archived=False)
        count = tasks.count()
        tasks.update(is_archived=True)
        messages.success(request, f'{count} tâches terminées ont été archivées.')
        return redirect('taskdoor:archived_tasks')
    else:
        return redirect('taskdoor:admin_dashboard')

