from setuptools import setup

setup(
    name='finerplan',
    version='0.3.2',
    packages=['finerplan'],
    include_package_data=True,
    install_requires=[
        'flask',
        'python-dotenv',
        'Flask-WTF',
        'pandas',
    ],
    python_requires='>=3.5',
)
