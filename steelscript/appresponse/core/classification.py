# Copyright (c) 2016 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.

import logging

from steelscript.common.datastructures import DictObject
from steelscript.appresponse.core.types import ServiceClass


logger = logging.getLogger(__name__)


class HostGroupConfig(DictObject):

    Attrs = ['name', 'id', 'desc', 'hosts', 'member_hostgroups',
             'enabled', 'in_speed', 'in_speed_unit',
             'out_speed', 'out_speed_unit', 'tags']

    def __init__(self, **kwargs):
        for k, v in kwargs.iteritems():
            if k in self.Attrs:
                setattr(self, k, v)


class ClassificationService(ServiceClass):
    """ This class provides an interface to manage classification
    service on an AppResponse application.
    """

    SERVICE_NAME = 'npm.classification'

    def __init__(self, appresponse):
        self.appresponse = appresponse
        self.servicedef = None
        self.hostgroups = None

    def bind_resources(self):

        # Init service:
        self.servicedef = self.appresponse.find_service(self.SERVICE_NAME)

        # Init resources
        self.hostgroups = self.servicedef.bind('hostgroups')

    def get_hostgroups(self):

        data = self.hostgroups.execute('get').data

        if 'items' in data:

            return [self.get_hostgroup_by_id(item['id'])
                    for item in data['items']]

        return []

    def get_hostgroup_by_id(self, id_):

        return HostGroup(self.servicedef.bind('hostgroup', id=id_))

    def create_hostgroup(self, obj):

        resp = self.hostgroups.execute('create', _data=obj)
        return HostGroup(resp)

    def create_hostgroups(self, objs):

        resp = self.hostgroups.execute('bulk_create', _data=dict(items=objs))
        return [self.get_hostgroup_by_id(item['id'])
                for item in resp.data['items']]

    def hierarchy_hostgroups(self, objs):

        resp = self.hostgroups.execute('bulk_hierarchy',
                                       _data=dict(items=objs))
        return [self.get_hostgroup_by_id(item['id'])
                for item in resp.data['items']]

    def bulk_delete(self, ids=None):

        if not ids:
            data = dict(delete_all=True)
        else:
            data = dict(delete_ids=ids)

        self.hostgroups.execute('bulk_delete', _data=data)


class HostGroup(object):

    def __init__(self, datarep=None):

        self.datarep = datarep
        data = self.datarep.execute('get').data
        self.prop = DictObject.create_from_dict(data)

    def update(self, obj):

        self.datarep.execute('set', _data=obj)
        self.prop.update(obj)

    def delete(self):

        self.datarep.execute('delete')
        self.datarep = None
        self.prop = None
