import pytest
from FileStorageConnector import FileConnector

link = FileConnector('http://127.0.0.1:9876')


@pytest.fixture(autouse=True)
def clean_file_storage():
    result = link.get_without_params()['content']
    for elem in result:
        link.delete_by_id(elem['id'])