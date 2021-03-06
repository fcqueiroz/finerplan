# FinerPlan - Financial Early Retirement Planner #

This program intends to help those people seeking financial independence and 
early retirement, so this can be helpful to track and analyze their finances.
It's designed so that you can focus on how to improve your savings rate and
predict when you can set FIRE!

## Disclaimer
This is my first big project and the program is still in a really early 
development stage. It's not well suited for any kind of serious work. This is a
learning project before anything else.

## Requirements

- Python >=3.6.1
- A defined locale (other than C/POSIX)

## Development

NOTE: The master branch of this repository tracks the very latest development 
and may contain features and changes that do not exist on any released version. 
To find the spec for a specific version, look in the versions subdirectory.

### Getting Started

Clone the project source code, install it in editable mode and start 
Flask development server from within the projects root directory:

```bash
git clone https://github.com/fcqueiroz/finerplan.git
cd finerplan
pip install -r requirements.txt
flask run
```

The application will greet you on _http://localhost:5000/_

### Run docker container

An optional working docker solution is offered with this repository. 
It requires docker-compose executable available on path. The next example
builds and runs Nginx container as reverse proxy and a uWSGI server
providing FinerPlan application.

Example:
```bash
python3 setup.py sdist bdist_wheel
export FINERPLAN_VERSION=$(cat VERSION)
export FINERPLAN_DATABASE=dev.db
docker-compose up --build
```

The application will greet you on _http://localhost/_

### Contributing

These steps are heavily inspired on [Borg](https://borgbackup.readthedocs.io/en/stable/development.html)
project development guidelines.

Some guidance for contributors:

* focus on some topic, resist changing anything else.
* do not do style changes mixed with functional changes.
* try to avoid refactorings mixed with functional changes.
* if you write new code, please add tests for it

#### Checklist for creating a new release:

* create a release-X.Y.Z branch
* update [CHANGELOG](CHANGELOG.md)
* update [VERSION](VERSION)
* commit and push branch
* if all CI tests pass, then tag the release and push it:

```bash
git tag -a vX.Y.Z
git push origin vX.Y.Z
```
