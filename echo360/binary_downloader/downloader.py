import sys
import os
import platform
import stat
import wget
import shutil
import logging

_LOGGER = logging.getLogger(__name__)


class BinaryDownloader(object):
    _name = None
    # need to overide
    _os_linux_32:str
    _os_linux_64:str
    _os_windows_32:str
    _os_windows_64:str
    _os_darwin_32:str
    _os_darwin_64:str
    _os_darwin_arm:str
    def __init__(self):
        raise NotImplementedError

    def get_os_suffix(self):
        arch = "64" if sys.maxsize > 2**32 else "32"
        if "linux" in sys.platform:
            if arch == "64":
                return self._os_linux_64
            else:
                return self._os_linux_32
        elif "win32" in sys.platform:
            if arch == "64":
                return self._os_windows_64
            else:
                return self._os_windows_32
        elif "darwin" in sys.platform:
            # detect if this is using arm processor (e.g. M1/M2 Mac)
            if platform.processor() == "arm":
                return self._os_darwin_arm
            if arch == "64":
                return self._os_darwin_64
            else:
                return self._os_darwin_32
        else:
            raise Exception("NON-EXISTING OS VERSION")

    def get_download_link(self):
        raise NotImplementedError

    def get_bin_root_path(self):
        return "{0}/bin".format(os.getcwd())

    def get_bin(self):
        raise NotImplementedError

    def download(self):
        print(
            f'>> Downloading {self._name} binary file for "{self.get_os_suffix()}"'
        )
        # Download bin for this os
        link, filename = self.get_download_link()
        bin_path = self.get_bin_root_path()
        # delete bin directory if exists
        if os.path.exists(bin_path):
            shutil.rmtree(bin_path)
        os.makedirs(bin_path)
        # remove existing binary file or folder
        wget.download(link, out=f"{bin_path}/{filename}")
        print(f'\r\n>> Extracting archive file "{filename}"')
        shutil.unpack_archive(
            f"{bin_path}/{filename}", extract_dir=bin_path
        )
        st = os.stat(self.get_bin())
        os.chmod(self.get_bin(), st.st_mode | stat.S_IEXEC)
