#!/bin/env python

import argparse
import json
import os
import tempfile
from zipfile import ZipFile

import requests
import shutil

import sys
from requests import HTTPError

__author__ = "Michael Egger"
__license__ = "GPL"
__version__ = "0.9"

"""
usage: inox-extinstall[-h] [-v] [-t PATH] extension

Chromium extension downloader

positional arguments:
  extension             extension_id or preset (available presets are:
                        [ublock-origin, postman, scriptsafe, umatrix])

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
  -t PATH, --target PATH
                        target directory where extensions will be stored

Install Guide:

  1. Visit chrome://extensions in your browser.
  2. Ensure that the Developer mode checkbox in the top right-hand corner is checked.
  3. Click Load unpacked extension… to pop up a file-selection dialog.
  4. Navigate to the directory in which your extension files live, and select it.

  Alternatively, you can drag and drop the directory where your extension files
  live onto chrome://extensions in your browser to load it.

"""


def download_extension(extension_id,
                       target_directory,
                       _os='linux',
                       chromium_version='55.0.2883.87'):
    url = 'https://clients2.google.com/service/update2/crx'
    params = {
        'response': 'redirect',
        'os': _os,
        'prodversion': chromium_version,
        'x': 'id={}&installsource=ondemand&uc'.format(extension_id),
    }

    # download extension
    response = requests.get(url, params)
    response.raise_for_status()
    filename = response.request.url.split('/')[-1]
    if not filename.endswith('.crx'):
        return RuntimeError('Something gone wrong during GET {}'
                            .format(response.request.url))

    # write extension to temp dir
    crx_path = '{}/{}'.format(target_directory, filename)
    with open(crx_path, 'wb') as fp:
        fp.write(response.content)
    return crx_path


def unpack_extension(crx_path, target_directory):
    """
    Unpacks an extension to the given target directory
    :param crx_path: path to crx file
    :param target_directory: directory where the extension will be unpacked
    :return: extension name
    """

    # unpack extension
    with ZipFile(crx_path) as zp:
        zp.extractall(path=target_directory)

    # remove _metadata file
    shutil.rmtree('{}/_metadata'.format(target_directory), ignore_errors=True)

    manifest_path = '{}/manifest.json'.format(target_directory)
    with open(manifest_path, 'r') as fp:
        manifest = json.load(fp)

    # remove update_url from manifest.json
    # because we cannot update without WebStore
    manifest.pop('update_url', None)

    extension_name = manifest['name']

    with open(manifest_path, 'w') as fp:
        json.dump(manifest, fp, indent=4)

    return extension_name


class MyParser(argparse.ArgumentParser):

    @staticmethod
    def get_install_help(filename=None):
        file_msg = filename or 'the directory in which your extension files live, and select it.'
        return '''
Install Guide:

  1. Visit chrome://extensions in your browser.
  2. Ensure that the Developer mode checkbox in the top right-hand corner is checked.
  3. Click Load unpacked extension… to pop up a file-selection dialog.
  4. Navigate to {}

  Alternatively, you can drag and drop the directory where your extension files
  live onto chrome://extensions in your browser to load it.
'''.format(file_msg)

    def error(self, message):
        sys.stderr.write('error: {}\n'.format(message))
        self.print_help()
        sys.exit(2)

    def print_help(self, file=None):
        super(MyParser, self).print_help(file=file)
        (file or sys.stderr).write(self.get_install_help())

presets = {
    'https-everywhere': 'gcbommkclmclpchllfjekcdonpmejbdp',
    'postman': 'fhbjgbiflinjbdggehcddcbncdddomop',
    'ublock-origin': 'cjpalhdlnbpafiamejdnhcphjbkeiagm',
    'umatrix': 'ogfcmafjalglgifnmanfmnieipoejdcf',
    'scriptsafe': 'oiigbmnaadbkfbmpbfijlflahbdbdgdf',
}

default_target_path = '~/.inoxunpack/'


def main():
    parser = MyParser(description='Chromium extension downloader')
    parser.add_argument('-v', '--version', action='version', version='%(prog)s {}'.format(__version__))
    parser.add_argument('-t', '--target',
                        metavar='PATH',
                        action='store',
                        default=default_target_path,
                        help='target directory where extensions will be stored')
    parser.add_argument('extension',
                        action='store',
                        help='extension_id or preset (available presets are:\n[{}])'.format(', '.join(presets.keys())))
    args = parser.parse_args()

    # initialize working directory
    target_path = os.path.expanduser(args.target)
    if not os.path.exists(target_path):
        os.makedirs(target_path)

    # parse given extension_id
    extension_id = presets.get(args.extension, None) or args.extension

    # create temp dir
    tempdir = tempfile.mkdtemp()

    # download and unpack extension
    try:
        print('Downloading extension {} ...'.format(extension_id))
        crx_path = download_extension(extension_id, tempdir)
        temp_unpacked_path = '{}/{}'.format(tempdir, extension_id)
        extension_name = unpack_extension(crx_path, temp_unpacked_path)

        # copy extension to final directory
        target_ext_path = '{}{}'.format(target_path, extension_id)
        shutil.rmtree(target_ext_path, ignore_errors=True)
        shutil.copytree(temp_unpacked_path, target_ext_path)
        shutil.rmtree(tempdir)
        print('Unpacked {} to {}'.format(extension_name, target_ext_path))
        print(MyParser.get_install_help(target_ext_path))
    except HTTPError as e:
        sys.stderr.write('error: {}\n'.format(e.response.reason))
        exit(1)
    except RuntimeError as e:
        sys.stderr.write('error: {}\n'.format(e))
        exit(1)

if __name__ == '__main__':
    main()
