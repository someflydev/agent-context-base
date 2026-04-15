import datetime
from fastapi import Request
from src.analytics_workbench.filters import parse_filter_state

class MockRequest:
    def __init__(self, query_params):
        self._query_params = query_params
        
    @property
    def query_params(self):
        class QP:
            def __init__(self, d):
                self.d = d
            def get(self, key, default=None):
                return self.d.get(key, [default])[0] if key in self.d and self.d[key] else default
            def getlist(self, key):
                return self.d.get(key, [])
        return QP(self._query_params)

def test_parse_empty_query():
    req = MockRequest({})
    fs = parse_filter_state(req) # type: ignore
    assert fs.date_from is None
    assert fs.date_to is None
    assert fs.services == []
    assert fs.severity == []
    assert fs.environment == []

def test_parse_multi_service():
    req = MockRequest({"services": ["a", "b, c"]})
    fs = parse_filter_state(req) # type: ignore
    assert fs.services == ["a", "b", "c"]

def test_parse_date_range():
    req = MockRequest({"date_from": ["2025-01-01"], "date_to": ["2025-12-31"]})
    fs = parse_filter_state(req) # type: ignore
    assert fs.date_from == datetime.date(2025, 1, 1)
    assert fs.date_to == datetime.date(2025, 12, 31)
