from unittest.case import TestCase

from requests import HTTPError, Response, request

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

    def test_upload_file_jpg(self):
        file = open('cat.jpg', mode='rb').read()
        self.fsc.upload(file, Metadata(id='1', name='new_cat.jpg'))
        self.assertEqual(self.fsc.get_by_params(dict(id='1', name='new_cat.jpg'))['content'],
                         self.fsc.get_without_params()['content'])

    def test_upload_without_data(self):
        self.fsc.upload(meta=Metadata(id='5', name='new_file.txt'))
        self.assertEqual(self.fsc.get_by_params(dict(id='5', name='new_file.txt'))['content'],
                         self.fsc.get_without_params()['content'])

    def test_upload_without_data_and_params(self):
        self.fsc.upload()
        self.assertEqual(self.fsc.get_by_params(dict(id='54321', name='54321'))['content'],
                         self.fsc.get_without_params()['content'])

    def test_upload_without_name(self):
        self.fsc.upload(meta=Metadata(id='8'))
        self.assertEqual(self.fsc.get_by_params(dict(id='8', name='8'))['content'],
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
    """
    Single File
     data = 'Hello!'
    [
    {
        "id": "5",
        "name": "new_file.txt",
        "tag": "",
        "size": 6.0,
        "mimeType": "text/plain",
        "modificationTime": time_now, format "year-month-day hour:minute:second"
    }
]
    """

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
        # ToDo сравнивать по элементам, для времени сделать сравнение с timedelta 5 сек
        result = self.fsc.get_without_params()
        content, code = result['content'], result['status-code']
        self.assertEqual(content, [(dict(id='5', name='new_file.txt',
                                         tag='', size=6.0, mimeType='text/plain',
                                         modificationTime=self.fsc.get_time_now()))])
        self.assertEqual(code, 200)

    def test_upload_new_name(self):
        self.fsc.upload('Hello!', Metadata(id='5', name='get.py'))
        self.assertEqual(self.fsc.get_by_params(dict(id='5', name='get.py'))['content'],
                         self.fsc.get_without_params()['content'])
        self.assertEqual(self.fsc.get_by_params(dict(id='5', name='get.py'))['status-code'],
                         self.fsc.get_without_params()['status-code'])

    def test_upload_without_data(self):
        self.fsc.upload(meta=Metadata(id='5', name='new_file.txt'))
        self.assertEqual(self.fsc.get_by_params(dict(id='5', name='new_file.txt'))['content'],
                         self.fsc.get_without_params()['content'])
        self.assertEqual(self.fsc.get_by_params(dict(id='5', name='new_file.txt'))['status-code'],
                         self.fsc.get_without_params()['status-code'])

    def test_upload_new_data(self):
        self.fsc.upload('Hello world!', Metadata(id='5', name='new_file.txt'))
        self.assertEqual(self.fsc.get_by_params(dict(id='5', name='new_file.txt'))['content'],
                         self.fsc.get_without_params()['content'])
        self.assertEqual(self.fsc.get_by_params(dict(id='5', name='new_file.txt'))['status-code'],
                         self.fsc.get_without_params()['status-code'])

    def test_delete_by_id(self):
        result = self.fsc.delete_by_params(dict(id='5'))
        content, code = result['content'], result['status-code']
        self.assertEqual(content, '1 files deleted')
        self.assertEqual(code, 200)

    def test_delete_by_name(self):
        result = self.fsc.delete_by_params(dict(name="new_file.txt"))
        content, code = result['content'], result['status-code']
        self.assertEqual(content, '1 files deleted')
        self.assertEqual(code, 200)

    def test_delete_by_other_id(self):
        result = self.fsc.delete_by_params(dict(id='345'))
        content, code = result['content'], result['status-code']
        self.assertEqual(content, '0 files deleted')
        self.assertEqual(code, 200)

    def test_download_by_id(self):
        result = self.fsc.download_by_params(dict(id='5'))
        content, code = result['content'], result['status-code']
        self.assertEqual(content, 'Hello!')
        self.assertEqual(code, 200)

    def test_download_by_parameters(self):
        result = self.fsc.download_by_params(dict(id='5', cat='meow'))
        content, code = result['content'], result['status-code']
        self.assertEqual(content, 'Hello!')
        self.assertEqual(code, 200)

    def test_download_by_other_id(self):
        with self.assertRaises(HTTPError) as dl:
            self.fsc.download_by_params(dict(id='43434'))
        the_exception = dl.exception
        self.assertEqual(the_exception.response.status_code, 404)
        self.assertEqual(the_exception.response.content.decode('utf-8'), "файл не существует")

    def test_download_by_2id(self):
        result = self.fsc.download_by_params(dict(id=['5', '6']))
        content, code = result['content'], result['status-code']
        self.assertEqual(content, 'Hello!')
        self.assertEqual(code, 200)


class FullFileStorageTest(TestCase):
    def __init__(self, methodName: str = ...):
        super().__init__(methodName)
        self.fsc = FileConnector('http://127.0.0.1:2207')

    def setUp(self) -> None:
        self.fsc.upload('Hello!', Metadata(id='1', name='new_file.txt', tag='test1'))
        self.fsc.upload('Hello!', Metadata(id='2', name='new_file1.txt', tag='test2'))
        self.fsc.upload('Hello!', Metadata(id='3', name='new_file2.txt', tag='test1'))
        self.fsc.upload('Hello!', Metadata(id='4', name='new_file.txt', tag='test2'))

    def tearDown(self) -> None:
        result = self.fsc.get_without_params()['content']
        for elem in result:
            self.fsc.delete_by_id(elem['id'])

    def test_get_by_id(self):
        result = self.fsc.get_by_params(dict(id='1'))
        content, code = result['content'], result['status-code']
        self.assertEqual(content, [(dict(id='1', name='new_file.txt', tag='test1',
                                         size=6.0, mimeType='text/plain',
                                         modificationTime=self.fsc.get_time_now()))])
        self.assertEqual(code, 200)

    def test_get_by_2id(self):
        result = self.fsc.get_by_params(dict(id=['1', '2']))
        content, code = result['content'], result['status-code']
        self.assertEqual(content, [(dict(id='1', name='new_file.txt', tag='test1',
                                         size=6.0, mimeType='text/plain',
                                         modificationTime=self.fsc.get_time_now())),
                                   (dict(id='2', name='new_file1.txt', tag='test2',
                                         size=6.0, mimeType='text/plain',
                                         modificationTime=self.fsc.get_time_now()))
                                   ])
        self.assertEqual(code, 200)

    def test_get_by_params(self):
        result = self.fsc.get_by_params(dict(id=['1', '2', '3', '4'],
                                             name='new_file.txt',
                                             tag='test2'))
        content, code = result['content'], result['status-code']
        self.assertEqual(content, [(dict(id='4', name='new_file.txt', tag='test2',
                                         size=6.0, mimeType='text/plain',
                                         modificationTime=self.fsc.get_time_now()))
                                   ])
        self.assertEqual(code, 200)

    def test_get_by_2id_and_name(self):
        result = self.fsc.get_by_params(dict(id=['1', '2'], name='new_file1.txt'))
        content, code = result['content'], result['status-code']
        self.assertEqual(content, [(dict(id='2', name='new_file1.txt', tag='test2',
                                         size=6.0, mimeType='text/plain',
                                         modificationTime=self.fsc.get_time_now()))])
        self.assertEqual(code, 200)

    def test_delete_4id(self):
        result = self.fsc.delete_by_params(dict(id=['1', '2', '3', '4']))
        content, code = result['content'], result['status-code']
        self.assertEqual(content, '4 files deleted')
        self.assertEqual(code, 200)

    def test_delete_by_id_name_tag(self):
        result = self.fsc.delete_by_params(dict(id=['1', '2', '3', '4'],
                                                name=['new_file.txt', 'new_file1.txt'],
                                                tag=['test1', 'test2']))
        content, code = result['content'], result['status-code']
        self.assertEqual(content, '3 files deleted')
        self.assertEqual(code, 200)

    def test_delete_by_tag(self):
        result = self.fsc.delete_by_params(dict(tag=['test2']))
        content, code = result['content'], result['status-code']
        self.assertEqual(content, '2 files deleted')
        self.assertEqual(code, 200)

    def test_delete_by_name_and_tag(self):
        result = self.fsc.delete_by_params(dict(name='new_file.txt', tag='test2'))
        content, code = result['content'], result['status-code']
        self.assertEqual(content, '1 files deleted')
        self.assertEqual(code, 200)


class NotExistingEndPoint(TestCase):
    def __init__(self, methodName: str = ...):
        super().__init__(methodName)
        self.url = 'http://127.0.0.1:2207/api/cats'

    def test_post(self):
        response = request(method='post', url=self.url)
        self.assertEqual(response.content.decode('utf-8'), "Not Implemented")
        self.assertEqual(response.status_code, 501)

    def test_delete(self):
        response = request(method='delete', url=self.url)
        self.assertEqual(response.content.decode('utf-8'), "Not Implemented")
        self.assertEqual(response.status_code, 501)

    def test_get(self):
        response = request(method='get', url=self.url)
        self.assertEqual(response.content.decode('utf-8'), "Not Implemented")
        self.assertEqual(response.status_code, 501)
