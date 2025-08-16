from django.contrib import admin
from .models import Door, Task

@admin.register(Door)
class DoorAdmin(admin.ModelAdmin):
    list_display = ('email', 'niveau', 'date_joined', 'is_active')
    list_filter = ('niveau', 'is_active')
    search_fields = ('email',)
    ordering = ('-date_joined',)

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('truncated_description', 'status', 'assigne_a', 'cree_par', 'date_creation')
    list_filter = ('status', 'assigne_a', 'cree_par')
    search_fields = ('description', 'assigne_a__email', 'cree_par__email')
    ordering = ('-date_creation',)
    readonly_fields = ('date_creation', 'date_mise_a_jour')
    
    # Add fields that can be edited in the list view
    list_editable = ('status', 'assigne_a')
    
    def truncated_description(self, obj):
        return obj.description[:50] + '...' if len(obj.description) > 50 else obj.description
    truncated_description.short_description = 'Description'
