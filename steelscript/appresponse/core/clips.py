# Copyright (c) 2016 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.

from steelscript.common.datastructures import DictObject


class ClipService(object):
    """This class provides an interface to manage the clip service on
    an AppResponse appliance.
    """

    def __init__(self, arx):
        self.npm_clip = arx.find_service('npm.clips')
        self.clips = self.npm_clip.bind('clips')

    def get_clips(self):
        resp = self.clips.execute('get')

        return [self.get_job_by_id(item['id'])
                for item in resp.data['items']]

    def get_clip_by_id(self, id_):
        return Clip(self.npm_clip.bind('clip', id=id_))

    def create_clip(self, job, timefilter, description=''):

        config = dict(job_id=job.prop.id,
                      start_time=timefilter.start,
                      end_time=timefilter.end,
                      description=description)

        data = dict(config=config)
        resp = self.clips.execute('create', _data=data)

        return Clip(resp)

    def create_clips(self, data_defs):
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
