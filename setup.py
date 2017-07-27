#!/usr/bin/env python

from setuptools import setup

setup(
    name='zappy',
    version='1.0',
    description='Python scraper for accessing ratings from tvbythenumbers.zap2it.com',
    author='sharibarboza',
    author_email='barbozashari@gmail.com',
    url='https://github.com/sharibarboza/zappy',
    download_url='https://github.com/sharibarboza/zappy/archive/1.0.0.tar.gz',
    license='MIT License',
    packages=['zappy'],
    install_requires=[
        'beautifulsoup4',
        'requests>=2.9.1'
    ]
)