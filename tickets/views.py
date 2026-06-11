import uuid
import io
import qrcode
from datetime import timedelta, datetime, time
from django.http import HttpResponse
from django.utils import timezone
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Etudiant, Personnel, Achat, Depense, Vente, QRCode, ProfilUtilisateur, Menu
from .forms import InscriptionEtudiantForm, RechargeForm, AchatTicketForm, VenteTicketForm, AjoutPersonnelForm
from .decorators import role_required

# --- Pages publiques ---
def accueil(request):
    menus_dejeuner = Menu.objects.filter(type='dejeuner', actif=True).order_by('ordre')
    menus_dessert_dejeuner = Menu.objects.filter(type='dessert_dejeuner', actif=True).order_by('ordre')
    menus_diner = Menu.objects.filter(type='diner', actif=True).order_by('ordre')
    menus_dessert_diner = Menu.objects.filter(type='dessert_diner', actif=True).order_by('ordre')
    return render(request, 'accueil.html', {
        'menus_dejeuner': menus_dejeuner,
        'menus_dessert_dejeuner': menus_dessert_dejeuner,
        'menus_diner': menus_diner,
        'menus_dessert_diner': menus_dessert_diner,
    })

def connexion(request):
    """Page de connexion (GET) et traitement (POST)"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('redirection')
        else:
            messages.error(request, "Identifiants invalides")
            return render(request, 'connexion.html')
    return render(request, 'connexion.html')

def inscription(request):
    """Page d'inscription (GET) et traitement (POST)"""
    if request.method == 'POST':
        form = InscriptionEtudiantForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Inscription réussie. Connectez-vous.")
            return redirect('connexion')
        else:
            return render(request, 'inscription.html', {'form': form})
    return render(request, 'inscription.html')

def redirection(request):
    if not request.user.is_authenticated:
        return redirect('accueil')

    # Vérifier ou créer le profil utilisateur
    try:
        profile = request.user.profilutilisateur
        role = profile.role
    except ProfilUtilisateur.DoesNotExist:
        if hasattr(request.user, 'etudiant'):
            role = 'etudiant'
        elif hasattr(request.user, 'personnel'):
            role = request.user.personnel.role
        else:
            role = 'admin'
        ProfilUtilisateur.objects.create(user=request.user, role=role)
        messages.info(request, f"Profil créé avec le rôle {role}. Veuillez vous reconnecter.")
        logout(request)
        return redirect('connexion')

    if role == 'etudiant':
        return redirect('portail_etudiant')
    elif role == 'vendeur':
        return redirect('portail_caissier')
    elif role == 'controleur':
        return redirect('portail_controleur')
    elif role == 'admin':
        return redirect('portail_admin')
    else:
        messages.error(request, f"Rôle '{role}' non reconnu.")
        return redirect('accueil')

def deconnexion(request):
    logout(request)
    return redirect('accueil')

def acces_refuse(request):
    return render(request, 'acces_refuse.html')

# --- Portail étudiant ---
@login_required
@role_required(['etudiant'])
def portail_etudiant(request):
    etudiant = request.user.etudiant
    achats = etudiant.achats.all().order_by('-date')
    mes_tickets = QRCode.objects.filter(etudiant=etudiant, utilise=False, expire_at__gt=timezone.now()).order_by('created_at')
    form_achat = AchatTicketForm()
    form_recharge = RechargeForm()
    menus_dejeuner = Menu.objects.filter(type='dejeuner', actif=True).order_by('ordre')
    menus_dessert_dejeuner = Menu.objects.filter(type='dessert_dejeuner', actif=True).order_by('ordre')
    menus_diner = Menu.objects.filter(type='diner', actif=True).order_by('ordre')
    menus_dessert_diner = Menu.objects.filter(type='dessert_diner', actif=True).order_by('ordre')
    return render(request, 'etudiant.html', {
        'etudiant': etudiant, 'achats': achats,
        'mes_tickets': mes_tickets, 'form_achat': form_achat, 'form_recharge': form_recharge,
        'menus_dejeuner': menus_dejeuner, 'menus_dessert_dejeuner': menus_dessert_dejeuner,
        'menus_diner': menus_diner, 'menus_dessert_diner': menus_dessert_diner,
    })

@login_required
@role_required(['etudiant'])
def recharger_wallet(request):
    if request.method == 'POST':
        form = RechargeForm(request.POST)
        if form.is_valid():
            montant = form.cleaned_data['montant']
            etudiant = request.user.etudiant
            etudiant.wallet += montant
            etudiant.save()
            messages.success(request, f"Rechargement de {montant} FCFA effectué.")
        else:
            messages.error(request, "Montant invalide.")
    return redirect('portail_etudiant')

from .models import Menu
from django.shortcuts import get_object_or_404

@login_required
@role_required(['admin'])
def gestion_menus(request):
    menus = Menu.objects.all()
    return render(request, 'gestion_menus.html', {'menus': menus})

@login_required
@role_required(['admin'])
def ajouter_menu(request):
    if request.method == 'POST':
        type_menu = request.POST.get('type')
        titre = request.POST.get('titre')
        description = request.POST.get('description')
        prix = request.POST.get('prix')
        image = request.FILES.get('image')   # ← récupération du fichier
        actif = request.POST.get('actif') == 'on'
        ordre = request.POST.get('ordre', 0)
        Menu.objects.create(
            type=type_menu,
            titre=titre,
            description=description,
            prix=prix or 200,
            image=image,
            actif=actif,
            ordre=ordre
        )
        messages.success(request, "Menu ajouté avec succès.")
        return redirect('gestion_menus')
    return render(request, 'ajouter_menu.html')

@login_required
@role_required(['admin'])
def modifier_menu(request, id):
    menu = get_object_or_404(Menu, id=id)
    if request.method == 'POST':
        menu.type = request.POST.get('type')
        menu.titre = request.POST.get('titre')
        menu.description = request.POST.get('description')
        menu.prix = request.POST.get('prix') or 200
        if request.FILES.get('image'):
            menu.image = request.FILES['image']
        menu.actif = request.POST.get('actif') == 'on'
        menu.ordre = request.POST.get('ordre', 0)
        menu.save()
        messages.success(request, "Menu modifié.")
        return redirect('gestion_menus')
    return render(request, 'modifier_menu.html', {'menu': menu})

@login_required
@role_required(['admin'])
def supprimer_menu(request, id):
    menu = get_object_or_404(Menu, id=id)
    if request.method == 'POST':
        menu.delete()
        messages.success(request, "Menu supprimé.")
        return redirect('gestion_menus')
    return render(request, 'confirmer_suppression.html', {'menu': menu})

@login_required
@role_required(['etudiant'])
def acheter_ticket(request):
    if request.method == 'POST':
        form = AchatTicketForm(request.POST)
        if form.is_valid():
            quantite = form.cleaned_data['quantite']
            etudiant = request.user.etudiant
            total = quantite * 200
            if etudiant.wallet >= total:
                etudiant.wallet -= total
                etudiant.tickets_repas += quantite
                etudiant.save()
                Achat.objects.create(
                    etudiant=etudiant, type_ticket='repas',
                    quantite=quantite, prix_total=total, paye_par_wave=True
                )
                expire_at = timezone.now() + timedelta(days=30)
                for _ in range(quantite):
                    QRCode.objects.create(
                        token=str(uuid.uuid4()), etudiant=etudiant,
                        type_ticket='repas', expire_at=expire_at
                    )
                messages.success(request, f"{quantite} ticket(s) acheté(s) — vos QR codes sont prêts.")
            else:
                messages.error(request, "Solde insuffisant.")
        else:
            messages.error(request, "Formulaire invalide.")
    return redirect('portail_etudiant')

REPAS_SLOTS = {
    'dejeuner': (time(11, 30), time(14, 0), 'déjeuner'),
    'diner':    (time(18, 0),  time(20, 0), 'dîner'),
}

@login_required
@role_required(['etudiant'])
def generer_qr(request):
    if request.method == 'POST':
        slot = request.POST.get('slot')          # 'dejeuner' | 'diner' | absent pour petit_dej
        type_ticket = request.POST.get('type_ticket', 'repas')
        etudiant = request.user.etudiant

        if type_ticket == 'repas':
            if slot not in REPAS_SLOTS:
                messages.error(request, "Créneau invalide.")
                return redirect('portail_etudiant')
            if etudiant.tickets_repas <= 0:
                messages.error(request, "Vous n'avez plus de tickets repas.")
                return redirect('portail_etudiant')

            ouverture, fermeture, label = REPAS_SLOTS[slot]
            now_local = timezone.localtime(timezone.now())
            today = now_local.date()
            expire_at = timezone.make_aware(datetime.combine(today, fermeture))

            deja_actif = QRCode.objects.filter(
                etudiant=etudiant, type_ticket='repas',
                utilise=False, expire_at=expire_at
            ).exists()
            if deja_actif:
                messages.warning(request, f"Vous avez déjà un QR actif pour le {label}.")
                return redirect('portail_etudiant')

            # Contrainte d'heure désactivée en mode test
            # if now_local.time() >= fermeture:
            #     messages.error(request, f"Le service {label} est terminé pour aujourd'hui.")
            #     return redirect('portail_etudiant')

            QRCode.objects.create(token=str(uuid.uuid4()), etudiant=etudiant,
                                  type_ticket='repas', expire_at=expire_at)
            messages.success(request, f"QR {label} généré — valable jusqu'à {fermeture.strftime('%Hh%M')}.")

        else:
            messages.error(request, "Type de ticket invalide.")

    return redirect('portail_etudiant')

# --- Portail caissier ---
@login_required
@role_required(['vendeur'])
def portail_caissier(request):
    personnel = request.user.personnel
    etudiants = Etudiant.objects.all()

    achats_ligne = Achat.objects.filter(paye_par_wave=True)
    nb_tickets_ligne = achats_ligne.aggregate(t=Sum('quantite'))['t'] or 0
    montant_ligne = achats_ligne.aggregate(t=Sum('prix_total'))['t'] or 0

    tous_achats = Achat.objects.all()
    nb_tickets_total = tous_achats.aggregate(t=Sum('quantite'))['t'] or 0
    montant_total = tous_achats.aggregate(t=Sum('prix_total'))['t'] or 0

    par_mois = (
        Achat.objects
        .annotate(mois=TruncMonth('date'))
        .values('mois')
        .annotate(nb=Sum('quantite'), montant=Sum('prix_total'))
        .order_by('-mois')[:6]
    )

    return render(request, 'caissier.html', {
        'personnel': personnel,
        'etudiants': etudiants,
        'nb_tickets_ligne': nb_tickets_ligne,
        'montant_ligne': montant_ligne,
        'nb_tickets_total': nb_tickets_total,
        'montant_total': montant_total,
        'par_mois': par_mois,
    })

@login_required
@role_required(['vendeur'])
def vendre_ticket(request):
    if request.method == 'POST':
        form = VenteTicketForm(request.POST)
        if form.is_valid():
            etudiant = form.cleaned_data['etudiant']
            quantite = form.cleaned_data['quantite']
            montant = quantite * 200
            etudiant.tickets_repas += quantite
            etudiant.save()
            Vente.objects.create(vendeur=request.user.personnel, etudiant=etudiant,
                                 type_ticket='repas', quantite=quantite, montant=montant)
            Achat.objects.create(etudiant=etudiant, type_ticket='repas',
                                 quantite=quantite, prix_total=montant, paye_par_wave=False)
            expire_at = timezone.now() + timedelta(days=30)
            for _ in range(quantite):
                QRCode.objects.create(
                    token=str(uuid.uuid4()), etudiant=etudiant,
                    type_ticket='repas', expire_at=expire_at
                )
            messages.success(request, f"Vente de {quantite} ticket(s) effectuée.")
        else:
            messages.error(request, "Erreur formulaire.")
    return redirect('portail_caissier')

@login_required
@role_required(['vendeur'])
def ajouter_etudiant(request):
    if request.method == 'POST':
        form = InscriptionEtudiantForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Étudiant ajouté.")
        else:
            messages.error(request, "Erreur formulaire.")
    return redirect('portail_caissier')

# --- Portail contrôleur ---
@login_required
@role_required(['controleur'])
def portail_controleur(request):
    personnel = request.user.personnel
    depenses = Depense.objects.filter(controleur=personnel).order_by('-date')
    etudiants = Etudiant.objects.all()
    qr_actifs = QRCode.objects.filter(utilise=False, expire_at__gt=timezone.now()).select_related('etudiant')
    today = timezone.now().date()
    stats = {
        'total': Depense.objects.filter(controleur=personnel, date__date=today).count(),
    }
    return render(request, 'controleur.html', {
        'personnel': personnel, 'depenses': depenses, 'etudiants': etudiants,
        'qr_actifs': qr_actifs, 'stats': stats
    })

@login_required
@role_required(['controleur'])
def valider_qr(request):
    if request.method == 'POST':
        token = request.POST.get('token')
        try:
            qr = QRCode.objects.get(token=token, utilise=False, expire_at__gt=timezone.now())
            qr.utilise = True
            qr.save()
            etudiant = qr.etudiant
            if not qr.est_transfere:
                if etudiant.tickets_repas <= 0:
                    messages.error(request, "Plus de tickets.")
                    return redirect('portail_controleur')
                etudiant.tickets_repas -= 1
                etudiant.save()
            Depense.objects.create(etudiant=etudiant, type_ticket='repas', controleur=request.user.personnel)
            if qr.transfere_depuis:
                messages.success(request, f"Accès autorisé — {etudiant.prenom} {etudiant.nom} (ticket reçu de {qr.transfere_depuis.prenom} {qr.transfere_depuis.nom})")
            else:
                messages.success(request, f"Accès autorisé pour {etudiant.prenom} {etudiant.nom}")
        except QRCode.DoesNotExist:
            messages.error(request, "QR invalide ou expiré.")
    return redirect('portail_controleur')

@login_required
@role_required(['controleur'])
def debit_manuel(request):
    if request.method == 'POST':
        etudiant_id = request.POST.get('etudiant_id')
        etudiant = get_object_or_404(Etudiant, id=etudiant_id)
        qr = QRCode.objects.filter(etudiant=etudiant, utilise=False, expire_at__gt=timezone.now()).order_by('created_at').first()
        if not qr:
            messages.error(request, f"{etudiant.prenom} {etudiant.nom} n'a plus de tickets.")
            return redirect('portail_controleur')
        qr.utilise = True
        qr.save()
        etudiant.tickets_repas = max(0, etudiant.tickets_repas - 1)
        etudiant.save()
        Depense.objects.create(etudiant=etudiant, type_ticket='repas', controleur=request.user.personnel)
        messages.success(request, f"Débit manuel pour {etudiant.prenom} {etudiant.nom}")
    return redirect('portail_controleur')

# --- Portail administrateur ---
@login_required
@role_required(['admin'])
def portail_admin(request):
    personnels = Personnel.objects.all()

    achats_ligne = Achat.objects.filter(paye_par_wave=True)
    nb_tickets_ligne = achats_ligne.aggregate(t=Sum('quantite'))['t'] or 0
    montant_ligne = achats_ligne.aggregate(t=Sum('prix_total'))['t'] or 0
    tous_achats = Achat.objects.all()
    nb_tickets_total = tous_achats.aggregate(t=Sum('quantite'))['t'] or 0
    montant_total = tous_achats.aggregate(t=Sum('prix_total'))['t'] or 0
    par_mois = (
        Achat.objects
        .annotate(mois=TruncMonth('date'))
        .values('mois')
        .annotate(nb=Sum('quantite'), montant=Sum('prix_total'))
        .order_by('-mois')[:6]
    )

    stats = {
        'nb_etudiants': Etudiant.objects.count(),
        'nb_passages': Depense.objects.count(),
    }
    form_personnel = AjoutPersonnelForm()
    return render(request, 'admin.html', {
        'personnels': personnels,
        'stats': stats,
        'form_personnel': form_personnel,
        'nb_tickets_ligne': nb_tickets_ligne,
        'montant_ligne': montant_ligne,
        'nb_tickets_total': nb_tickets_total,
        'montant_total': montant_total,
        'par_mois': par_mois,
    })

@login_required
@role_required(['admin'])
def ajouter_personnel(request):
    if request.method == 'POST':
        form = AjoutPersonnelForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            if User.objects.filter(username=email).exists():
                messages.error(request, "Cet email est déjà utilisé.")
                return redirect('portail_admin')
            user = User.objects.create_user(username=email, password=password, email=email)
            user.first_name = form.cleaned_data['prenom']
            user.last_name = form.cleaned_data['nom']
            user.save()
            personnel = form.save(commit=False)
            personnel.user = user
            personnel.save()
            ProfilUtilisateur.objects.create(user=user, role=personnel.role)
            messages.success(request, "Personnel ajouté avec succès.")
        else:
            messages.error(request, "Erreur dans le formulaire.")
    return redirect('portail_admin')

@login_required
@role_required(['admin'])
def toggle_personnel(request, id):
    if request.method == 'POST':
        personnel = get_object_or_404(Personnel, id=id)
        personnel.est_actif = not personnel.est_actif
        personnel.user.is_active = personnel.est_actif
        personnel.user.save()
        personnel.save()
        messages.success(request, f"Statut modifié pour {personnel.prenom} {personnel.nom}")
    return redirect('portail_admin')

@login_required
@role_required(['admin'])
def supprimer_personnel(request, id):
    if request.method == 'POST':
        personnel = get_object_or_404(Personnel, id=id)
        user = personnel.user
        personnel.delete()
        user.delete()
        messages.success(request, "Personnel supprimé.")
    return redirect('portail_admin')

@login_required
@role_required(['admin'])
def modifier_personnel(request, id):
    personnel = get_object_or_404(Personnel, id=id)
    if request.method == 'POST':
        personnel.nom = request.POST.get('nom')
        personnel.prenom = request.POST.get('prenom')
        personnel.sexe = request.POST.get('sexe')
        personnel.telephone = request.POST.get('telephone')
        personnel.email = request.POST.get('email')
        personnel.role = request.POST.get('role')
        personnel.save()
        user = personnel.user
        user.username = personnel.email
        user.email = personnel.email
        user.first_name = personnel.prenom
        user.last_name = personnel.nom
        new_password = request.POST.get('password')
        if new_password:
            user.set_password(new_password)
        user.save()
        profile = user.profilutilisateur
        profile.role = personnel.role
        profile.save()
        messages.success(request, f"Membre {personnel.prenom} {personnel.nom} modifié avec succès.")
        return redirect('portail_admin')
    return redirect('portail_admin')

@login_required
@role_required(['etudiant'])
def partager_ticket(request, token):
    qr = get_object_or_404(QRCode, token=token, etudiant=request.user.etudiant, utilise=False)
    return render(request, 'partager_ticket.html', {'qr': qr, 'etudiant': request.user.etudiant})

@login_required
@role_required(['etudiant'])
def transferer_ticket(request, token):
    if request.method == 'POST':
        qr = get_object_or_404(QRCode, token=token, etudiant=request.user.etudiant, utilise=False)
        numero_ce = request.POST.get('numero_ce', '').strip()
        try:
            destinataire = Etudiant.objects.get(numero_ce=numero_ce)
        except Etudiant.DoesNotExist:
            messages.error(request, f"Aucun étudiant trouvé avec la carte n° {numero_ce}.")
            return redirect('portail_etudiant')
        if destinataire == request.user.etudiant:
            messages.error(request, "Vous ne pouvez pas vous transférer un ticket à vous-même.")
            return redirect('portail_etudiant')

        # Bloquer le QR original
        qr.utilise = True
        qr.save()

        # Décrémenter le compteur de l'expéditeur
        expediteur = request.user.etudiant
        expediteur.tickets_repas = max(0, expediteur.tickets_repas - 1)
        expediteur.save()

        # Créer un nouveau QR pour le destinataire (marqué comme transféré)
        QRCode.objects.create(
            token=str(uuid.uuid4()),
            etudiant=destinataire,
            type_ticket='repas',
            expire_at=qr.expire_at,
            est_transfere=True,
            transfere_depuis=expediteur,
        )
        messages.success(request, f"Ticket transféré à {destinataire.prenom} {destinataire.nom}.")
    return redirect('portail_etudiant')

@login_required
@role_required(['admin'])
def update_statut_menu(request, id):
    if request.method == 'POST':
        menu = get_object_or_404(Menu, id=id)
        menu.statut = request.POST.get('statut', 'en_attente')
        menu.save()
    return redirect('gestion_menus')

@login_required
def image_qr(request, token):
    qr_obj = get_object_or_404(QRCode, token=token, etudiant=request.user.etudiant)
    img = qrcode.make(token)
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    return HttpResponse(buffer, content_type='image/png')