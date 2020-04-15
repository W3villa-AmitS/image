# Generated by Django 2.0.6 on 2019-03-07 06:19

from django.conf import settings
import django.contrib.auth.models
import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0009_alter_user_last_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('first_name', models.CharField(blank=True, max_length=30, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('username', models.CharField(db_index=True, max_length=255, unique=True)),
                ('email', models.EmailField(db_index=True, max_length=254, unique=True)),
                ('state', models.CharField(choices=[('U', 'Uninitialized'), ('L', 'Locked'), ('A', 'Activated'), ('D', 'Deactivated')], max_length=1)),
                ('roles', models.CharField(max_length=4)),
                ('active_role', models.CharField(choices=[('A', 'Admin'), ('M', 'Manager'), ('S', 'Searcher'), ('W', 'Worker')], max_length=1)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('jwt_secret', models.UUIDField(default=uuid.uuid4)),
                ('last_passwords', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=128), default=list, size=None)),
                ('password_set_at', models.DateTimeField()),
            ],
            options={
                'verbose_name': 'User',
                'verbose_name_plural': 'Users',
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Request',
            fields=[
                ('email_id', models.EmailField(max_length=254, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField()),
                ('secret_key', models.CharField(max_length=128)),
            ],
        ),
        migrations.CreateModel(
            name='TaskAllocation',
            fields=[
                ('task_id', models.CharField(max_length=24, primary_key=True, serialize=False)),
                ('job_id', models.CharField(max_length=8)),
                ('worker_list', django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(), default=list, size=None)),
            ],
        ),
        migrations.CreateModel(
            name='TaskCompleted',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('task_id', models.CharField(max_length=24)),
                ('job_id', models.CharField(max_length=8)),
                ('user_id', models.IntegerField()),
                ('status', models.CharField(choices=[('ST', 'Started Task'), ('CT', 'Completed Task'), ('AB', 'Aborted by Worker'), ('RA', 'Rejected due to accuracy')], max_length=1)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Worker',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.IntegerField()),
                ('is_active', models.BooleanField(default=True)),
                ('is_completed', models.BooleanField(default=False)),
                ('job_id', models.CharField(max_length=8)),
                ('qat_passed', models.IntegerField(default=0)),
                ('qat_failed', models.IntegerField(default=0)),
                ('task_allocated', models.CharField(max_length=24)),
                ('tasks_completed', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=24), default=list, size=None)),
                ('disqualified_till', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name='UserInformation',
            fields=[
                ('user_id', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('first_name', models.CharField(max_length=50)),
                ('last_name', models.CharField(max_length=50)),
                ('date_of_birth', models.DateField()),
                ('phone_number', models.CharField(max_length=12)),
                ('location', models.CharField(max_length=30)),
                ('gender', models.CharField(choices=[('M', 'Male'), ('F', 'Female'), ('T', 'Transgender')], max_length=1)),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='worker',
            unique_together={('user_id', 'job_id')},
        ),
        migrations.AddField(
            model_name='user',
            name='groups',
            field=models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups'),
        ),
        migrations.AddField(
            model_name='user',
            name='user_permissions',
            field=models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions'),
        ),
    ]