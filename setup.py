from setuptools import setup

setup(
    name='finerplan',
    version='0.3',
    packages=['finerplan'],
    include_package_data=True,
    install_requires=[
        'flask',
    ],
    python_requires='>=3',
    setup_requires=[
        'pytest-runner',
    ],
    tests_require=[
        'pytest',
    ],
)
