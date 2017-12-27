from setuptools import setup

setup(
    name='finpy',
    version='0.0.1',
    packages=['finpy'],
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
