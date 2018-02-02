from flask import render_template, flash
from .forms import AddTransactionForm, TestForm

from finerplan import sql, dates, reports
from .finerplan import app

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    form = AddTransactionForm()
    #if form.validate_on_submit():
    if form.submit.data:
        if form.transaction.data:
            err = sql.insert_entry(form)
        if err:
            flash("The new entry wasn't inserted correctly. Error {}".format(err))
        else:
            flash("Successfully added new {}".format(form.transaction.data.lower()))
    tables = {'expenses':sql.last_expenses(),
              'earnings':sql.last_earnings(),
              'investments':sql.last_investments()}
    basic_report = reports.basic()
    basic_report['name'] = app.config['NAME']
    return render_template('overview.html', title='Overview', form=form,
                            tables=tables, report=basic_report)

@app.route('/earnings', methods=['GET', 'POST'])
def earnings():
    form = TestForm()

    if (form.category_0.data):
        flash("Voce selecionou {}".format(form.category_0.data))
    if form.pay_method.data == 'Dinheiro':
        flash("Voce selecionou {}".format(form.pay_method.data))
    if form.submit.data:
        flash("date: {}. Type: {}".format(form.date.data, type(form.date.data)))
        flash("categoria: {}. Type: {}".format(form.category_0.data, type(form.category_0.data)))
    return render_template('earnings.html', title='Test Zone', form=form)
