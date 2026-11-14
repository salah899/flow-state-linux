import pytest

from flow_state.data.database import Database
from flow_state.services import AppServices


@pytest.fixture
def services():
    s = AppServices(Database(":memory:"))
    yield s
    s.close()
