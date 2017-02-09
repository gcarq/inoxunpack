# inoxunpack
Downloads extensions from Chrome WebStore and unpacks them,
this makes it possible to install extensions offline via developer mode.

### Example
```
$ git clone https://github.com/gcarq/inoxunpack.git
$ cd inoxunpack
$ ./inoxunpack.py ublock-origin
```

### Usage
```
inoxunpack.py [-h] [-v] [-t PATH] extension

Chromium extension downloader

positional arguments:
  extension             extension_id or preset (available presets are: [https-
                        everywhere, postman, ublock-origin, umatrix,
                        scriptsafe])

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
```