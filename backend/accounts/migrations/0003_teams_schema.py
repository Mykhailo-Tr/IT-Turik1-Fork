from django.db import migrations, models
import django.db.models.deletion


def migrate_team_data(apps, schema_editor):
    Team = apps.get_model('accounts', 'Team')
    User = apps.get_model('accounts', 'User')
    TeamMember = apps.get_model('accounts', 'TeamMember')
    db_alias = schema_editor.connection.alias

    users_with_team = User.objects.using(db_alias).exclude(team_id=None)
    for user in users_with_team.iterator():
        TeamMember.objects.using(db_alias).get_or_create(team_id=user.team_id, user_id=user.id)

    fallback_user = User.objects.using(db_alias).order_by('id').first()

    for team in Team.objects.using(db_alias).all().iterator():
        changed = False

        if not team.email:
            team.email = f'team-{team.id}@example.local'
            changed = True

        if not team.captain_id:
            captain_member = (
                TeamMember.objects.using(db_alias)
                .filter(team_id=team.id)
                .order_by('user_id')
                .first()
            )
            captain_id = captain_member.user_id if captain_member else (fallback_user.id if fallback_user else None)

            if captain_id is None:
                base_username = f'team_captain_{team.id}'
                username = base_username
                suffix = 1
                while User.objects.using(db_alias).filter(username=username).exists():
                    username = f'{base_username}_{suffix}'
                    suffix += 1

                fallback_user = User.objects.using(db_alias).create(
                    username=username,
                    email=f'{username}@example.local',
                    password='!',
                    role='team',
                    is_active=False,
                )
                captain_id = fallback_user.id

            team.captain_id = captain_id
            changed = True

        if changed:
            team.save(update_fields=['email', 'captain'])

        TeamMember.objects.using(db_alias).get_or_create(team_id=team.id, user_id=team.captain_id)


def noop_reverse(apps, schema_editor):
    return


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_user_needs_onboarding'),
    ]

    operations = [
        migrations.AddField(
            model_name='team',
            name='email',
            field=models.EmailField(default='team@example.local', max_length=254),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='team',
            name='organization',
            field=models.CharField(blank=True, default='', max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='team',
            name='contact',
            field=models.CharField(blank=True, default='', max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='team',
            name='captain',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='captained_teams', to='accounts.user'),
        ),
        migrations.CreateModel(
            name='TeamMember',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='team_members', to='accounts.team')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='team_memberships', to='accounts.user')),
            ],
            options={
                'unique_together': {('user', 'team')},
                'indexes': [models.Index(fields=['user', 'team'], name='team_members_index_0')],
            },
        ),
        migrations.AddField(
            model_name='team',
            name='members',
            field=models.ManyToManyField(related_name='teams', through='accounts.TeamMember', to='accounts.user'),
        ),
        migrations.RunPython(migrate_team_data, noop_reverse),
        migrations.RemoveField(
            model_name='user',
            name='team',
        ),
        migrations.AlterField(
            model_name='team',
            name='captain',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='captained_teams', to='accounts.user'),
        ),
        migrations.AlterField(
            model_name='team',
            name='name',
            field=models.CharField(max_length=255),
        ),
    ]
