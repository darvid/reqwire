import pathlib
import pip.models
import pip.req
import responses
import six

import reqwire.scaffold


def test_build_filename():
    filename = reqwire.scaffold.build_filename(
        '.', tag_name='test', extension='.in', prefix='build')
    assert filename == pathlib.Path('.') / 'build' / 'test.in'


def test_build_source_header_timestamp(fake_time, patch_datetime_now):
    header = reqwire.scaffold.build_source_header()
    assert header == reqwire.scaffold.build_source_header(timestamp=fake_time)


def test_build_source_header_format(fake_time, patch_datetime_now):
    header = reqwire.scaffold.build_source_header(
        index_url=pip.models.PyPI.simple_url,
        extra_index_urls=[pip.models.PyPI.simple_url],
        nested_cfiles={'constraints.txt'},
        nested_rfiles={'requirements.txt'})
    assert header == reqwire.scaffold.MODELINES_HEADER + six.text_type("""\
# Generated by reqwire on {}
-c constraints.txt
-r requirements.txt
--index-url https://pypi.python.org/simple
--extra-index-url https://pypi.python.org/simple
""".format(fake_time.strftime('%c')))


@responses.activate
def test_extend_source_file(mocker, tmpdir):
    responses.add(
        responses.GET, pip.models.PyPI.simple_url,
        body=b'<a>Flask</a>\n')
    src_dir = tmpdir.mkdir('src')
    src_file = src_dir.join('requirements.in')
    with mocker.patch('reqwire.helpers.requirements.resolve_specifier',
                      return_value=pip.req.InstallRequirement.from_line(
                          'Flask==0.11.1')):
        reqwire.scaffold.extend_source_file(
            working_directory=str(tmpdir),
            tag_name='requirements',
            specifiers=['flask'])
        assert 'flask==0.11.1' in src_file.read()


@responses.activate
def test_extend_source_file_wo_resolve_versions(mocker, tmpdir):
    responses.add(
        responses.GET, pip.models.PyPI.simple_url,
        body=b'<a>Flask</a>\n')
    src_dir = tmpdir.mkdir('src')
    src_file = src_dir.join('requirements.in')
    with mocker.patch('reqwire.helpers.requirements.resolve_specifier',
                      return_value=pip.req.InstallRequirement.from_line(
                          'Flask')):
        reqwire.scaffold.extend_source_file(
            working_directory=str(tmpdir),
            tag_name='requirements',
            resolve_versions=False,
            specifiers=['flask'])
        assert 'flask' in src_file.read(), src_file.read()


def test_init_source_dir(tmpdir):
    reqwire.scaffold.init_source_dir(str(tmpdir))
    assert tmpdir.join('src').exists()
    # assert tmpdir.join('src').stat().mode & 0o777 == 0o777
