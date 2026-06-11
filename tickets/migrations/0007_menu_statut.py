from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0006_remove_menu_image_url_menu_image_alter_menu_ordre'),
    ]

    operations = [
        migrations.AddField(
            model_name='menu',
            name='statut',
            field=models.CharField(
                choices=[
                    ('en_attente', 'En attente'),
                    ('en_cours', 'En cours de préparation'),
                    ('pret', 'Prêt à servir'),
                    ('termine', 'Service terminé'),
                ],
                default='en_attente',
                max_length=20,
            ),
        ),
    ]
