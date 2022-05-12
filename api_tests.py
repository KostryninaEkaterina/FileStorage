from unittest.case import TestCase

from requests import HTTPError

from FileStorageConnector import FileConnector, Metadata


class EmptyStorageTest(TestCase):
    """Тестирование при пустом наполнении сервера"""

    def __init__(self, methodName: str = ...):
        super().__init__(methodName)
        self.fsc = FileConnector('http://127.0.0.1:2207')

    def setUp(self) -> None:
        result = self.fsc.get_without_params()['content']
        for elem in result:
            self.fsc.delete_by_id(elem['id'])

    def tearDown(self) -> None:
        result = self.fsc.get_without_params()['content']
        for elem in result:
            self.fsc.delete_by_id(elem['id'])

    def test_empty_get_id(self):
        result = self.fsc.get_by_params(dict(id='0'))
        content, code = result['content'], result['status-code']
        self.assertEqual(content, list())
        self.assertEqual(code, 200)

    def test_empty_get_name(self):
        result = self.fsc.get_by_params(dict(name='new.txt'))
        content, code = result['content'], result['status-code']
        self.assertEqual(content, list())
        self.assertEqual(code, 200)

    def test_empty_get_size_and_tag(self):
        result = self.fsc.get_by_params(dict(size=7.0, tag=''))
        content, code = result['content'], result['status-code']
        self.assertEqual(content, list())
        self.assertEqual(code, 200)

    def test_empty_get_empty_parameters(self):
        result = self.fsc.get_by_params(dict(id='', name='', tag="", size="", mimeType="", modificationTime=''))
        content, code = result['content'], result['status-code']
        self.assertEqual(content, list())
        self.assertEqual(code, 200)

    def test_empty_get_non_existent_parameter(self):
        result = self.fsc.get_by_params(dict(cat='meow', id='6', name='new_cat.jpg'))
        content, code = result['content'], result['status-code']
        self.assertEqual(content, list())
        self.assertEqual(code, 200)

    def test_empty_delete_without_parameters(self):
        with self.assertRaises(HTTPError) as cm:
            self.fsc.delete_without_params()
        the_exception = cm.exception
        self.assertEqual(the_exception.response.status_code, 400)
        self.assertEqual(the_exception.response.content.decode('utf-8'), "отсутствуют условия")

    def test_empty_delete_by_id(self):
        result = self.fsc.delete_by_params(dict(id='0'))
        content, code = result['content'], result['status-code']
        self.assertEqual(content, '0 files deleted')
        self.assertEqual(code, 200)

    def test_empty_delete_by_name(self):
        result = self.fsc.delete_by_params(dict(name='new.txt'))
        content, code = result['content'], result['status-code']
        self.assertEqual(content, '0 files deleted')
        self.assertEqual(code, 200)

    def test_empty_delete_by_params(self):
        result = self.fsc.delete_by_params(dict(id='6', name='new_cat.jpg', size=10.0))
        content, code = result['content'], result['status-code']
        self.assertEqual(content, '0 files deleted')
        self.assertEqual(code, 200)

    def test_upload(self):
        self.fsc.upload('Hello!', Metadata(id='5', name='new_file.txt'))
        self.assertEqual(self.fsc.get_by_params(dict(id='5', name='new_file.txt'))['content'],
                         self.fsc.get_without_params()['content'])

    def test_upload_without_data(self):
        self.fsc.upload(meta=Metadata(id='5', name='new_file.txt'))
        self.assertEqual(self.fsc.get_by_params(dict(id='5', name='new_file.txt'))['content'],
                         self.fsc.get_without_params()['content'])

    def test_download_by_id(self):
        with self.assertRaises(HTTPError) as dl:
            self.fsc.download_by_params(dict(id=0))
        the_exception = dl.exception
        self.assertEqual(the_exception.response.status_code, 404)
        self.assertEqual(the_exception.response.content.decode('utf-8'), "файл не существует")

    def test_download_by_params(self):
        with self.assertRaises(HTTPError) as dl:
            self.fsc.download_by_params(dict(id=0, cat='meow'))
        the_exception = dl.exception
        self.assertEqual(the_exception.response.status_code, 404)
        self.assertEqual(the_exception.response.content.decode('utf-8'), "файл не существует")

    def test_download_non_existent_parameter(self):
        with self.assertRaises(HTTPError) as dl:
            self.fsc.download_by_params(dict(cat='meow'))
        the_exception = dl.exception
        self.assertEqual(the_exception.response.status_code, 400)
        self.assertEqual(the_exception.response.content.decode('utf-8'), "отсутствуют условия")

    def test_download_without_params(self):
        with self.assertRaises(HTTPError) as dl:
            self.fsc.download_without_params()
        the_exception = dl.exception
        self.assertEqual(the_exception.response.status_code, 400)
        self.assertEqual(the_exception.response.content.decode('utf-8'), "отсутствуют условия")



class SingleFileStorageTest(TestCase):
    def __init__(self, methodName: str = ...):
        super().__init__(methodName)
        self.fsc = FileConnector('http://127.0.0.1:2207')

    def setUp(self) -> None:
        self.fsc.upload('Hello!', Metadata(id='5', name='new_file.txt'))

    def tearDown(self) -> None:
        result = self.fsc.get_without_params()['content']
        for elem in result:
            self.fsc.delete_by_id(elem['id'])

    def test_get(self):
        result = self.fsc.get_without_params()
        content, code = result['content'], result['status-code']
        self.assertEqual(content, [(dict(id='5', name='new_file.txt',
                                         tag='', size=6.0, mimeType='text/plain',
                                         modificationTime=self.fsc.get_time_now()))])
        self.assertEqual(code, 200)

    def test_get_by_id(self):
        result = self.fsc.get_without_params()
        print(result)

    def test_get_by_params(self):
        test_dict = {
            'id': 5,
        }
        result = self.fsc.get_by_params(test_dict)
        print(result)

    def test_download(self):
        self.assertEqual(self.fsc.download_by_id('5'), 'Hello!')

    def test_delete(self):
        self.assertEqual(self.fsc.delete_by_id('5'), 200)
