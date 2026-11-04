"""Regression: every Ask template's bind parameters must be recognised by SQLAlchemy text().

`:name::uuid` is NOT parsed as a bind parameter (the regex refuses a name followed by ':'), so the literal text
reaches Postgres and fails with 'syntax error at or near ":"'. Use CAST(:name AS uuid) instead.
"""
import inspect
import re
from unittest.mock import MagicMock

from app import ask_templates


def _captured_query(fn, **kwargs):
    db = MagicMock()
    db.execute.return_value.fetchone.return_value = None
    db.execute.return_value.fetchall.return_value = []
    fn(db, **kwargs)
    return db.execute.call_args_list[0].args[0]


def test_package_members_binds_package_id():
    q = _captured_query(
        ask_templates.package_members, package_id="550e8400-e29b-41d4-a716-446655440702", production_code="EXFTR"
    )
    # `package_id` would be missing with the old `:package_id::uuid`
    assert {"package_id", "production_code"} <= set(q._bindparams)


def test_no_template_uses_colon_cast_after_a_bind_param():
    src = inspect.getsource(ask_templates)
    assert not re.search(r":[a-z_]+::", src)


def test_every_template_accepts_production_code():
    """routes.py and ask_executor.py always add production_code to a template's params, whatever the intent."""
    for name, fn in ask_templates.TEMPLATES.items():
        assert "production_code" in inspect.signature(fn).parameters, name
