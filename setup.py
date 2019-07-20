import setuptools

setuptools.setup(
    name='Finerplan',
    version='0.3',
    url='https://github.com/fcqueiroz/finerplan',
    license='GPLv3+',
    author='Fernanda Queiroz',
    description='Financial Early Retirement Planner',
    packages=setuptools.find_packages(),
    include_package_data=True,
    python_requires='>=3.7',
    install_requires=[
        'Flask>=1.0',
        'Flask-SQLAlchemy>=1.3',
        'Flask-Login>=0.4',
        'Flask-Migrate>=2.5',
        'Flask-WTF>=0.14',
        'pandas>=0.24',
        'python-dotenv>=0.10'
    ],
    tests_require=[
        'pytest>=5.0',
    ],
)
