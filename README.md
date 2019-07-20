# FinerPlan - Financial Early Retirement Planner #

This program intends to help those people seeking financial independence and 
early retirement to track and analyze their finances. It's designed so that 
you can focus on how to improve your savings rate and predict when you can set FIRE!

## Disclaimer
This is my first big project and the program is still in a really early 
development stage. It's not well suited for any kind of serious work. This is a
learning project before anything else.

## Getting Started
Run the following commands to get the application working in a development environment.

### Linux

Create a local copy of the repository in the current folder
> git clone https://github.com/fcqueiroz/finerplan.git  
> cd finerplan  

Install the application (using virtual environment is recommended)
> pip install --editable .  
> flask db upgrade  

Run this command inside finerplan/ folder whenever you want to start the application.
> flask run  

The application will greet you on _http://localhost:5001/_
