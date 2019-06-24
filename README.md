# FinerPlan - Financial Early Retirement Planner #

This program intends to help those people seeking financial independence and 
early retirement to track and analyze their finances. It's designed so that 
you can focus on how to improve your savings rate and predict when you can set FIRE!

## Disclaimer
This is my first big project and the program is still in a really early 
development stage. It's not well suited for any kind of serious work. This is a
learning project before anything else.

## Getting Started

### Linux

Create a local copy of the repository in the current folder
> git clone https://github.com/fcqueiroz/finerplan.git

Export the path to reach the application
> export FLASK_APP=$PWD/finerplan/finerplan.py

Install project (running in virtual environment is recommended)
> pip install finerplan/.

Run flask on port 5001 (or any other port you like)
> flask run --host=0.0.0.0 --port=5001  

The application will greet you on _http://localhost:5001/_
