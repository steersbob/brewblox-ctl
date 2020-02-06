"""
Tests brewblox_ctl.commands.install
"""


import pytest
from click.testing import CliRunner

from brewblox_ctl.commands import install

TESTED = install.__name__


def invoke(*args, _ok=True, **kwargs):
    result = CliRunner().invoke(*args, **kwargs)
    if bool(result.exception) is _ok:
        print(result.stdout)
        raise AssertionError('{}, expected exc: {}'.format(result, _ok))


@pytest.fixture(autouse=True)
def m_sleep(mocker):
    m = mocker.patch(TESTED + '.sleep')
    return m


@pytest.fixture
def m_utils(mocker):
    m = mocker.patch(TESTED + '.utils')
    m.optsudo.return_value = 'SUDO '
    m.docker_tag.side_effect = lambda v: v
    return m


@pytest.fixture
def m_sh(mocker):
    m = mocker.patch(TESTED + '.sh')
    return m


def test_install_short(m_utils, m_sh):
    m_utils.path_exists.return_value = False
    m_utils.command_exists.side_effect = [
        False,  # apt
        True,  # docker
        True,  # docker-compose
    ]
    invoke(install.install, '--use-defaults')
    assert m_sh.call_count == 3


def test_install_full(m_utils, m_sh):
    m_utils.path_exists.return_value = False
    m_utils.is_docker_user.return_value = False
    m_utils.command_exists.side_effect = [
        True,  # apt
        False,  # docker
        False,  # docker-compose
    ]
    invoke(install.install, '--use-defaults')
    assert m_sh.call_count == 7


def test_install_existing_declined(m_utils, m_sh):
    m_utils.path_exists.return_value = True
    m_utils.confirm.return_value = False
    m_utils.is_docker_user.return_value = False
    m_utils.command_exists.side_effect = [
        True,  # apt
        False,  # docker
        False,  # docker-compose
    ]
    invoke(install.install, '--no-use-defaults')
    assert m_sh.call_count == 0


def test_install_existing_continue(m_utils, m_sh):
    m_utils.path_exists.return_value = True
    m_utils.confirm.side_effect = [
        True,  # continue existing dir
        False  # no reboot
    ]
    m_utils.is_docker_user.return_value = True
    m_utils.command_exists.side_effect = [
        False,  # apt
        True,  # docker
        True,  # docker-compose
    ]
    invoke(install.install, '--no-use-defaults')
    assert m_sh.call_count == 2


def test_prepare_flasher(m_utils, m_sh):
    install.prepare_flasher('taggart', True)
    m_sh.assert_any_call('SUDO docker pull brewblox/firmware-flasher:taggart')
    m_sh.assert_any_call('SUDO docker-compose down')

    # No-op call
    m_sh.reset_mock()
    m_utils.path_exists.return_value = False

    install.prepare_flasher('taggart', False)
    m_sh.assert_not_called()


def test_run_flasher(m_utils, m_sh):
    install.run_flasher('taggart', 'do-stuff')
    m_sh.assert_called_with('SUDO docker run -it --rm --privileged brewblox/firmware-flasher:taggart do-stuff')


def test_flash(m_utils, m_sh):
    invoke(install.flash, '--release develop --pull')
    assert m_sh.call_count == 4
    m_sh.assert_called_with('SUDO docker run -it --rm --privileged brewblox/firmware-flasher:develop flash')


def test_bootloader(m_utils, m_sh):
    invoke(install.bootloader, '--release develop --pull --force')
    assert m_sh.call_count == 3
    m_sh.assert_called_with(
        'SUDO docker run -it --rm --privileged brewblox/firmware-flasher:develop flash-bootloader --force')


def test_wifi(m_utils, m_sh):
    invoke(install.wifi, '--release develop --pull')
    assert m_sh.call_count == 3