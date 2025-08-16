from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone

# Niveaux disponibles pour les utilisateurs
NIVEAU_CHOICES = (
    ('user-simple', 'Utilisateur Simple'),
    ('admin', 'Administrateur')
)

# Status disponibles pour les tâches
STATUS_CHOICES = (
    ('TO DO', 'À Faire'),
    ('EN COURS', 'En Cours'),
    ('TERMINÉ', 'Terminé')
)

# Niveaux d'importance
IMPORTANCE_CHOICES = (
    ('LOW', 'L'),
    ('MEDIUM', 'M'),
    ('HIGH', 'H')
)

class DoorManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('L\'email est obligatoire')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('niveau', 'admin')
        return self.create_user(email, password, **extra_fields)

class Door(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    niveau = models.CharField(max_length=20, choices=NIVEAU_CHOICES, default='user-simple')
    date_joined = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = DoorManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

class Task(models.Model):
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='TO DO')
    importance = models.CharField(
        max_length=20,
        choices=IMPORTANCE_CHOICES,
        default='MEDIUM',
        verbose_name='Importance'
    )
    assigne_a = models.ForeignKey(Door, on_delete=models.CASCADE, related_name='tasks_assigne')
    cree_par = models.ForeignKey(Door, on_delete=models.CASCADE, related_name='tasks_crees')
    date_creation = models.DateTimeField(auto_now_add=True)
    date_mise_a_jour = models.DateTimeField(auto_now=True)
    archived = models.BooleanField(default=False, verbose_name='Archivée')

    def __str__(self):
        return self.description[:50] + '...' if len(self.description) > 50 else self.description
