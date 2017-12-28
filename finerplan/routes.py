from flask import render_template, flash
from .finerplan import app
from .forms import AddTransactionForm
from finerplan import sql, dates

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    form = AddTransactionForm()
    if form.validate_on_submit():
        if form.transaction.data == "Receita":
            if sql.insert_earning(form):
                flash("The earning wasn't inserted correctly")
            else:
                flash("Added new earning '{}', occurred in {} with the value of R$ {}".format(form.description.data, form.date.data, form.value.data))
        elif form.transaction.data == "Investimento":
            if sql.insert_investment(form):
                flash("The investment wasn't inserted correctly")
            else:
                flash("Added new investment '{}', occurred in {} with the value of R$ {}".format(form.description.data, form.date.data, form.value.data))
        else:
            if sql.insert_expense(form):
                flash("The expense wasn't inserted correctly")
            else:
                flash("Added new expense '{}', occurred in {} with the value of R$ {}".format(form.description.data, form.date.data, form.value.data))
                
    report = {'name': app.config['NAME'], 
              'eom': dates.s_eom, 
              'balance': sql.balance_eom(local=True), 
              'income': sql.income_ocm(local=True), 
              'savings': sql.savings_ocm(local=True), 
              'sav_rate': sql.savings_rate(), 
              'credit': sql.credit_payment(local=True),
              'expenses':sql.last_expenses(), 
              'earnings':sql.last_earnings(), 
              'investments':sql.last_investments(), 
              'categorias': [ elem[1] for elem in sql.generate_categories()[0] ]}
    return render_template('overview.html', title='Overview', form=form,  report=report)
