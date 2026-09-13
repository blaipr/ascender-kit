import importlib

import pytest

pytest.importorskip('sphinxcontrib.autoprogram', reason='needs the docs extra')


def test_extension_imports_without_a_running_ascender(monkeypatch):
    """The module used to end in `parser = render()`, so importing it raised
    SystemExit unless ASCENDER_HOST pointed at a live server. Sphinx could
    not load the extension at all, which is why no workflow builds the docs.
    """
    for prefix in ('ASCENDER_', 'CONTROLLER_', 'TOWER_'):
        for suffix in ('HOST', 'USERNAME', 'PASSWORD'):
            monkeypatch.delenv(prefix + suffix, raising=False)

    module = importlib.import_module('ascenderkit.cli.sphinx')
    importlib.reload(module)

    assert hasattr(module, 'setup')
    assert 'parser' not in vars(module), 'parser should not be built until it is asked for'


def test_asking_for_the_parser_is_what_needs_the_server(monkeypatch):
    for prefix in ('ASCENDER_', 'CONTROLLER_', 'TOWER_'):
        monkeypatch.delenv(prefix + 'HOST', raising=False)

    module = importlib.reload(importlib.import_module('ascenderkit.cli.sphinx'))

    with pytest.raises(SystemExit, match='ASCENDER_HOST'):
        module.parser


def test_unknown_attributes_still_raise_attribute_error():
    module = importlib.import_module('ascenderkit.cli.sphinx')

    with pytest.raises(AttributeError):
        module.no_such_thing
