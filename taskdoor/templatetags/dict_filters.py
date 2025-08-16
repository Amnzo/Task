from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def filter_by_status(tasks, status):
    """Filtre une liste de tâches par statut."""
    return [task for task in tasks if task.status == status]
