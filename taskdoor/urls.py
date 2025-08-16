from django.urls import path
from . import views
from django.views.generic import RedirectView

app_name = 'taskdoor'

urlpatterns = [
    path('', RedirectView.as_view(pattern_name='taskdoor:login'), name='index'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('user/dashboard/', views.user_dashboard, name='user_dashboard'),
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),
    path('user/create/', views.create_user, name='create_user'),
    path('task/create/', views.create_task, name='create_task'),
    path('task/<int:task_id>/status/', views.update_task_status, name='update_task_status'),
    path('task/<int:task_id>/update/', views.update_task, name='update_task'),
    path('task/<int:task_id>/info/update/', views.update_task_info, name='update_task_info'),
    path('task/<int:task_id>/delete/', views.delete_task, name='delete_task'),
    path('task/<int:task_id>/delete_admin/', views.delete_task_admin, name='delete_task_admin'),
    path('task/<int:task_id>/reassign/', views.reassign_task, name='reassign_task'),
    path('task/<int:task_id>/edit/', views.edit_task, name='edit_task'),
    path('tasks/archived/', views.archived_tasks, name='archived_tasks'),
    path('task/<int:task_id>/unarchive/', views.unarchive_task, name='unarchive_task'),
    path('task/<int:task_id>/archive/', views.archive_task, name='archive_task'),
    path('tasks/archive-all-done/', views.archive_all_done_tasks, name='archive_all_done_tasks'),
]
