import json
from utils.comm import RemoteFile


def load_config(config_file):
    with open(config_file, "rb") as f:
        config = json.load(f)
    return config


class ImageFile:
    def __init__(self, path):
        self._path = path
        if path.startswith("http:") or path.startswith("https:"):
            try:
                url, port = path.rsplit(":", 1)
            except ValueError:
                raise ValueError(f"path should be of format http://[hostname]/[path]:[port]")
            self._file_handle = RemoteFile(url=url, port=port)
        else:
            self._file_handle = open(path, mode="rb")

    def close(self):
        self._file_handle.close()

    def read(self, nbytes):
        return self._file_handle.read(nbytes)

    def readline(self):
        return self._file_handle.readline()

    def seek(self, nbytes):
        return self._file_handle.seek(nbytes)

    def tell(self):
        return self._file_handle.tell()

    def pnm_read_header(self):
        """
        :param pnm_file: This should be a file object so that after reading the header,
         file pointer is at the beginning of image data
        :return:
        """
        hdr = {
            "type": "UNKNOWN",
            "width": None,
            "height": None,
            "max_gray": 1
        }
        tokens = list()
        while len(tokens) < 3:
            line = self.readline().decode().strip().split("#")[0].strip()
            if not line:
                continue
            tokens += line.split()

        if tokens[0] == "P4":
            hdr["type"] = "PNM_BITMAP"
        elif tokens[0] == "P5":
            hdr["type"] = "PNM_GREYSCALE"
        else:
            raise ValueError(f"Unable to read header in file {self._path}")

        hdr["width"] = int(tokens[1])
        hdr["height"] = int(tokens[2])

        if hdr["type"] == "PNM_GREYSCALE":
            try:
                hdr["max_gray"] = int(tokens[3])
            except IndexError:
                max_gray = self.readline().decode().strip().split("#")[0].strip()
                while not max_gray:
                    max_gray = self.readline().decode().strip().split("#")[0].strip()
                hdr["max_gray"] = int(max_gray)

        return hdr

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return
