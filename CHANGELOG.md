# Changelog

## [Unreleased]

## [0.3.3] - 2020-04-12

- Implement github-actions to test and publish
- Update package metadata and publish to PyPI
- Implement first tests
- Drop support to python==3.5.* because pandas>=1.1 requires python>=3.6.1

## [0.3.2] - 2020-04-06

- Flask server visibility got limited to development machine.
- Package dependencies were included in setup.py (including the correct 
python minimum version i.e. 3.5).
- Removed commented code in HTML template that raised errors. Apparently
 Jinja does not care about HTML comments.
- User name got a default value "Anon"
- Add Transaction Form categories now update when page reload (before 
it required a whole application restart).
- Database connection is created per request and is not shared among 
different threads anymore.

## [0.3.1] - 2020-03-27

This is just a checkpoint for reverting all changes made since v0.3. 
Also, from now on this project adopts the [Semantic Versioning](https://semver.org/). 

## [0.3] - 2019-06-23
### Added
- The UI was updated using 
[SRTdash admin dashboard](https://github.com/puikinsh/srtdash-admin-dashboard) template.
- New expenses/earnings categories can be added while including a new transaction.

### Fixed
- The installments variable resets to 1 whenever the payment method or the 
transaction kind is changed

### Removed
- Some infos in **Basic Report** (amount available for investing, ema calculation)

## [0.2] - 2018-02-11
### Added
 - Overview shows how much is owed in the next credit card invoice, current month 
 earnings and investments made
 - 'last expenses' view shows the payment method
 - 'add transaction' form accepts investments and earnings
 - Three payment methods are available; 'Dinheiro' for cash transactions, 
 'Crédito' for transactions with a credit card and 'Terceiros' (explained below).
 - When using the credit payment method, the number of installments can be included.
 - Expenses paid in credit (and their installments) automatically get the 
 cash date assigned to the payment dates according to the period when the 
 expense ocurred and the date when the invoice closes. 
 - The 'Terceiros' pay method is a way of keeping track of expenses that 
 don't change the cash flow because another person paid for it. When used, 
 an entry of equal value is created on the earnings table
 - Overview now shows debt free balance, last 12 months average expending and 
 exponential moving average (calculated for all periods) expending.
 - Earnings now accepts categories
 - Expenses page now shows current month transactions and past 6 months 
 expendings separated by category

### Changed
 - 'Last expenses' view presents entries by the accrual date in reverse order (most recent on top) and doesn't show the id numbers column anymore
 - special dates constants are update everytime they are needed

### Fixed
 - By default, the analysis take into account the accrual data. The currently existing exceptions are the balance value and the credit card invoice value, which consider the cash data.
 - Overview gathers information from database AFTER new expenses are added, so the user can immediatly see the new entry on 'last expenses' view
 - App couldn't open in certain dates close to the month ending
 
## [0.1] - 2017-12-26
### Added
 - Overview shows all categories ordened by the most used first
 - Form to insert new expenses
 - Overview shows the balance for the end of the current month
 - Overview shows savings rate of last 12 months
 - Overview shows current month earnings and savings
 - Overview shows last expenses (10 by default)
 - Connect python to a sqlite database
 - Creates database automatically

### Deprecated
 - Overview shows most used categories
