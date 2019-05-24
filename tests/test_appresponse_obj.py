from steelscript.appresponse.core.capture import PacketCapture20


class TestAppResponseObj:
    def test_connection(self, app, user_auth):
        assert app.auth == user_auth
        assert isinstance(app.capture, PacketCapture20)
