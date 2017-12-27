from flask import render_template, flash
#from finpy.__init__ import app
from finpy.finpy import app
from finpy.forms import AddTransactionForm
from finpy.sql import *

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    report = {'name': 'Fernanda', 
              'eom': s_eom, 
              'balance': balance_eom(local=True), 
              'income': income_ocm(local=True), 
              'savings': savings_ocm(local=True), 
              'sav_rate': savings_rate(), 
              'expenses':last_expenses(), 
              'categorias': [ elem[1] for elem in generate_categories()[0] ]}
    form = AddTransactionForm()
    if form.validate_on_submit():
        insert_expense([form.pay_method.data, 
                        form.date.data, 
                        form.description.data, 
                        form.category_0.data, 
                        float(form.value.data.replace(',','.'))])
        flash("Added new expense '{}', occurred in {} with the value of R$ {}".format(form.description.data, form.date.data, form.value.data))
    return render_template('overview.html', title='Overview', form=form, report=report)
