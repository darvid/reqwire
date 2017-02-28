import datetime

from click.testing import CliRunner
import pytest


FAKE_TIME = datetime.datetime(2020, 1, 1, 0, 0, 0)


@pytest.fixture
def fake_time():
    return FAKE_TIME


@pytest.fixture
def patch_datetime_now(fake_time, mocker):
    class mocked_datetime:
        @classmethod
        def now(cls):
            return fake_time

    mocker.patch('datetime.datetime', mocked_datetime)


@pytest.fixture(scope='session')
def cli_runner():
    return CliRunner()
