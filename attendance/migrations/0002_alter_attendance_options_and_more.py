# Generated by Django 5.1.4 on 2025-01-23 14:30

import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('attendance', '0001_initial'),
        ('courses', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='attendance',
            options={},
        ),
        migrations.AlterModelOptions(
            name='attendancesession',
            options={},
        ),
        migrations.RenameField(
            model_name='attendance',
            old_name='timestamp',
            new_name='check_in_time',
        ),
        migrations.AlterUniqueTogether(
            name='attendance',
            unique_together=set(),
        ),
        migrations.RemoveField(
            model_name='attendancesession',
            name='lecturer',
        ),
        migrations.RemoveField(
            model_name='attendancesession',
            name='status',
        ),
        migrations.AddField(
            model_name='attendance',
            name='latitude',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='attendance',
            name='longitude',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='attendancesession',
            name='allowed_latitude',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='attendancesession',
            name='allowed_longitude',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='attendancesession',
            name='geofence_radius',
            field=models.FloatField(default=50),
        ),
        migrations.AddField(
            model_name='attendancesession',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='attendancesession',
            name='is_geofencing_enabled',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='attendance',
            name='session',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='attendance.attendancesession'),
        ),
        migrations.AlterField(
            model_name='attendance',
            name='status',
            field=models.CharField(choices=[('present', 'Present'), ('late', 'Late'), ('absent', 'Absent')], default='present', max_length=20),
        ),
        migrations.AlterField(
            model_name='attendance',
            name='student',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='attendancesession',
            name='course',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='courses.course'),
        ),
        migrations.AlterField(
            model_name='attendancesession',
            name='qr_code',
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
        migrations.AlterField(
            model_name='attendancesession',
            name='start_time',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.RemoveField(
            model_name='attendance',
            name='location_data',
        ),
    ]
