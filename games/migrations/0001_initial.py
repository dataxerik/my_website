# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-09-17 14:54
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Game',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('type', models.CharField(max_length=200)),
                ('release_year', models.DateTimeField(verbose_name='game published date')),
                ('developer', models.CharField(max_length=200)),
                ('publisher', models.CharField(max_length=200)),
            ],
        ),
    ]