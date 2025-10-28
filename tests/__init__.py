import os
import tempfile
import pytest
from flask import Flask

# tests/__init__.py
# Test package initialization and common pytest fixtures for Flask apps.


try:
    # Try to import an application factory and SQLAlchemy db from the application package.
    # Adjust import path if your app package name is different (e.g. from myapp import create_app, db).
    from app import create_app, db as _db  # type: ignore
except Exception:
    create_app = None
    _db = None



def _make_app():
    if create_app:
        # Prefer application factory if available; allow the factory to accept config dicts.
        try:
            return create_app({"TESTING": True})
        except TypeError:
            return create_app()
    # Fallback to a minimal Flask application for tests when no factory is present.
    app = Flask(__name__)
    app.config.update(TESTING=True)
    return app


@pytest.fixture(scope="session")
def app():
    """
    Session-scoped Flask application for tests.
    If SQLAlchemy `db` is available, create a temporary sqlite database for the session.
    """
    app = _make_app()

    if _db is not None:
        # create a temporary file-backed sqlite DB so multiple connections work
        fd, db_path = tempfile.mkstemp(prefix="test_db_", suffix=".sqlite")
        app.config.setdefault("SQLALCHEMY_DATABASE_URI", f"sqlite:///{db_path}")
        app.config.setdefault("SQLALCHEMY_TRACK_MODIFICATIONS", False)

        with app.app_context():
            _db.create_all()

        yield app

        with app.app_context():
            _db.session.remove()
            _db.drop_all()

        os.close(fd)
        try:
            os.unlink(db_path)
        except OSError:
            pass
    else:
        yield app


@pytest.fixture
def client(app):
    """Test client for making HTTP requests to the app."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Click runner for invoking CLI commands registered on the app."""
    return app.test_cli_runner()