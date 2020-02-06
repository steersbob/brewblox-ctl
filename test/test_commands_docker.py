"""
Tests brewblox_ctl.commands.docker
"""


from unittest.mock import call

import pytest
from click.testing import CliRunner

from brewblox_ctl.commands import docker

TESTED = docker.__name__


def invoke(*args, _ok=True, **kwargs):
    result = CliRunner().invoke(*args, **kwargs)
    if bool(result.exception) is _ok:
        print(result.stdout)
        raise AssertionError('{}, expected exc: {}'.format(result, _ok))


@pytest.fixture
def m_utils(mocker):
    m = mocker.patch(TESTED + '.utils')
    m.optsudo.return_value = 'SUDO '
    return m


@pytest.fixture
def m_sh(mocker):
    m = mocker.patch(TESTED + '.sh')
    return m


def test_up(m_utils, m_sh):
    invoke(docker.up)
    m_sh.assert_called_once_with('SUDO docker-compose up -d --remove-orphans')


def test_down(m_utils, m_sh):
    invoke(docker.down)
    m_sh.assert_called_once_with('SUDO docker-compose down --remove-orphans')


def test_restart(m_utils, m_sh):
    invoke(docker.restart)
    m_sh.assert_has_calls([
        call('SUDO docker-compose down --remove-orphans'),
        call('SUDO docker-compose up -d'),
    ])


def test_follow(m_utils, m_sh):
    invoke(docker.follow, 'spark-one spark-two')
    m_sh.assert_called_with('SUDO docker-compose logs --follow spark-one spark-two')
    invoke(docker.follow)
    m_sh.assert_called_with('SUDO docker-compose logs --follow ')


def test_kill(m_utils, m_sh):
    invoke(docker.kill)
    m_sh.assert_called_once_with('SUDO docker rm --force $(SUDO docker ps -aq)', check=False)
