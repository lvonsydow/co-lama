from setuptools import setup

APP = ['colama.py']
DATA_FILES = ['lama.png','path.txt','green.png', 'red.png']
OPTIONS = {
    'argv_emulation': False,
    'iconfile': 'lama.icns',
    'plist': {
        'CFBundleName': 'Co-lama',
        'CFBundleDisplayName': 'Co-lama',
        'CFBundleGetInfoString': "Co-lama",
        'CFBundleVersion': "0.1.0",
        'CFBundleShortVersionString': "0.1.0",
    },
    'packages': ['rumps'],
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'], install_requires=['rumps']
)
