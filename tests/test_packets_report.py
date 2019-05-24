import pytest

from steelscript.appresponse.core.types import Key, Value
from steelscript.appresponse.core.reports import DataDef, Report, SourceProxy

from tests.settings import PACKETS_KEY_COLS, PACKETS_VALUE_COLS


@pytest.fixture
def packet_columns():
    key_cols = [Key(key) for key in PACKETS_KEY_COLS]
    value_cols = [Value(key) for key in PACKETS_VALUE_COLS]
    return key_cols, value_cols


@pytest.fixture
def capture_jobs(app):
    return app.capture.get_jobs()


@pytest.fixture
def packets_source(capture_jobs):
    if len(capture_jobs) > 0:
        return capture_jobs[0]
    return None


@pytest.fixture
def packets_report_data_def(app, packets_source,
                            packet_columns, report_time_frame):
    granularity = 60
    resolution = 120
    cols = packet_columns[0] + packet_columns[1]
    source_proxy = SourceProxy(packets_source)
    data_def = DataDef(source=source_proxy, columns=cols,
                       time_range=report_time_frame, granularity=granularity,
                       resolution=resolution)
    return data_def


@pytest.fixture
def packet_report_columns(app):
    columns = app.reports.sources.get('packets', {}).get('columns')
    return columns


@pytest.fixture
def report_time_frame():
    return "previous hour"


class TestPacketsReport:
    def test_assert_capture_jobs(self, capture_jobs):
        assert len(capture_jobs) > 0

    @pytest.mark.parametrize("column_name, is_key, exists", [
        ('start_time', True, True),
        ('end_time', True, True),
        ('cli_tcp.ip', True, True),
        ('somefieldthatdoesnotexistever', True, False),
        ('sum_web.packets', False, True),
        ('avg_tcp.network_time_c2s', False, True),
        ('avg_cifs.data_transfer_time', False, True)
    ])
    def test_packets_cols_are_valid(self, column_name, is_key,
                                    exists, packet_report_columns):
        col = packet_report_columns.get(column_name)
        col_exists = True if col is not None else False
        assert col_exists == exists
        if exists:
            assert col.get('grouped_by', False) == is_key

    def test_execute_report(self, app, packets_report_data_def):
        report = Report(app)
        report.add(packets_report_data_def)
        report.run()
        legend = sorted(report.get_legend())
        report_data = report.get_data()

        assert legend == sorted(PACKETS_KEY_COLS + PACKETS_VALUE_COLS)
        assert len(report_data) > 0
        assert len(report_data[1]) == len(PACKETS_KEY_COLS + PACKETS_VALUE_COLS)
