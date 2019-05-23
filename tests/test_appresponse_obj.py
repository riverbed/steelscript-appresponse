from steelscript.appresponse.core.capture import PacketCapture20
from tests.settings import ARX_ENDPOINT


class TestAppResponseObj:
    def test_connection(self, app, user_auth):
        # assert app.host == ARX_ENDPOINT
        import pdb; pdb.set_trace()
        assert app.auth == user_auth
        assert isinstance(app.capture, PacketCapture20)
