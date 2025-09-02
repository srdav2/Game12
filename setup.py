"""
Setup script to create a Mac application bundle for Hevy to Garmin FIT Merger
"""

from setuptools import setup
import py2app
import os

# Application metadata
APP = ['app.py']
DATA_FILES = [
    'hevy_garmin_config.json',
    'muscle_groups.json',
    'sample_hevy_workout.csv',
    ('test files', ['test files/2025-09-01-16-42-38.fit', 'test files/workouts-2.csv'])
]

OPTIONS = {
    'argv_emulation': True,
    'iconfile': None,  # We could add an icon file here
    'plist': {
        'CFBundleName': 'Hevy to Garmin FIT Merger',
        'CFBundleDisplayName': 'Hevy to Garmin FIT Merger',
        'CFBundleGetInfoString': 'Merge Hevy workouts with Garmin FIT files',
        'CFBundleIdentifier': 'com.hevy2garmin.merger',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'NSHighResolutionCapable': True,
        'LSMinimumSystemVersion': '10.15.0',
    },
    'packages': ['customtkinter', 'pandas', 'fit_tool', 'tkinter'],
    'includes': ['json', 're', 'datetime', 'threading', 'tempfile', 'os'],
    'excludes': ['matplotlib', 'numpy.distutils'],
    'resources': ['hevy_garmin_config.json', 'muscle_groups.json'],
    'optimize': 1,
}

setup(
    name='Hevy to Garmin FIT Merger',
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
    install_requires=[
        'customtkinter==5.2.2',
        'pandas==2.3.2', 
        'fit_tool==0.9.13'
    ]
)
