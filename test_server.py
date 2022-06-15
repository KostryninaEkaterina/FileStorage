import pytest
from FileStorageConnector import FileConnector, Metadata
from requests import HTTPError

link = FileConnector('http://127.0.0.1:9876')


@pytest.mark.get
@pytest.mark.parametrize('id, result_list, status_code', [
                                                          ('0', list(), 200),
                                                          ('1', list(), 200)])
def test_empty_get_id(id, result_list, status_code):
    result = link.get_without_params()['content']
    for elem in result:
        link.delete_by_id(elem['id'])
    result = link.get_by_params(dict(id=id))
    content, code = result['content'], result['status-code']
    assert content == result_list
    assert code == status_code


@pytest.mark.delete
def test_delete_without_parameters():
        with pytest.raises(HTTPError) as excinfo:
            link.delete_without_params()
        the_exeption = excinfo.value.response
        assert the_exeption.text == 'отсутствуют условия'
        assert the_exeption.status_code == 400


@pytest.mark.upload
@pytest.mark.parametrize('id, name, text', [('0', 'new_file.txt', 'Hello!'),
                                            ('1', 'new_file1.txt', 'Hello, world!')])
def test_upload(id, name, text):
    result = link.get_without_params()['content']
    for elem in result:
        link.delete_by_id(elem['id'])
    link.upload(text, Metadata(id=id, name=name))
    assert link.get_by_params(dict(id=id, name=name))['content'] \
           == link.get_without_params()['content']