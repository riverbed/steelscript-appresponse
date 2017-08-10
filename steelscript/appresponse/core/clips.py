# Copyright (c) 2017 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.

import logging

from steelscript.common.datastructures import DictObject
from steelscript.appresponse.core.types import ServiceClass
from steelscript.appresponse.core.capture import Job

logger = logging.getLogger(__name__)


class ClipService(ServiceClass):
    """This class provides an interface to manage the clip service on
    an AppResponse appliance.
    """

    def __init__(self, appresponse):
        self.appresponse = appresponse
        self.servicedef = None
        self.clips = None

    def _bind_resources(self):

        # Init service
        self.servicedef = self.appresponse.find_service('npm.clips')

        # Init resource
        self.clips = self.servicedef.bind('clips')

    def get_clips(self):
        """Return a list of Clip objects."""

        logger.debug("Obtaining all Clip objects ")

        resp = self.clips.execute('get')

        if 'items' not in resp.data:
            return []

        return [Clip.create(item, self.servicedef)
                for item in resp.data['items']]

    def get_clip_by_id(self, id_):
        """Return the Clip object given an id."""

        logger.debug("Getting clip object with id {}".format(id_))
        return Clip(self.servicedef.bind('clip', id=id_))

    def create_clip(self, job, timefilter, description='', from_job=False):
        """Create a Clip object based on the packet capture job and time
         filter.
        """

        config = dict(job_id=job.id,
                      start_time=timefilter.start,
                      end_time=timefilter.end,
                      description=description)

        logger.debug("Creating a Clip object with configuration as {}"
                     .format(config))

        data = dict(config=config)

        resp = self.clips.execute('create', _data=data)

        return Clip.create(data=resp.data, servicedef=self.servicedef,
                           datarep=resp, from_job=from_job)

    def create_clips(self, data_defs):
        """Create a Clips object from a list of data definition requests.
        When some DataDef objects are using sources other than capture jobs,
        then those sources will stay the same. The capture job sources will
        be converted into Clip objects.

        :param data_defs: list of DataDef objects
        :return: a Clips object
        """
        clips = []
        for dd in data_defs:
            if isinstance(dd.source, Job):
                logger.debug("Creating a Clip object for one data def request "
                             "with capture job '{}'"
                             .format(dd.source.name))

                clip = self.create_clip(dd.source, dd.timefilter,
                                        from_job=True)
                clips.append(clip)
            else:
                clips.append(dd.source)

        return Clips(clips)


class Clips(object):

    def __init__(self, clip_objs):
        self.clip_objs = clip_objs

    def __iter__(self):
        for clip_obj in self.clip_objs:
            yield clip_obj

    def __enter__(self):
        return self.clip_objs

    def __exit__(self, type, value, traceback):
        for clip in self.clip_objs:
            if isinstance(clip, Clip) and clip.from_job:
                logger.debug("Deleting Clip object with id {}"
                             .format(clip.id))
                clip.delete()

        self.clip_objs = None


class Clip(DictObject):

    @classmethod
    def create(cls, data, servicedef, datarep=None, from_job=False):
        logger.debug('Creating Clip object with data {}'.format(data))
        obj = DictObject.create_from_dict(data)
        if not datarep:
            obj.datarep = servicedef.bind('clip', id=obj.id)
        else:
            obj.datarep = datarep
        obj.from_job = from_job
        return Clip(obj)

    def delete(self):
        self.datarep.execute('delete')
