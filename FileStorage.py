from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse
import magic
from FileStorageDatabase import DataStorage
import json

class RequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path.startswith('/api/get'):
            params = parse_qs(urlparse(self.path).query) #словарь
            print(params)
            if ('id' or 'name' or 'tag' or 'size' or 'mimeType' or 'modificationTime') not in params:
                database = DataStorage()
                self.send_response(200)
                self.end_headers()
                json_obj = json.dumps(database.loading_all(), indent=4)
                print(database.loading_all())
                self.wfile.write(str(json_obj).encode('utf-8'))
            else:
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                # self.send_header('Content-type', 'multipart/form-data')
                self.end_headers()
                params_dict = {}
                for k, v in params.items():
                    if k in ['id', 'name', 'tag', 'size', 'mimeType', 'modificationTime']:
                        params_dict[k] = v
                data_base = DataStorage()
                json_obj = json.dumps(data_base.loading_by_params(params_dict), indent=4)
                self.wfile.write(str(json_obj).encode('utf-8'))
        elif self.path.startswith('/api/download'):
            params = parse_qs(urlparse(self.path).query)
            if 'id' in params:
                id = str(params['id'][0])
                database = DataStorage()
                print(database.get_name_by_id(id))
                if database.get_name_by_id(id):
                    self.send_response(200)
                    self.end_headers()
                    print(database.get_name_by_id(id))
                    with open(database.get_name_by_id(id)[0][0], mode="rb") as body:
                        content = body.read()
                        self.wfile.write(content)
                else:
                    self.send_response(404)
                    self.end_headers()
                    self.wfile.write(str('файл не существует').encode('utf-8'))
            else:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(str('отсутствуют условия').encode('utf-8'))
        else:
            self.send_response(501)
            self.end_headers()
            self.wfile.write(str('Not Implemented').encode('utf-8'))

    def do_POST(self):
        if self.path.startswith('/api/upload'):
            content_length = int(self.headers['Content-Length'])
            print(content_length)
            if content_length == 0:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(str("Запрос без файла").encode('utf-8'))
            else:
                content_length = int(self.headers['Content-Length'])
                body = self.rfile.read(content_length)
                mimeType = magic.from_buffer(body, mime=True)
                params = parse_qs(urlparse(self.path).query)
                modificationTime = self.log_date_time_string()
                # modificationTime = str(datetime.now().date()) + str(datetime.now().time())
                id = str(params['id'][0]) if 'id' in params else ''
                name = str(params['name'][0]) if 'name' in params else id
                tag = str(params['tag'][0]) if 'tag' in params else ''
                file_dict = {
                    'id': id,
                    'name': name,
                    'tag': tag,
                    'size': content_length,
                    'mimeType': mimeType,
                    'modificationTime': modificationTime

                }
                print(file_dict)
                database = DataStorage()
                if database.loading_by_id(id):
                    print('был апдейт')
                    database.update(file_dict)
                else:
                    print('запись нового файла')
                    database.save_in_table(file_dict)
                print(self.path)
                with open(name, mode="wb") as file:
                    file.write(body)
                self.send_response(201)
                self.send_header('Content-type', 'multipart/form-data')
                self.end_headers()
                json_obj = json.dumps([file_dict], indent=4)
                self.wfile.write(str(json_obj).encode('utf-8'))
        else:
            self.send_response(501)
            self.end_headers()
            self.wfile.write(str('Not Implemented').encode('utf-8'))

    def do_DELETE(self):
        if self.path.startswith('/api/delete'):
            params = parse_qs(urlparse(self.path).query)
            if ('id' or 'name' or 'tag' or 'size' or 'mimeType' or 'modificationTime') not in params:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(str("Запрос без параметров").replace("'", '"').encode('utf-8'))
            else:
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                # self.send_header('Content-type', 'multipart/form-data')
                self.end_headers()
                params_dict = {}
                for k, v in params.items():
                    if k in ['id', 'name', 'tag', 'size', 'mimeType', 'modificationTime']:
                        params_dict[k] = v
                data_base = DataStorage()
                count = data_base.delete(params_dict)
                result = str(count) + ' files deleted'
                self.wfile.write(result.encode('utf-8'))
        else:
            self.send_response(501)
            self.end_headers()
            self.wfile.write(str('Not Implemented').encode('utf-8'))


    def do_dict(self):
        content_length = int(self.headers['Content-Length']) #если это используется только в post, возвращать еще и body
        body = self.rfile.read(content_length)
        mimeType = magic.from_buffer(body, mime=True)
        params = parse_qs(urlparse(self.path).query)
        modificationTime = self.log_date_time_string()
        id = str(params['id'][0])
        name = str(params['name'][0]) if 'name' in params else id
        file_dict = {
            'id': id,
            'name': name,
            'tag': '',
            'size': content_length,
            'mimeType': mimeType,
            'modificationTime': modificationTime

        }
        return file_dict



server = HTTPServer(("127.0.0.1", 2207), RequestHandler)
server.serve_forever()
