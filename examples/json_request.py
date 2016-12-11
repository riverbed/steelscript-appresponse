# Create a clip from a job


from steelscript.common.service import Service, UserAuth

host = '<hostname>'

username = '<username>'

password = '<password>'

auth = UserAuth(username=username, password=password)

service = Service('AppResponse', host=host, auth=auth)

# Get a list of packet capture jobs

uri = '/api/npm.packet_capture/1.0/jobs'
jobs = service.conn.json_request('GET', uri)


# Create a clip from a job

uri = '/api/npm.clips/1.0/clips'

config = dict(job_id='<job_id>',
              start_time='<start_epoch_time>',
              end_time='<end_epoch_time>')

data = dict(config=config)
resp = service.conn.json_request('POST', uri, body=data)
