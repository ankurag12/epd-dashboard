import socket


class RemoteFile:
    def __init__(self, url='http://macbook-pro.local/sample_image.pgm', port=8080):
        self._port = port
        _, _, self._host, self._path = url.split('/', 3)
        self._addr = socket.getaddrinfo(self._host.split(":")[0], self._port)[0][-1]
        self._socket = socket.socket()
        self._socket.connect(self._addr)
        self._send_http_request()
        # This value should only be updated for the "contents" of the file, not HTTP header
        self._curr_pos = 0
        self._http_header = self._parse_http_header()
        self._curr_pos = 0

    def close(self):
        self._socket.close()

    def read(self, nbytes):
        rx = self._socket.recv(nbytes)
        self._curr_pos += len(rx)
        return rx

    def seek(self, pos):
        move_bytes = pos - self._curr_pos
        if move_bytes < 0:
            raise ValueError(f"Cannot go back in a remote file as everything is done on the fly")
        chunk_size = 1024
        while move_bytes > 0:
            move_bytes -= len(self.read(min(move_bytes, chunk_size)))

    def tell(self):
        return self._curr_pos

    def readline(self, end=b"\n"):
        line = b""
        len_end = len(end)
        while line[-len_end:] != end:
            line += self.read(1)
        return line

    def _send_http_request(self):
        self._socket.send(bytes(f'GET /{self._path} HTTP/1.0\r\nHost: {self._host}\r\n\r\n', 'utf8'))

    def _parse_http_header(self):
        # HTTP header and content is separated by a '\r\n\r\n'
        header = self.readline(end=b"\r\n\r\n")
        return str(header[:-4], 'utf8')

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
