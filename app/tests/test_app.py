from main import app


def test_app_existe():
    assert app is not None


def test_app_em_modo_teste():
    app.config["TESTING"] = True
    assert app.config["TESTING"] is True