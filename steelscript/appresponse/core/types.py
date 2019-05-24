# Copyright (c) 2019 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.

import logging
import threading

from steelscript.common import timeutils
from steelscript.common.datastructures import DictObject

logger = logging.getLogger(__name__)


lock = threading.Lock()


class AppResponseException(Exception):
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
        # Add threading lock to ensure that the resources are all
        # allocated before claiming to be initialized.
        with lock:
            logger.debug('Checking %s service' % self.__class__.__name__)
            if self.initialized:
                return self

            logger.debug('Initializing %s service' % self.__class__.__name__)
            self._bind_resources()
            logger.debug('Resources bound for %s' % self.__class__.__name__)

            self.initialized = True

            return self


# This class is used for instance descriptors
# http://blog.brianbeck.com/post/74086029/instance-descriptors
class InstanceDescriptorMixin(object):

    def __getattribute__(self, name):
        value = object.__getattribute__(self, name)
        if hasattr(value, '__get__'):
            value = value.__get__(self, self.__class__)
        return value


class ResourceObject(object):

    resource = None

    property_names = None

    def __init__(self, data, servicedef=None, datarep=None):
        logger.debug('Initialized {} object with data {}'
                     .format(self.__class__.__name__, data))
        self.data = DictObject.create_from_dict(data)
        if not datarep:
            self.datarep = servicedef.bind(self.resource, id=self.data.id)
        else:
            self.datarep = datarep

    def get_property_values(self):
        return None

    def print_properties(self):
        property_values = self.get_property_values()
        if (property_values is not None and
                self.property_names is not None):
            for num, value in enumerate(property_values, start=0):
                if isinstance(value, dict):
                    for k, v in value.items():
                        print("{}->{}: {}"
                              .format(self.property_names[num], k, v))
                else:
                    print("{}: {}"
                          .format(self.property_names[num], value))
        else:
            raise NotImplementedError("Property names and Property "
                                      "values have to be implemented")

    @property
    def id(self):
        return self.data.id

    @property
    def name(self):
        if hasattr(self.data, 'name'):
            return self.data.name
        elif hasattr(self.data.config, 'name'):
            return self.data.config.name
        return self.id


class Column(object):

    def __init__(self, name, key=False):
        self.name = name
        self.key = key

    def __str__(self):
        return self.name

    def __repr__(self):
        msg = '<{cls}(name={name} key={key})>'
        return msg.format(cls=self.__class__.__name__, **self.__dict__)


class Key(Column):

    def __init__(self, name):
        super(Key, self).__init__(name, key=True)


class Value(Column):

    def __init__(self, name):
        super(Value, self).__init__(name, key=False)


class TrafficFilter(object):

    valid_types = ['STEELFILTER', 'WIRESHARK', 'BPF']

    def __init__(self, value, type_=None, id_=None):
        """Initialize a TrafficFilter object.

        :param value: string, the actual filter expression
        :param type_: string, 'STEELFILTER' or 'WIRESHARK' or 'BPF', defaults
            to 'STEELFILTER'

            example STEELFILTER expression:
                <column_id>==<value1> OR <column_id>==<value2>
            where "column_id" refers to the ID of the column of which the
            records are filtered. The column should be supported by the
            source, and is either a key column or a metric column if
            the source supports filters on metric columns.

            example WIRESHARK expression: ip.addr==1.2.3.4 or ip.addr==1.1.1.1

            example BPF expression: host 1.2.3.4 or host 1.1.1.1
        :param id_: string, ID of the filter, optional

        """
        if not value:
            msg = 'Traffic filter expression required.'
            raise AppResponseException(msg)

        if type_ and type_.upper() not in self.valid_types:
            msg = ('Traffic filter type needs to be one of {}'
                   .format(self.valid_types))
            raise AppResponseException(msg)

        if type_ and type_.upper() == 'WIRESHARK' and not id_:
            # Wireshark filters are checked via ID to ensure they are
            # identical across multiple data defs within one report instance.
            # Use value as the ID if no id is provided to distinguish between
            # other wireshark filters in the same data def
            self.id = value
        else:
            self.id = id_
        self.type = type_.upper() if type_ else None
        self.value = value

    def as_dict(self):
        """Convert the object into dictionary"""

        ret = {}
        for k in ['id', 'type', 'value']:
            v = getattr(self, k, None)
            if v:
                ret[k] = v
        return ret


class TimeFilter(object):

    def __init__(self, start=None, end=None, duration=None, time_range=None):
        """Initialize a TimeFilter object.

         :param start: integer, start time in epoch seconds
         :param end: integer, end time in epoch seconds
         :param duration: string, time duration, i.e. '1 hour'
         :param time_range: string, time range, i.e. 'last 1 hour'
            or '4/21/13 4:00 to 4/21/13 5:00'

        """
        invalid = False

        if not start and not end and not duration and not time_range:
            # when querying file or clip, usually no time filters are provided
            self.start = None
            self.end = None

        elif start and end:
            if duration or time_range:
                invalid = True
            else:
                self.start = str(start)
                self.end = str(end)

        elif time_range:
            if start or end or duration:
                invalid = True
            else:
                start, end = timeutils.parse_range(time_range)
                self.start = str(timeutils.datetime_to_seconds(start))
                self.end = str(timeutils.datetime_to_seconds(end))

        elif duration:
            if not start and not end:
                invalid = True
            else:
                td = timeutils.parse_timedelta(duration).total_seconds()
                if start:
                    self.start = str(start)
                    self.end = str(int(start + td))
                else:
                    self.start = str(int(end - td))
                    self.end = str(end)

        elif start or end:
            invalid = True

        if invalid:
            msg = ('Start/end timestamps can not be derived from start "{}" '
                   'end "{}" duration "{}" time_range "{}".'
                   .format(start, end, duration, time_range))
            raise AppResponseException(msg)

    def __repr__(self):
        return "TimeFilter(start={}, end={})".format(self.start, self.end)
