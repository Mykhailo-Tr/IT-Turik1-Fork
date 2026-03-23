from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('teams', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='team',
            old_name='contact',
            new_name='contact_telegram',
        ),
        migrations.AddField(
            model_name='team',
            name='contact_discord',
            field=models.CharField(blank=True, default='', max_length=100),
            preserve_default=False,
        ),
    ]
