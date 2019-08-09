"""Contains a list of default objects an user might want to set up."""

common_expenses_housing = [
    {'name': 'Rent'}, {'name': 'Furniture'}, {'name': 'Maintenance'}, {'name': 'Utilities'}
]

common_expenses_electronic_devices = [
    {'name': 'Phone'}, {'name': 'Computer'}
]

common_expenses_personal_care = [
    {'name': 'Cosmetics'}, {'name': 'Hairdresser'}, {'name': 'Hair removal'}, {'name': 'Clothing'}
]

common_expenses_education = [
    {'name': 'Courses'}, {'name': 'Supplies'}, {'name': 'Books'}
]

common_expenses_leisure = [
    {'name': 'General'}, {'name': 'Hobbies'}, {'name': 'Vacation'}
]

common_expenses_food = [
    {'name': 'Groceries'}, {'name': 'Restaurants'}
]

common_expenses_other = [
    {'name': 'Uncategorized'}, {'name': 'Gifts and donations'}
]

common_expenses_health = [
    {'name': 'Pharmacy'}, {'name': 'Special care'}, {'name': 'Doctors'}, {'name': 'Medicine'}
]

common_expenses_transportation = [
    {'name': 'Auto'}, {'name': 'Public'}, {'name': 'Taxi'}, {'name': 'Travel'}
]

common_expenses = [
    {'name': 'Business'},
    {'name': 'Housing', 'children_data': common_expenses_housing},
    {'name': 'Electronic devices', 'children_data': common_expenses_electronic_devices},
    {'name': 'Personal care', 'children_data': common_expenses_personal_care},
    {'name': 'Education', 'children_data': common_expenses_education},
    {'name': 'Leisure', 'children_data': common_expenses_leisure},
    {'name': 'Food', 'children_data': common_expenses_food},
    {'name': 'Other', 'children_data': common_expenses_other},
    {'name': 'Health', 'children_data': common_expenses_health},
    {'name': 'Transportation', 'children_data': common_expenses_transportation}
]

common_income = [
    {'name': 'Scholarship'},
    {'name': 'Paycheck'},
    {'name': 'Subsidy'},
    {'name': 'Other'},
    {'name': 'Business'}
]

common_assets = [
    {'name': 'Cash', 'accounting_type': 'Cash'}
]

common_accounts = [
    {'name': 'Income', 'accounting_type': 'Income', 'parent': None, 'children_data': common_income},
    {'name': 'Expenses', 'accounting_type': 'Expense', 'parent': None, 'children_data': common_expenses},
    {'name': 'Assets', 'accounting_type': 'Asset', 'parent': None, 'children_data': common_assets}
]
