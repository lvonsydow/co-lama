"""
Setup script for building the Colama macOS application using py2app.
"""
from setuptools import setup

APP = ['colama/main.py']
DATA_FILES = [
    'resources/green.png',
    'resources/red.png',
]

OPTIONS = {
    'argv_emulation': False,
    'iconfile': 'resources/lama.icns',
    'plist': {
        'LSUIElement': True,
        'CFBundleName': 'Co-lama',
        'CFBundleDisplayName': 'Co-lama',
        'CFBundleIdentifier': 'com.lvonsydow.colama',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
    },
    'packages': ['colama'],
    'includes': [
        'asyncio',
        'PySide6',
        'PySide6.QtCore',
        'PySide6.QtGui',
        'PySide6.QtWidgets',
        'docker',
        'qasync',
        'chardet',
    ],
    'resources': ['resources/lama.icns'],
}

setup(
    app=APP,
    name='Co-lama',
    data_files=[
        ('resources', ['resources/lama.icns']),
    ] + DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
