from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

class SimplePasswordValidator:
    def validate(self, password, user=None):
        # Pas de validation, accepte tout
        return

    def get_help_text(self):
        return ""

def get_password_validators():
    return [SimplePasswordValidator()]
