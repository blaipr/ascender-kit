"""Tests that need a running Ascender.

The whole directory is skipped unless a host is set, so `pytest
tests/` stays offline by default and CI is unaffected until it is pointed at a
server. To run them:

    export ASCENDER_HOST=https://ascender.example.org
    export ASCENDER_USERNAME=admin ASCENDER_PASSWORD=...
    export ASCENDER_VERIFY_SSL=false      # self-signed development servers
    pytest tests/integration -v
"""

import os
import subprocess

import pytest

from ascenderkit.cli.format import env_default

HOST = env_default(os.environ, 'HOST', None)

# Without a server there is nothing here to run, so do not collect it at all.
# A skip marker would still build the fixtures and report a wall of errors.
if not HOST:
    collect_ignore_glob = ['test_*.py']


def pytest_collection_modifyitems(items):
    for item in items:
        item.add_marker(pytest.mark.integration)


@pytest.fixture(scope='session')
def insecure():
    """`-k` when the server presents a certificate we should not verify."""
    verify = env_default(os.environ, 'VERIFY_SSL', 'true').lower()
    return ['-k'] if verify in ('false', 'f', 'no', 'n', '0', 'off') else []


@pytest.fixture(scope='session')
def ascender(insecure):
    """Run the CLI, returning (returncode, stdout, stderr)."""

    def run(*args, stdin=None, timeout=300):
        proc = subprocess.run(
            ['ascender', *insecure, *args],
            input=stdin,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return proc.returncode, proc.stdout, proc.stderr

    return run


@pytest.fixture(scope='session')
def api():
    """A configured ApiV2, for the library rather than the CLI."""
    from ascenderkit import api as _api, config
    from ascenderkit.utils import PseudoNamespace

    config.base_url = HOST
    config.assume_untrusted = env_default(os.environ, 'VERIFY_SSL', 'true').lower() in ('false', 'f', 'no', 'n', '0', 'off')
    config.use_sessions = True
    config.credentials = PseudoNamespace(
        {'default': {'username': env_default(os.environ, 'USERNAME', 'admin'), 'password': env_default(os.environ, 'PASSWORD', '')}}
    )
    root = _api.Api()
    root.load_session().get()
    return root.get().available_versions.v2.get()
