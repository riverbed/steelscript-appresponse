
class PacketsService(object):
    """This class is responsible for managing capture jobs"""

    def __init__(self, host, auth, name):
        self.packets = svcmgr.find(host, auth, name)
        self.jobs = packets.bind('jobs')

    def get_jobs(self):
        resp = self.jobs.execute('get')

        return [Job(self.get_job(item['id']))
                for item in resp.data['items']]

    def create_job(self):
        resp = self.jobs.execute('create')
        return Job(resp)

    def delete_jobs(self):
        return self.jobs.execute('bulk_delete')

    def bulk_start(self):
        return self.jobs.execute('bulk_start')

    def bulk_stop(self):
        return self.jobs.execute('bulk_stop')

    def get_job(self, id):
        datarep = self.packets.bind('job', id)
        resp = datarep.execute('get')
        return Job(resp)


class Job(object):

    def __init__(self, datarep):
        self.datarep = datarep

    def set(self):
        self.datarep.execute('set')

    def stop(self):
        self.datarep.execute('stop')

    def delete(self):
        self.datarep.execute('delete')

    def start(self):
        self.datarep.execute('start')

    def clear_packets(self):
        self.datarep.execute('clear_packets')

    def get_stats(self):
        return self.datarep.execute('get_stats')
