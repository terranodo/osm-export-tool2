from __future__ import absolute_import

from djmp.models import Tileset
from mapproxy.script.conf.app import config_command
import yaml
from django.core.files.temp import NamedTemporaryFile
import logging
import sys
from django.db import IntegrityError
from django.conf import settings

logger = logging.getLogger(__name__)


class WMSToGeopackage():
    """
    Convert a WMS services to a geopackage.
    """

    def __init__(self, gpkgfile=None, bbox=None, wms_url=None, debug=None):
        """
        Initialize the SQliteToKml utility.

        Args:
            gpkgfile: where to write the gpkg output
            debug: turn debugging on / off
        """
        self.gpkgfile = gpkgfile
        self.bbox = bbox
        self.wms_url = wms_url
        if not self.gpkgfile:
            # create gpkg path from sqlite path.
            root = self.sqlite.split('.')[0]
            self.gpkgfile = root + '.gkpg'
        self.debug = debug

    def convert(self, ):
        """
        Convert sqlite to gpkg.
        """
        conf_dict = create_conf_from_wms(self.wms_url)
        tileset = create_tileset_from_conf_dict(conf_dict)


def create_conf_from_wms(wms_url):
    temp_file = NamedTemporaryFile()
    # wms_url = wms_url.replace('"','')
    params = ['--capabilities', wms_url, '--output', temp_file.name, '--force']
    config_command(params)

    conf_dict = None
    try:
        conf_dict = yaml.load(temp_file)
    except yaml.YAMLError as exc:
        logger.error(exc)
    return conf_dict

def create_tileset_from_conf_dict(conf_dict, name, bbox=None):

    name = name
    created_by = "Eventkit Service"
    cache_type = 'file'
    directory_layout = 'tms'
    directory = getattr(settings, 'CACHE_DIR', '/cache')
    filename = None
    table_name = None
    server_url = None
    source_type = 'wms'
    mapfile = None
    layer_zoom_stop = 6

    layers = get_layers(conf_dict.get('layers'))
    print(str(layers))
    sys.stdout.flush()
    for layer in layers:
        layer_name = layer.get('name')
        for source in layer.get('sources'):
            layer_source_data = conf_dict.get('sources').get(source) or conf_dict.get('caches').get(source)
            if layer_source_data.get('cache'):
                cache_type = layer_source_data.get('cache').get('type')
                directory_layout = layer_source_data.get('cache').get('directory_layout')
                directory = layer_source_data.get('cache').get('directory')
                filename = layer_source_data.get('cache').get('filename')
                table_name = layer_source_data.get('cache').get('table_name')

                if layer_source_data.get('cache').get('grids'):
                    for grid in layer_source_data.get('cache').get('grids'):
                        if grid.get('srs').lower() == 'epsg:4326':
                            temp_bbox = conf_dict.get('grids').get(grid).get('bbox')
                            if bbox and temp_bbox:
                                #since we are supporting only one grid, ensure that grid covers all of the grids area.
                                for i in [0, 1]:
                                    bbox[i] = temp_bbox if temp_bbox[i] < bbox[i] else bbox[i]
                                for i in [2, 3]:
                                    bbox[i] = temp_bbox if temp_bbox[i] > bbox[i] else bbox[i]
                            elif temp_bbox:
                                bbox = temp_bbox
            if layer_source_data.get('type', ' ').lower() == 'wms':
                server_url = layer_source_data.get('req').get('url')
                source_type = 'wms'
            if layer_source_data.get('type', ' ').lower() == 'mapnik':
                mapfile = layer_source_data.get('mapfile')
        if not bbox:
            bbox = [-180, -89, 180, 89]
        try:
            print("Creating tileset for name: {}".format(name))
            return Tileset.objects.get_or_create(name=name,
                                          created_by=created_by,
                                          layer_name=layer_name,
                                          cache_type=cache_type,
                                          directory_layout=directory_layout,
                                          directory=directory,
                                          filename=filename,
                                          table_name=table_name,
                                          bbox_x0=bbox[0],
                                          bbox_y0=bbox[1],
                                          bbox_x1=bbox[2],
                                          bbox_y1=bbox[3],
                                          server_url=server_url,
                                          source_type=source_type,
                                          mapfile=mapfile,
                                          layer_zoom_stop=layer_zoom_stop)
        except IntegrityError:
            continue
    sys.stdout.flush()

def get_layers(layers):
    layer_list = []
    for layer in layers:
        if isinstance(layer, dict) and layer.get('layers'):
            layer_list += get_layers(layer.get('layers'))
        else:
            layer_list += [layer]
    return layer_list
