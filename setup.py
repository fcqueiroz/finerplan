from setuptools import setup
import os


here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'requirements.txt')) as f:
    install_requires = f.read().splitlines()

setup(
    name='finerplan',
    version='0.3.2',
    packages=['finerplan'],
    include_package_data=True,
    install_requires=install_requires,
    python_requires='>=3.6',
)
