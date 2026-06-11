from django.contrib import admin
from .models import Menu, ProfilUtilisateur, Etudiant, Personnel, Achat, Depense, Vente, QRCode

admin.site.register(ProfilUtilisateur)
admin.site.register(Etudiant)
admin.site.register(Personnel)
admin.site.register(Achat)
admin.site.register(Depense)
admin.site.register(Vente)
admin.site.register(QRCode)
admin.site.register(Menu) 