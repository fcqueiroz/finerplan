from setuptools import setup

setup(
    name='finerplan',
    version='0.3',
    packages=['app'],
    include_package_data=True,
    install_requires=[
        'flask',
        'flask-migrate',
        'flask-sqlalchemy',
        'flask-wtf',
        'pandas',
        'python-dotenv',
    ],
    python_requires='>=3',
    setup_requires=[
        'pytest-runner',
    ],
    tests_require=[
        'pytest',
    ],
)
