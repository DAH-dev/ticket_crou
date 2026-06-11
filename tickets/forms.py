from django import forms
from django.contrib.auth.models import User
from .models import Etudiant, Menu, Personnel

class InscriptionEtudiantForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Mot de passe")
    confirm_password = forms.CharField(widget=forms.PasswordInput, label="Confirmation")

    class Meta:
        model = Etudiant
        fields = ['numero_cni', 'numero_ce', 'nom', 'prenom', 'sexe', 'date_naissance',
                  'niveau', 'filiere', 'telephone', 'email']

    def clean(self):
        cleaned_data = super().clean()
        pwd = cleaned_data.get('password')
        confirm = cleaned_data.get('confirm_password')
        if pwd and confirm and pwd != confirm:
            raise forms.ValidationError("Les mots de passe ne correspondent pas.")
        return cleaned_data

    def save(self, commit=True):
        etudiant = super().save(commit=False)
        if commit:
            user = User.objects.create_user(
                username=self.cleaned_data['numero_ce'],
                password=self.cleaned_data['password'],
                email=self.cleaned_data['email'],
                first_name=self.cleaned_data['prenom'],
                last_name=self.cleaned_data['nom']
            )
            etudiant.user = user
            etudiant.save()
            from .models import ProfilUtilisateur
            ProfilUtilisateur.objects.create(user=user, role='etudiant')
        return etudiant

class RechargeForm(forms.Form):
    montant = forms.IntegerField(min_value=200, label="Montant (FCFA)")

class AchatTicketForm(forms.Form):
    quantite = forms.IntegerField(min_value=1, max_value=50, label="Nombre de tickets")

class VenteTicketForm(forms.Form):
    etudiant = forms.ModelChoiceField(queryset=Etudiant.objects.all(), label="Étudiant")
    quantite = forms.IntegerField(min_value=1, label="Nombre de tickets")

class AjoutPersonnelForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Mot de passe")
    class Meta:
        model = Personnel
        fields = ['nom', 'prenom', 'sexe', 'telephone', 'email', 'role']
        
# Si vous avez ajouté MenuForm, remplacez-le par :
class MenuForm(forms.ModelForm):
    class Meta:
        model = Menu
        fields = ['type', 'titre', 'description', 'prix', 'image', 'actif', 'ordre']
        widgets = {
            'type': forms.Select(attrs={'class': 'w-full border rounded p-2'}),
            'titre': forms.TextInput(attrs={'class': 'w-full border rounded p-2'}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'w-full border rounded p-2'}),
            'prix': forms.NumberInput(attrs={'class': 'w-full border rounded p-2'}),
            'image': forms.ClearableFileInput(attrs={'class': 'w-full border rounded p-2'}),
            'actif': forms.CheckboxInput(attrs={'class': 'mr-2'}),
            'ordre': forms.NumberInput(attrs={'class': 'w-full border rounded p-2'}),
        }