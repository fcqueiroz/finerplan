# FinerPlan - Financial Early Retirement Planner #

This program intends to help those people seeking financial independence and early retirement to track and analyze their finances. It's designed so that you can focus on how to improve your savings rate and predict when you can set FIRE!

## Disclaimer
This is my first big project and the program is still in a really early development stage. It's not well suited for any kind of serious work. My main goals are to solve a personal need while I develop skills in programming, project management and other areas.

## Getting Started

For installing the application, run the following command within the projects root directory finerplan/

> pip install --editable .

The editable flag allows editing source code without having to reinstall the Flask app each time you make changes. You should then be able to start up the application with the following commands:

> export FLASK_APP=finerplan/finerplan.py  
> export FLASK_DEBUG=true  
> flask run  

The application will greet you on _http://localhost:5000/_
