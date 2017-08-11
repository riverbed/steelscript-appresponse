# Copyright (c) 2017 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.

import logging

from steelscript.common.datastructures import DictObject
from steelscript.appresponse.core.types import ServiceClass, ResourceObject
from steelscript.common.exceptions import RvbdHTTPException

logger = logging.getLogger(__name__)


class HostGroupConfig(DictObject):
    """Encapsulating HostGroup Config data, this class is used to
    create objects as arguments for creating Hostgroups.
    """

    Attrs = ['name', 'id', 'desc', 'hosts', 'member_hostgroups',
             'enabled', 'in_speed', 'in_speed_unit',
             'out_speed', 'out_speed_unit', 'tags']

    def __init__(self, **kwargs):
        for k, v in kwargs.iteritems():
            if k in self.Attrs:
                setattr(self, k, v)
            else:
                raise KeyError("'%s' is not a valid attribute "
                               "for hostgroup" % k)


class ClassificationService(ServiceClass):
    """ This class provides an interface to manage classification
    service on an AppResponse appliance.
    """

    SERVICE_NAME = 'npm.classification'

    def __init__(self, appresponse):
        self.appresponse = appresponse
        self.servicedef = None
        self.hostgroups = None

    def _bind_resources(self):

        # Init service:
        self.servicedef = self.appresponse.find_service(self.SERVICE_NAME)

        # Init resources
        self.hostgroups = self.servicedef.bind('hostgroups')

    def get_hostgroups(self):
        """Return all hostgroups as a list of HostGroup objects."""

        resp = self.hostgroups.execute('get')

        if 'items' in resp.data:

            return [HostGroup(data=item, servicedef=self.servicedef)
                    for item in resp.data['items']]

        return []

    def get_hostgroup_by_id(self, id_):
        try:
            resp = self.servicedef.bind('hostgroup', id=id_)
            return HostGroup(data=resp.data, datarep=resp)
        except RvbdHTTPException, e:
            if str(e).startswith('404'):
                raise ValueError('No hostgroup found with id %s' % id_)

    def get_hostgroup_by_name(self, name):
        try:
            return (hg for hg in self.get_hostgroups()
                    if hg.name == name).next()
        except StopIteration:
            raise ValueError("No hostgroups found with name "
                             "'%s'." % name)

    def create_hostgroup(self, obj):
        """Create a Hostgroup on the appresponse appliance.

        :param obj: an HostGroupConfig object.
        :return : an HostGroup object.
        """

        resp = self.hostgroups.execute('create', _data=obj)
        return HostGroup(data=resp.data, datarep=resp)

    def create_hostgroups(self, objs):
        """Create multiple hostgroup objects in one go.

        :param obj: a list of HostGroupConfig objects.
        :return: a list of HostGroup objects.
        """

        resp = self.hostgroups.execute('bulk_create', _data=dict(items=objs))

        return [HostGroup(data=item, servicedef=self.servicedef)
                for item in resp.data['items']]

    def hierarchy_hostgroups(self, objs):

        resp = self.hostgroups.execute('bulk_hierarchy',
                                       _data=dict(items=objs))
        return [HostGroup(data=item, servicedef=self.servicedef)
                for item in resp.data['items']]

    def bulk_delete(self, ids=None):
        """Delete Hostgroups on an appresponse appliance.

        :param ids: a list of integers representing ids of HostGroups to be
            deleted. If None, all hostgroups will be deleted.
        """
        if not ids:
            data = dict(delete_all=True)
        else:
            data = dict(delete_ids=ids)

        self.hostgroups.execute('bulk_delete', _data=data)


class HostGroup(ResourceObject):
    """This class provides an interface to interact with one hostgroup
    on an appresponse appliance.
    """
    resource = 'hostgroup'

    def __repr__(self):
        return '<%s id: %s, name: %s>'\
               % (self.__class__.__name__, self.id, self.name)

    def update(self, obj):
        """Update the HostGroup on an appresponse appliance.

        :param obj: an HostGroupConfig object. Note that the Hostgroup
            on the appresponse will be totally overwritten by the
            HostGroup object.
        """

        resp = self.datarep.execute('set', _data=obj)
        self.data = DictObject.create_from_dict(resp.data)

    def delete(self):
        """Delete the HostGroup on the appresponse appliance."""
        self.datarep.execute('delete')
        self.datarep = None
