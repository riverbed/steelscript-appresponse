# Copyright (c) 2016 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.

from steelscript.appresponse.core.clips import Clip
from steelscript.appresponse.core.capture import Job
from steelscript.common import timeutils


class InvalidType(Exception):
    pass


class Column(object):

    def __init__(self, name, key=False):
        self.name = name
        self.key = key

    def __str__(self):
        return self.name


class Key(Column):

    def __init__(self, name):
        super(Key, self).__init__(name, key=True)


class Value(Column):

    def __init__(self, name):
        super(Value, self).__init__(name, key=False)


class Source(object):

    def __init__(self, name, path, packets_obj):
        self.name = name
        self.path = path
        self.packets_obj = packets_obj

    def to_dict(self):
        return dict(name=self.name, path=self.path)


class PacketsSource(Source):

    def __init__(self, packets_obj):
        if isinstance(packets_obj, Clip):
            path = 'clips/%s' % packets_obj.prop.id
        elif isinstance(packets_obj, Job):
            path = 'jobs/%s' % packets_obj.prop.id
        else:
            raise InvalidType('Can only support clip packet source')

        super(PacketsSource, self).__init__(name='packets', path=path,
                                            packets_obj=packets_obj)


class TimeFilter(object):

    def __init__(self, start, end):
        self.start = start.strftime('%s')
        self.end = end.strftime('%s')

    @classmethod
    def parse_range(cls, string):
        start, end = timeutils.parse_range(string)
        return cls(start, end)
