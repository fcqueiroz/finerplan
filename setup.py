import setuptools

setuptools.setup(
    name='finerplan',
    version='0.3',
    packages=setuptools.find_packages(),
    include_package_data=True,
    python_requires='>=3',
    setup_requires=[
        'pytest-runner',
    ],
    tests_require=[
        'pytest',
    ],
)
