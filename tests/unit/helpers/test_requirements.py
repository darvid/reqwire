import pip.exceptions
import pip.models
import pip.req
import pytest
import responses

import reqwire.helpers.requirements


@pytest.fixture
def ireq():
    return pip.req.InstallRequirement.from_line('reqwire==0.1a1')


def test_hashable_ireq_from_ireq(ireq):
    hireq = reqwire.helpers.requirements.HashableInstallRequirement.from_ireq(
        ireq=ireq)
    assert hireq.comes_from == ireq.comes_from
    assert hireq.source_dir == ireq.source_dir
    assert hireq.editable == ireq.editable
    assert hireq.link == ireq.link
    assert hireq.as_egg == ireq.as_egg
    assert hireq.update == ireq.update
    assert hireq.pycompile == ireq.pycompile
    assert hireq.markers == ireq.markers
    assert hireq.isolated == ireq.isolated
    assert hireq.options == ireq.options
    assert hireq._wheel_cache == ireq._wheel_cache
    assert hireq.constraint == ireq.constraint


def test_hashable_ireq_hashable(ireq):
    ireq2 = pip.req.InstallRequirement.from_line(str(ireq))
    assert hash(ireq) != hash(ireq2)
    hireq = reqwire.helpers.requirements.HashableInstallRequirement.from_ireq(
        ireq=ireq)
    hireq2 = reqwire.helpers.requirements.HashableInstallRequirement.from_ireq(
        ireq=ireq2)
    assert hash(hireq) == hash(hireq2)
    assert hireq == hireq2


@responses.activate
def test_get_canonical_name():
    responses.add(
        responses.GET, pip.models.PyPI.simple_url,
        body=b'<a>Flask</a>\n<a>Jinja2</a>')
    name = reqwire.helpers.requirements.get_canonical_name('jinja2')
    assert name == 'Jinja2'
    with pytest.raises(pip.exceptions.DistributionNotFound):
        name = reqwire.helpers.requirements.get_canonical_name('Jinja3')


def test_requirements_from_line():
    assert reqwire.helpers.requirements.HashableInstallRequirement.from_line(
        'reqwire') is not None


def test_resolve_specifier_wihout_resolve_versions(ireq):
    requirement = reqwire.helpers.requirements.resolve_specifier(
        'reqwire', resolve_versions=False)
    assert not requirement.is_pinned
