from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class ProfilUtilisateur(models.Model):
    ROLE_CHOICES = [
        ('etudiant', 'Étudiant'),
       ('vendeur', 'Caissier/Vendeur'), 
        ('controleur', 'Contrôleur'),
        ('admin', 'Administrateur'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='etudiant')

    def __str__(self):
        return f"{self.user.username} - {self.role}"

class Etudiant(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    numero_cni = models.CharField(max_length=50, unique=True, verbose_name="CNI")
    numero_ce = models.CharField(max_length=50, unique=True, verbose_name="Carte étudiant")
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    sexe = models.CharField(max_length=1, choices=[('M','Masculin'),('F','Féminin')])
    date_naissance = models.DateField(null=True, blank=True)
    niveau = models.CharField(max_length=50)
    filiere = models.CharField(max_length=100)
    telephone = models.CharField(max_length=20)
    email = models.EmailField()
    wallet = models.IntegerField(default=0)
    tickets_petit_dej = models.IntegerField(default=0)
    tickets_repas = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.prenom} {self.nom} ({self.numero_ce})"

class Personnel(models.Model):
    ROLE_CHOICES = [
        ('vendeur', 'Caissier/Vendeur'),
        ('controleur', 'Contrôleur'),
        ('admin', 'Administrateur'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    sexe = models.CharField(max_length=1, choices=[('M','M'),('F','F')])
    telephone = models.CharField(max_length=20)
    email = models.EmailField()
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    est_actif = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.prenom} {self.nom} ({self.role})"
    
class Menu(models.Model):
    TYPE_CHOICES = [
        ('dejeuner', 'Déjeuner (11h30 – 14h)'),
        ('dessert_dejeuner', 'Dessert Déjeuner'),
        ('diner', 'Dîner (18h – 20h)'),
        ('dessert_diner', 'Dessert Dîner'),
    ]
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    titre = models.CharField(max_length=100)
    description = models.TextField()
    prix = models.IntegerField(default=200)
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('en_cours', 'En cours de préparation'),
        ('pret', 'Prêt à servir'),
        ('termine', 'Service terminé'),
    ]
    image = models.ImageField(upload_to='menus/', null=True, blank=True)
    actif = models.BooleanField(default=True)
    ordre = models.IntegerField(default=0)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente')

    class Meta:
        ordering = ['type', 'ordre']
    
class Achat(models.Model):
    TYPE_TICKET = [('petit_dej', 'Petit déjeuner'), ('repas', 'Repas')]
    etudiant = models.ForeignKey(Etudiant, on_delete=models.CASCADE, related_name='achats')
    type_ticket = models.CharField(max_length=20, choices=TYPE_TICKET)
    quantite = models.PositiveIntegerField(default=1)
    prix_total = models.PositiveIntegerField()
    date = models.DateTimeField(auto_now_add=True)
    paye_par_wave = models.BooleanField(default=True)

class Depense(models.Model):
    etudiant = models.ForeignKey(Etudiant, on_delete=models.CASCADE, related_name='depenses')
    type_ticket = models.CharField(max_length=20, choices=[('petit_dej','Petit déj'),('repas','Repas')])
    date = models.DateTimeField(auto_now_add=True)
    controleur = models.ForeignKey(Personnel, on_delete=models.SET_NULL, null=True, limit_choices_to={'role':'controleur'})

class Vente(models.Model):
    vendeur = models.ForeignKey(Personnel, on_delete=models.CASCADE, limit_choices_to={'role':'vendeur'})
    etudiant = models.ForeignKey(Etudiant, on_delete=models.CASCADE)
    type_ticket = models.CharField(max_length=20, choices=[('petit_dej','Petit déj'),('repas','Repas')])
    quantite = models.PositiveIntegerField()
    montant = models.PositiveIntegerField()
    date = models.DateTimeField(auto_now_add=True)

class QRCode(models.Model):
    token = models.CharField(max_length=100, unique=True)
    etudiant = models.ForeignKey(Etudiant, on_delete=models.CASCADE)
    type_ticket = models.CharField(max_length=20, choices=[('petit_dej','Petit déj'),('repas','Repas')])
    created_at = models.DateTimeField(auto_now_add=True)
    expire_at = models.DateTimeField()
    utilise = models.BooleanField(default=False)
    est_transfere = models.BooleanField(default=False)
    transfere_depuis = models.ForeignKey(
        Etudiant, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='tickets_donnes'
    )