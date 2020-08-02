import sys
from setuptools import setup, find_packages

setup(
    name = "python-dispatch",
    version = "v0.1.31",
    author = "Matthew Reid",
    author_email = "matt@nomadic-recording.com",
    description = "Lightweight Event Handling",
    url='https://github.com/nocarryr/python-dispatch',
    license='MIT',
    packages=find_packages(exclude=['tests*']),
    include_package_data=True,
    keywords='event properties dispatch',
    platforms=['any'],
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
)
