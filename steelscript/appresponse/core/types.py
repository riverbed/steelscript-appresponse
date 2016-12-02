# Copyright (c) 2016 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.

import logging

from steelscript.common import timeutils

logger = logging.getLogger(__name__)


class InvalidType(Exception):
    pass


class ServiceClass(object):
    """Service classes are implemented as descriptors:
    They are not fully fledged service objects until
    they are called second time. 'common' service is
    an exception because it will always be used to fetch
    service versions first."""

    initialized = False

    def _bind_resources(self):
        pass

    def __get__(self, obj, objtype):
        if self.initialized:
            return self

        self.initialized = True

        logger.debug('initializing %s service' % self.__class__.__name__)
        self._bind_resources()
        return self


# This class is used for instance descriptors
# http://blog.brianbeck.com/post/74086029/instance-descriptors
class InstanceDescriptorMixin(object):

    def __getattribute__(self, name):
        value = object.__getattribute__(self, name)
        if hasattr(value, '__get__'):
            value = value.__get__(self, self.__class__)
        return value


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


class TimeFilter(object):

    def __init__(self, start, end):
        self.start = start.strftime('%s')
        self.end = end.strftime('%s')

    @classmethod
    def parse_range(cls, string):
        start, end = timeutils.parse_range(string)
        return cls(start, end)
