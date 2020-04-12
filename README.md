# FinerPlan - Financial Early Retirement Planner #

![](https://github.com/fcqueiroz/finerplan/workflows/CI/badge.svg)

This program intends to help those people seeking financial independence and 
early retirement to track and analyze their finances. It's designed so that 
you can focus on how to improve your savings rate and predict when you can set FIRE!

## Disclaimer
This is my first big project and the program is still in a really early 
development stage. It's not well suited for any kind of serious work. This is a
learning project before anything else.

## Development

### Getting Started

For installing the application, run the following command within the projects root 
directory finerplan/

> pip install --editable .

The editable flag allows editing source code without having to reinstall the Flask 
app each time you make changes. You should then be able to start up the application 
with the following commands:

> flask run --port=5001  

The application will greet you on _http://localhost:5001/_

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
> git tag -a vX.Y.Z
> git push origin vX.Y.Z