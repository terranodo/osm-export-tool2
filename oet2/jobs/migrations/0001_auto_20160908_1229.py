# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-09-08 12:29
from __future__ import unicode_literals

from django.db import migrations, models
import oet2.jobs.models


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', 'insert_export_providers'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='exportprovidertype',
            name='supported_formats',
        ),
        migrations.RemoveField(
            model_name='providertask',
            name='formats',
        ),
        migrations.RemoveField(
            model_name='providertask',
            name='provider',
        ),
        migrations.RemoveField(
            model_name='exportprovider',
            name='export_provider_type',
        ),
        migrations.RemoveField(
            model_name='job',
            name='provider_tasks',
        ),
        migrations.AddField(
            model_name='exportprovider',
            name='type',
            field=oet2.jobs.models.LowerCaseCharField(choices=[('osm', 'OpenStreetMap'), ('wms', 'WMS'), ('wfs', 'WFS'), ('wmts', 'WMTS'), ('dg', 'Digital Globe')], default='wms', max_length=3, verbose_name='Service Type'),
        ),
        migrations.AddField(
            model_name='job',
            name='formats',
            field=models.ManyToManyField(related_name='formats', to='jobs.ExportFormat'),
        ),
        migrations.DeleteModel(
            name='ExportProviderType',
        ),
        migrations.DeleteModel(
            name='ProviderTask',
        ),
    ]