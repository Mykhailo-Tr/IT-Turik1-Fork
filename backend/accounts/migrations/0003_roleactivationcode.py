from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_move_team_models_to_teams'),
    ]

    operations = [
        migrations.CreateModel(
            name='RoleActivationCode',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(db_index=True, max_length=24, unique=True)),
                (
                    'role',
                    models.CharField(
                        choices=[
                            ('admin', 'Admin'),
                            ('team', 'Team Member'),
                            ('jury', 'Jury'),
                            ('organizer', 'Organizer'),
                        ],
                        max_length=20,
                    ),
                ),
                ('is_used', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('used_at', models.DateTimeField(blank=True, null=True)),
                (
                    'created_by',
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=models.SET_NULL,
                        related_name='created_role_activation_codes',
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    'used_by',
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=models.SET_NULL,
                        related_name='used_role_activation_codes',
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.AddIndex(
            model_name='roleactivationcode',
            index=models.Index(fields=['role', 'is_used'], name='role_code_role_used_idx'),
        ),
    ]
