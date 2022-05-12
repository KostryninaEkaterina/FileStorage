import time
from datetime import datetime
from json import loads
from logging import getLogger
from mimetypes import guess_type
from typing import List, Dict, NamedTuple
from urllib.parse import urljoin

from requests import request, Response
from FileStorageDatabase import DataStorage

# from requests.compat import urljoin

LOGGER = getLogger('FileStorageConnector')


class Metadata(NamedTuple):
    id: str = ''
    name: str = ''
    tag: str = ''

    @property
    def mime_type(self):
        return guess_type(self.name)[0]


_UPLOAD_END_POINT = '/api/upload'
_GET_END_POINT = '/api/get'
_DELETE_END_POINT = '/api/delete'
_DOWNLOAD_END_POINT = '/api/download'

REST_TYPE_MAPPING = {
    _UPLOAD_END_POINT: 'post',
    _GET_END_POINT: 'get',
    _DELETE_END_POINT: 'delete',  # или post?..
    _DOWNLOAD_END_POINT: 'get'
}
_UNKNOWN_MIME_TYPE = 'application/octet-stream'


def prepare_request(base_url, end_point):
    method = REST_TYPE_MAPPING[end_point]
    url = urljoin(base_url, end_point)

    def make_request(params=None, headers=None, data=None):
        response: Response = request(method=method, url=url,
                                     headers=headers, params=params, data=data)
        response.raise_for_status()
        return {'content': response.content.decode('utf-8'), 'status-code': response.status_code}

    return make_request


class FileConnector:

    def __init__(self, base_url: str):
        self._upload = prepare_request(base_url, _UPLOAD_END_POINT)
        self._get = prepare_request(base_url, _GET_END_POINT)
        self._delete = prepare_request(base_url, _DELETE_END_POINT)
        self._download = prepare_request(base_url, _DOWNLOAD_END_POINT)

    def upload(self, payload=None, meta: Metadata = None, mime_type: str = None) -> dict:
        params = {k: v for k, v in meta._asdict().items() if v} if meta else {}
        content_type = mime_type or (meta and meta.mime_type) or _UNKNOWN_MIME_TYPE

        content = self._upload(params, {'Content_Type': content_type}, payload)['content']
        code = self._upload(params, {'Content_Type': content_type}, payload)['status-code']
        return {'content': loads(content), 'status-code': code}

    def get_by_id(self, file_id) -> List[Dict]:
        response = self._get({'id': file_id})['content']
        return loads(response)

    def get_by_params(self, params_dict) -> dict:
        response = self._get(params_dict)['content']
        code = self._get(params_dict)['status-code']
        return {'content': loads(response), 'status-code': code}

    def get_without_params(self):
        response = self._get()
        content = response['content']
        code = response['status-code']
        return {'content': loads(content), 'status-code': code}

    def delete_by_id(self, file_id):
        self._delete({'id': file_id})
        return self._delete({'id': file_id})['status-code']

    def download_by_id(self, file_id):
        return self._download({'id': file_id})['content']

    def download_by_params(self, params: dict):
        response = self._download(params)
        content = response['content']
        code = response['status-code']
        return {'content': loads(content), 'status-code': code}

    def download_without_params(self):
        response = self._download()
        content = response['content']
        code = response['status-code']
        return {'content': loads(content), 'status-code': code}

    def delete_all_from_database(self) -> None:
        data = DataStorage()
        data.delete_all()

    def get_time_now(self):
        now = datetime.now()
        modificationTime = now.strftime("%Y-%m-%d %H:%M:%S")
        return modificationTime

    def log_date_time_string(self) -> str:
        """Return the current time formatted for logging."""
        now = time.time()
        monthname = [None,
                     'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                     'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        year, month, day, hh, mm, ss, x, y, z = time.localtime(now)
        s = "%02d/%3s/%04d %02d:%02d:%02d" % (
            day, monthname[month], year, hh, mm, ss)
        return s

    def delete_by_params(self, params: dict):
        response = self._delete(params)
        content = response['content']
        code = response['status-code']
        return {'content': content, 'status-code': code}

    def delete_without_params(self):
        response = self._delete()
        content = response['content']
        code = response['status-code']
        return {'content': content, 'status-code': code}
