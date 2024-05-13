from .downloader import BinaryDownloader


class PhantomjsDownloader(BinaryDownloader):
    def __init__(self):
        self._name = "phantomjs"
        self._download_link_root = "https://bitbucket.org/ariya/phantomjs/downloads"
        self._version = "2.1.1"

    def get_os_suffix(self):
        self._os_linux_32 = "linux-i686"
        self._os_linux_64 = "linux-x86_64"
        self._os_windows_32 = "windows"
        self._os_windows_64 = "windows"
        self._os_darwin_32 = "macosx"
        self._os_darwin_64 = "macosx"
        return super(PhantomjsDownloader, self).get_os_suffix()

    def get_download_link(self):
        os_suffix = self.get_os_suffix()
        filename = f"phantomjs-{self._version}-{os_suffix}"
        if "linux" in os_suffix:
            filename = f"{filename}.tar.bz2"
        else:
            filename = f"{filename}.zip"
        download_link = f"{self._download_link_root}/{filename}"
        return download_link, filename

    def get_bin_root_path(self):
        return super(PhantomjsDownloader, self).get_bin_root_path()

    def get_bin(self):
        extension = ".exe" if "windows" in self.get_os_suffix() else ""
        return f"{self.get_bin_root_path()}/phantomjs-{self._version}-{self.get_os_suffix()}/bin/phantomjs{extension}"

    def download(self):
        super(PhantomjsDownloader, self).download()
