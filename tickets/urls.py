from django.urls import path

from django.urls import path
from . import views

urlpatterns = [
    path('', views.accueil, name='accueil'),
    path('inscription/', views.inscription, name='inscription'),
    path('connexion/', views.connexion, name='connexion'),
    path('deconnexion/', views.deconnexion, name='deconnexion'),
    path('redirection/', views.redirection, name='redirection'),
    path('acces-refuse/', views.acces_refuse, name='acces_refuse'),
    # Étudiant
    path('etudiant/', views.portail_etudiant, name='portail_etudiant'),
    path('recharger/', views.recharger_wallet, name='recharger'),
    path('acheter/', views.acheter_ticket, name='acheter_ticket'),
    path('generer-qr/', views.generer_qr, name='generer_qr'),
    path('qr/<str:token>.png', views.image_qr, name='image_qr'),
    # Caissier
    path('caissier/', views.portail_caissier, name='portail_caissier'),
    path('vendre/', views.vendre_ticket, name='vendre_ticket'),
    path('ajouter-etudiant/', views.ajouter_etudiant, name='ajouter_etudiant'),
    # Contrôleur
    path('controleur/', views.portail_controleur, name='portail_controleur'),
    path('valider-qr/', views.valider_qr, name='valider_qr'),
    path('debit-manuel/', views.debit_manuel, name='debit_manuel'),
    # Admin
    path('portail_admin/', views.portail_admin, name='portail_admin'),
    path('ajouter-personnel/', views.ajouter_personnel, name='ajouter_personnel'),
    path('modifier-personnel/<int:id>/', views.modifier_personnel, name='modifier_personnel'),
    path('toggle-personnel/<int:id>/', views.toggle_personnel, name='toggle_personnel'),
    path('supprimer-personnel/<int:id>/', views.supprimer_personnel, name='supprimer_personnel'),
    # Menus
    path('gestion-menus/', views.gestion_menus, name='gestion_menus'),
    path('ajouter-menu/', views.ajouter_menu, name='ajouter_menu'),
    path('modifier-menu/<int:id>/', views.modifier_menu, name='modifier_menu'),
    path('supprimer-menu/<int:id>/', views.supprimer_menu, name='supprimer_menu'),
    path('statut-menu/<int:id>/', views.update_statut_menu, name='update_statut_menu'),
    path('transferer/<str:token>/', views.transferer_ticket, name='transferer_ticket'),
    path('partager/<str:token>/', views.partager_ticket, name='partager_ticket'),
]