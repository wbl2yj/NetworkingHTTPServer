
class FileReader:

    def __init__(self):
        pass

    def get(self, filepath, cookies):
        '''
        Returns a binary string of the file contents, or None.
        '''
        requestHead = self.head(filepath, cookies)
        import os
        body = b''
        if os.path.exists(filepath):
            if os.path.isdir(filepath):
                body = b"<html><body><h1>" + filepath.encode(encoding="ascii") + b"</h1></body></html>"
            else:
                with open(filepath, mode='r+b') as file:
                    body = file.read()
            return requestHead, body
        else:
            return requestHead, b""

    def head(self, filepath, cookies):
        '''
        Returns the size to be returned, or None.
        '''
        from datetime import datetime
        from time import mktime
        now = datetime.now()
        import os
        response = "HTTP/1.1 "
        exists = os.path.exists(filepath)
        isDir = os.path.isdir(filepath)
        if exists:
            response = response + "200 OK\r\n"
        else:
            response = response + "404 Not Found\r\n"
        response = response + "Date: " + now.strftime("%a, %d %b %Y %H:%M:%S GMT\r\n")
        if exists:
            modDate = datetime.fromtimestamp(os.path.getmtime(filepath))
            response = response + "Last-Modified: " + modDate.strftime("%a, %d %b %Y %H:%M:%S GMT\r\n")
            if isDir:
                response = response + "Content-Length: " + str(39 + len(filepath)) + "\r\n"
            else:
                response = response + "Content-Length: " + str(os.stat(filepath).st_size + 4) + "\r\n"
            name, extension = os.path.splitext(filepath)
            mimetype = "None"
            if isDir:
                mimetype = "text/html"
            else:
                if extension == ".html" or extension == ".htm":
                    mimetype = "text/html"
                elif extension == ".css":
                    mimetype = "text/css"
                elif extension == ".png":
                    mimetype = "image/png"
                elif extension == ".jpg" or extension == ".jpeg":
                    mimetype = "image/jpeg"
                elif extension == ".gif":
                    mimetype = "image/gif"
                elif extension == ".txt":
                    mimetype = "image/txt"
            response = response + "Content-Type: " + mimetype + "\r\n"
        else:
            response = response + "Content-Length: 0\r\n"
        response = response + "Access-Control-Allow-Origin: *\r\n"
        response = response + "Connection: Closed\r\n"
        return response.encode(encoding='ascii')
