import sys
from setuptools import setup, find_packages

def convert_readme():
    try:
        import pypandoc
    except ImportError:
        return read_rst()
    rst = pypandoc.convert_file('README.md', 'rst')
    with open('README.rst', 'w') as f:
        f.write(rst)
    return rst

def read_rst():
    try:
        with open('README.rst', 'r') as f:
            rst = f.read()
    except IOError:
        rst = None
    return rst

def get_long_description():
    if {'sdist', 'bdist_wheel'} & set(sys.argv):
        long_description = convert_readme()
    else:
        long_description = read_rst()
    return long_description

setup(
    name = "python-dispatch",
    version = "v0.0.5",
    author = "Matthew Reid",
    author_email = "matt@nomadic-recording.com",
    description = "Lightweight Event Handling",
    url='https://github.com/nocarryr/python-dispatch',
    license='MIT',
    packages=find_packages(exclude=['tests*']),
    include_package_data=True,
    setup_requires=['pypandoc'],
    long_description=get_long_description(),
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
    ],
)
