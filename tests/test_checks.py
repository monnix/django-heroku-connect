import pytest
from django.core import checks
from django.core.management import call_command
from django.core.management.base import SystemCheckError

from heroku_connect.checks import _check_foreign_key_target, _check_unique_sf_object_name
from heroku_connect.db.models import HerokuConnectModel


def test_check_foreign_key_target():
    errors = _check_foreign_key_target(None)
    assert checks.Error(
        "testapp.OtherModel.number should point to an External ID or the 'sf_id', not 'id'.",
        hint="Specify the 'to_field' argument.",
        id='heroku_connect.E005',
    ) in errors


def test_check_unique_sf_object_name(monkeypatch):
    class ModelA(HerokuConnectModel):
        sf_object_name = 'A'

        class Meta:
            app_label = 'test'
            abstract = True

    class ModelB(HerokuConnectModel):
        sf_object_name = 'A'  # Same name as ModelA

        class Meta:
            app_label = 'test'
            abstract = True

    monkeypatch.setattr('heroku_connect.checks.get_heroku_connect_models',
                        lambda: [ModelA, ModelB])
    errors = _check_unique_sf_object_name(None)
    assert checks.Error(
        "test.ModelB.sf_object_name clashes with another model.",
        hint="Specify a unique 'sf_object_name' argument.",
        id='heroku_connect.E006',
    ) in errors


def test_django_check():
    with pytest.raises(SystemCheckError):
        call_command('check')
