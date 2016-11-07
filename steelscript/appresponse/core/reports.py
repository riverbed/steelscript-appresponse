import svcmgr
from collections import defaultdict

def build_data_def(self, **kwargs):

    data_def = {}
    data_def['reference'] = 'pcap file'
    data_def['source'] = dict(name='packets', path='fs/admin/packets.pcap')
    data_def['group_by'] = ['start_time']
    data_def['time'] = dict(granularity='0.001')
    data_def['columns'] = ['start_time', 'sum_network.total_bytes']

    return data_def


class ProbeReportService(object):

    def __init__(self, svcmgr, host, auth, name):
        reports = svcmgr.find(svcmgr.host, svcmgr.auth, name)
        self.instances = reports.bind('instances')

    def create_report(self, **kwargs):

        config = {'data_defs': [build_data_def(**kwargs)]}

        # link = 'create_sync' if sync else 'create'
        resp = self.instances.execute('create', _data=config)
        return Instance(resp)

    def create_instance(self, data_defs):
        resp = self.instances.execute('create', _data=data_defs)
        return Instance(resp)

    def get_instances(self):
        resp = self.instances.execute('get')

        return [Instance(self.get_instance_by_id(instance['id'])
                for instance in resp.data['items'])]

    def bulk_delete(self):
        self.instances.execute('bulk_delete')

    def get_instance_by_id(self, _id):
        resp = self.instances.execute(id=_id)
        return ReportInstance(resp)


class ReportInstance(object):
    """Instance class should """
    def __init__(self, datarep):
        self.datarep = datarep

    def get_status(self):
        return self.datarep.execute('get_status').data

    def get_data(self):
        return self.datarep.execute('get_data').data

    def delete(self):
        return self.datarep.execute('delete')


class Report(object):
    # Needs to support multiple instances
    def __init__(self, appresponse):
        self.appresponse = appresponse
        self.data_defs = defaultdict(list)
        self.instance = None

    def add(self, **kwargs):
        self.data_defs['data_defs'].append(build_data_def(**kwargs))

    def run(self):
        datarep = self.appresponse.reports.create_instance(self.data_defs)
        self.instance = ReportInstance(datarep)

    def get_data(self):
        return self.datarep.execute('get_data').data

class data_def(object)

"""
arx = AppResponse()
report = arx.create_view(**kwargs)
report.get_data()

arx = AppResponse()
report = Report(arx)
report.add(**kwargs)
report.add(**kwargs)
report.run()
report.get_data()
"""