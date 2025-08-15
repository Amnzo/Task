from django.apps import AppConfig

class TaskdoorConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'taskdoor'

    def ready(self):
        import taskdoor.templatetags.dict_filters
