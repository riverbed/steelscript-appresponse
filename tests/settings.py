import os

USERNAME = os.environ.get('USERNAME')
PASSWORD = os.environ.get('PASSWORD')
AR_ENDPOINT = os.environ.get('ARX_ENDPOINT')
AR11_ADVANCED_FEATURES = os.environ.get('AR11_ADVANCED_FEATURES', 'False')
WIREMOCK_SERVER = os.environ.get('WIREMOCK_SERVER')
WIREMOCK_START_RECORDING = '__admin/recordings/start'
WIREMOCK_STOP_RECORDING = '__admin/recordings/stop'
WIREMOCK_SNAPSHOT = "__admin/recordings/snapshot"
WIREMOCK_RESET = "/__admin/mappings/reset"

PACKETS_KEY_COLS = [u'start_time', u'end_time',
                    u'cli_tcp.ip', u'srv_tcp.port_name']
PACKETS_VALUE_COLS = [u'avg_cifs.data_transfer_time',
                      u'sum_srv_tcp.payload_packets',
                      u'avg_tcp.network_time_c2s', u'sum_web.packets']
