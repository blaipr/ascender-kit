"""Which environment variable wins when more than one names the same setting.

Three prefixes reach the same arguments. `ASCENDER_` is what the client
documents, `CONTROLLER_` is what it read before the rebrand, and `TOWER_` is
what awxkit read before that. A script written against any of them has to keep
working, so none of the three can simply be dropped, and the only question a
reader needs answered is which one wins when two are set at once.
"""

import pytest

from ascenderkit.cli.format import env_default


def test_the_ascender_name_wins():
    env = {'ASCENDER_HOST': 'new', 'CONTROLLER_HOST': 'middle', 'TOWER_HOST': 'old'}
    assert env_default(env, 'HOST', 'fallback') == 'new'


def test_the_controller_name_wins_over_the_tower_one():
    env = {'CONTROLLER_HOST': 'middle', 'TOWER_HOST': 'old'}
    assert env_default(env, 'HOST', 'fallback') == 'middle'


@pytest.mark.parametrize('prefix', ['ASCENDER_', 'CONTROLLER_', 'TOWER_'])
def test_any_one_of_the_three_on_its_own_is_read(prefix):
    assert env_default({prefix + 'USERNAME': 'mary'}, 'USERNAME', 'admin') == 'mary'


def test_nothing_set_falls_back():
    assert env_default({}, 'USERNAME', 'admin') == 'admin'


def test_a_name_that_is_set_but_empty_still_wins():
    """`env.get(name, other)` returned an empty value rather than looking on,
    and a deployment that exports an empty token to mean "no token" relies on
    it, so the ordered lookup has to do the same.
    """
    assert env_default({'ASCENDER_PASSWORD': ''}, 'PASSWORD', 'password') == ''
    assert env_default({'TOWER_PASSWORD': '', 'ASCENDER_PASSWORD': 'set'}, 'PASSWORD', 'password') == 'set'


def test_the_oauth_token_name_is_tried_before_the_short_one():
    """Both spellings exist for the token, across all three prefixes, and the
    full name is the one the login command prints.
    """
    env = {'ASCENDER_OAUTH_TOKEN': 'full', 'ASCENDER_TOKEN': 'short'}
    assert env_default(env, 'OAUTH_TOKEN', '', extra=('TOKEN',)) == 'full'


def test_a_newer_prefix_beats_a_longer_name():
    """`ASCENDER_TOKEN` is preferred over `CONTROLLER_OAUTH_TOKEN`: the prefix
    says which release wrote the script, and the suffix is only a spelling.
    """
    env = {'ASCENDER_TOKEN': 'short', 'CONTROLLER_OAUTH_TOKEN': 'full'}
    assert env_default(env, 'OAUTH_TOKEN', '', extra=('TOKEN',)) == 'short'


def test_the_old_chain_keeps_its_own_order():
    """`CONTROLLER_TOKEN` came before `TOWER_OAUTH_TOKEN` before this change,
    and still does, so adding a prefix on top reorders nothing below it.
    """
    env = {'CONTROLLER_TOKEN': 'middle', 'TOWER_OAUTH_TOKEN': 'old'}
    assert env_default(env, 'OAUTH_TOKEN', '', extra=('TOKEN',)) == 'middle'
