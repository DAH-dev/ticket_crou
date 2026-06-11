from django.shortcuts import redirect
from .models import ProfilUtilisateur, Etudiant, Personnel

def role_required(allowed_roles=[]):
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('connexion')
            
            # Création automatique du profil si inexistant
            try:
                profile = request.user.profilutilisateur
            except ProfilUtilisateur.DoesNotExist:
                if hasattr(request.user, 'etudiant'):
                    role = 'etudiant'
                elif hasattr(request.user, 'personnel'):
                    role = request.user.personnel.role
                else:
                    role = 'admin'  # pour les superusers
                ProfilUtilisateur.objects.create(user=request.user, role=role)
                profile = request.user.profilutilisateur
            
            if profile.role in allowed_roles:
                return view_func(request, *args, **kwargs)
            else:
                return redirect('acces_refuse')
        return wrapper
    return decorator