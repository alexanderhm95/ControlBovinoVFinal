# Generated by Django 5.0.6 on 2024-06-10 17:53

import django.db.models.deletion
import temp_car.utils.getHours
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('temp_car', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Bovinos',
            fields=[
                ('id_Bovinos', models.AutoField(primary_key=True, serialize=False)),
                ('idCollar', models.IntegerField(unique=True)),
                ('macCollar', models.CharField(blank=True, max_length=100, null=True, unique=True)),
                ('nombre', models.CharField(max_length=100)),
                ('fecha_registro', models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name='MedicionCompleto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('temperatura', models.FloatField()),
                ('pulsaciones', models.IntegerField()),
                ('fecha_creacion', models.DateTimeField(verbose_name=temp_car.utils.getHours.getDate)),
                ('collar_id', models.CharField(max_length=5000)),
                ('nombre_vaca', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='PersonalInfo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cedula', models.CharField(blank=True, max_length=15, null=True, unique=True)),
                ('telefono', models.CharField(blank=True, max_length=15, null=True)),
                ('nombre', models.CharField(blank=True, max_length=50, null=True)),
                ('apellido', models.CharField(blank=True, max_length=50, null=True)),
                ('email', models.EmailField(blank=True, max_length=50, null=True, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Pulsaciones',
            fields=[
                ('id_Pulsaciones', models.AutoField(primary_key=True, serialize=False)),
                ('valor', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Temperatura',
            fields=[
                ('id_Temperatura', models.AutoField(primary_key=True, serialize=False)),
                ('valor', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Lectura',
            fields=[
                ('id_Lectura', models.AutoField(primary_key=True, serialize=False)),
                ('fecha_lectura', models.DateField(default=temp_car.utils.getHours.getDate)),
                ('hora_lectura', models.TimeField(default=temp_car.utils.getHours.getTime)),
                ('id_Bovino', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='temp_car.bovinos')),
                ('id_Pulsaciones', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='temp_car.pulsaciones')),
                ('id_Temperatura', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='temp_car.temperatura')),
            ],
        ),
    ]