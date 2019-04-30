import os

USERNAME = os.environ.get('USERNAME')
PASSWORD = os.environ.get('PASSWORD')
ARX_ENDPOINT = os.environ.get('ARX_ENDPOINT')
AR11_ADVANCED_FEATURES = os.environ.get('AR11_ADVANCED_FEATURES', 'False')
WIREMOCK_SERVER = "http://localhost:8080"
WIREMOCK_START_RECORDING = '__admin/recordings/start'
WIREMOCK_STOP_RECORDING = '__admin/recordings/stop'

PACKETS_KEY_COLS = [u'start_time', u'end_time', u'cli_tcp.ip', u'srv_tcp.ip']
PACKETS_VALUE_COLS = [u'avg_cifs.data_transfer_time', u'avg_sql.data_transfer_time',
                      u'avg_tcp.network_time_c2s', u'sum_web.packets']