# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    def insert_export_providers(apps, schema_editor):

        ExportProvider = apps.get_model('jobs', 'ExportProvider')
        ExportProviderType = apps.get_model('jobs', 'ExportProviderType')
        ExportFormat = apps.get_model('jobs', 'ExportFormat')

        export_formats = ExportFormat.objects.filter(slug__in=['OBF',
                                                               'SHP',
                                                               'KML',
                                                               'SQLITE',
                                                               'GARMIN',
                                                               'THEMATIC',
                                                               'GPKG'])
        osm_type = ExportProviderType.objects.create(type_name='osm')
        for export_format in export_formats:
            osm_type.supported_formats.add(export_format.pk)
        osm_type.save()

        export_formats = ExportFormat.objects.filter(slug__in=['GPKG'])
        wms_type = ExportProviderType.objects.create(type_name='wms')
        for export_format in export_formats:
            wms_type.supported_formats.add(export_format.pk)
        wms_type.save()

        ExportProvider.objects.create(name='OpenStreetMap', export_provider_type=osm_type)
        ExportProvider.objects.create(name='Active Fires 1 Month',
                                    url='http://neowms.sci.gsfc.nasa.gov/wms/wms?SERVICE=WMS&REQUEST=GetCapabilities&VERSION=1.3.0',
                                    layer='MOD14A1_M_FIRE',
                                    export_provider_type=wms_type)

    dependencies = [
        ('jobs', '0003_auto_20160825_1845'),
    ]

    operations = [
        migrations.RunPython(insert_export_providers),
    ]