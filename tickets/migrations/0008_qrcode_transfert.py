from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0007_menu_statut'),
    ]

    operations = [
        migrations.AddField(
            model_name='qrcode',
            name='est_transfere',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='qrcode',
            name='transfere_depuis',
            field=models.ForeignKey(
                blank=True, null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='tickets_donnes',
                to='tickets.etudiant',
            ),
        ),
    ]
