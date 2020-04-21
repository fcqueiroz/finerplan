from setuptools import setup, find_namespace_packages
import os


here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'requirements.txt')) as f:
    install_requires = f.read().splitlines()

with open(os.path.join(here, 'README.md')) as f:
    long_description = f.read()

with open(os.path.join(here, 'VERSION')) as f:
    version = f.read()

setup(
    name='finerplan',
    version=version,
    license="GPLv3",
    description='Financial Early Retirement Planner',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Fernanda Queiroz',
    author_email='fernanda.cdqueiroz@gmail.com',
    url='https://github.com/fcqueiroz/finerplan',
    download_url='https://github.com/fcqueiroz/finerplan/archive/v{}.tar.gz'.format(version),
    classifiers=[
        'Development Status :: 3 - Alpha',
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Framework :: Flask",
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    packages=find_namespace_packages(include=['finerplan.*']),
    include_package_data=True,
    install_requires=install_requires,
    python_requires='~=3.6',
)
