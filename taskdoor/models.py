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
    ('LOW', 'Faible'),
    ('MEDIUM', 'Moyen'),
    ('HIGH', 'Élevé')
)

class DoorManager(BaseUserManager):
    def create_user(self, nom, email=None, password=None, **extra_fields):
        if not nom:
            raise ValueError('Le nom est obligatoire')
        user = self.model(nom=nom, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, nom, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('niveau', 'admin')
        return self.create_user(nom, email, password, **extra_fields)

class Door(AbstractBaseUser, PermissionsMixin):
    nom = models.CharField('Nom', max_length=100, unique=True)
    email = models.EmailField('Email', unique=True, blank=True, null=True)  # Gardé pour la rétrocompatibilité
    niveau = models.CharField('Niveau', max_length=20, choices=NIVEAU_CHOICES, default='user-simple')
    date_joined = models.DateTimeField('Date d\'inscription', auto_now_add=True)
    is_active = models.BooleanField('Actif', default=True)
    is_staff = models.BooleanField('Staff', default=False)

    objects = DoorManager()

    USERNAME_FIELD = 'nom'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = 'Utilisateur'
        verbose_name_plural = 'Utilisateurs'

    def __str__(self):
        return self.nom

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
