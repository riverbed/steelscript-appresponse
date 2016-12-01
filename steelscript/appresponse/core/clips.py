# Copyright (c) 2016 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.

from steelscript.common.datastructures import DictObject
from steelscript.appresponse.core.types import ServiceClass


class ClipService(ServiceClass):
    """This class provides an interface to manage the clip service on
    an AppResponse appliance.
    """

    def __init__(self, appresponse):
        self.appresponse = appresponse
        self.servicedef = None
        self.clips = None

    def bind_resources(self):

        # Init service
        self.servicedef = self.appresponse.find_service('npm.clips')

        # Init resource
        self.clips = self.servicedef.bind('clips')

    def get_clips(self):
        """Return a list of Clip objects."""

        resp = self.clips.execute('get')

        return [self.get_job_by_id(item['id'])
                for item in resp.data['items']]

    def get_clip_by_id(self, id_):
        """Return the Clip object given an id."""

        return Clip(self.servicedef.bind('clip', id=id_))

    def create_clip(self, job, timefilter, description=''):
        """Create a Clip object based on the packet capture job and time
         filter.
        """

        config = dict(job_id=job.prop.id,
                      start_time=timefilter.start,
                      end_time=timefilter.end,
                      description=description)

        data = dict(config=config)
        resp = self.clips.execute('create', _data=data)

        return Clip(resp)

    def create_clips(self, data_defs):
        """Create a Clips object from a list of data definition requests."""

        return Clips([self.create_clip(dd.job, dd.timefilter)
                      for dd in data_defs])


class Clips(object):

    def __init__(self, clip_objs):
        self.clip_objs = clip_objs

    def __enter__(self):
        return self.clip_objs

    def __exit__(self, type, value, traceback):
        for clip in self.clip_objs:
            clip.delete()

        self.clip_objs = None


class Clip(object):

    def __init__(self, datarep):

        self.datarep = datarep
        data = self.datarep.execute('get').data
        self.prop = DictObject.create_from_dict(data)

    def delete(self):
        self.datarep.execute('delete')
        self.prop = None
        self.datarep = None
