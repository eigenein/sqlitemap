from pathlib import Path
from setuptools import find_packages, setup

setup(
    name='sqlitemap',
    version='0.1.0',
    description='Dictionary interface to an SQLite database',
    long_description=Path('README.md').read_text(encoding='utf-8'),
    long_description_content_type='text/markdown',
    author='Pavel Perestoronin',
    author_email='eigenein@gmail.com',
    url='https://github.com/eigenein/sqlitemap',
    packages=find_packages(exclude=['tests']),
    zip_safe=True,
    install_requires=[],
    extras_require={
        'dev': ['flake8', 'isort', 'pytest', 'pytest-cov', 'coveralls', 'ujson', 'orjson', 'twine'],
        'ujson': ['ujson'],
        'orjson': ['orjson'],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'License :: OSI Approved :: MIT License',
    ],
)
