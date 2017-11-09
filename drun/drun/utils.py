#
#    Copyright 2017 EPAM Systems
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
#
"""
DRun utils functional
"""

import socket
import tempfile
import os
import shutil


def detect_ip():
    """
    Get current machine IP address

    :return: str -- IP address
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.connect(("8.8.8.8", 80))
    addr = sock.getsockname()[0]
    sock.close()
    return addr


def escape(unescaped_string):
    """
    Escape string (replace .:& with -)

    :param unescaped_string: source string
    :type unescaped_string: str
    :return: str -- escaped string
    """
    return unescaped_string.replace('.', '-').replace(':', '-').replace('&', '-')


def make_archive(source_folder, zip_file):
    """
    Make ZIP archive from folder

    :param source_folder: path to source folder
    :type source_folder: str
    :param zip_file: path to target zip file
    :type zip_file: str
    :return: None
    """
    filename = shutil.make_archive(zip_file, 'zip', source_folder)
    shutil.move(filename, zip_file)


def extract_archive(zip_file, target_folder):
    """
    Unpack zip file to folder

    :param zip_file: path source zip file
    :type zip_file: str
    :param target_folder: path to target folder
    :type target_folder: str
    :return: None
    """
    shutil.unpack_archive(zip_file, target_folder, 'zip')


class TemporaryFolder:
    """
    Temporary folder representation with context manager (temp. directory deletes of context exit)
    """

    def __init__(self, *args, **kwargs):
        """
        Build temp. folder representation using tempfile.mkdtemp

        :param args: tempfile.mkdtemp args
        :type args: tuple
        :param kwargs: tempfile.mkdtemp kwargs
        :type kwargs: dict
        """
        self._path = tempfile.mkdtemp(*args, **kwargs)

    @property
    def path(self):
        """
        Get path to temp. folder

        :return: str -- path
        """
        return self._path

    def remove(self):
        """
        Try to remove temporary folder (without exceptions)

        :return: None
        """
        try:
            for root, dirs, files in os.walk(self.path, topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    os.rmdir(os.path.join(root, name))
        finally:
            pass

    def __enter__(self):
        """
        Return self on context enter

        :return: :py:class:`drun.utils.TemporaryFolder`
        """
        return self

    def __exit__(self, type, value, traceback):
        """
        Call remove on context exit

        :param type: -
        :param value: -
        :param traceback: -
        :return: None
        """
        self.remove()


class Colors:
    """
    Terminal colors
    """

    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
