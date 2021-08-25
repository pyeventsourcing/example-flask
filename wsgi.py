import os
from flask_wtf import FlaskForm
from werkzeug.utils import redirect
from wtforms import StringField, DecimalField, SubmitField
from wtforms import validators as v
from flask import Flask, render_template, url_for
from uuid import UUID

import bankaccounts.exceptions
from bankaccounts.application import BankAccounts

class OpenAccountForm(FlaskForm):
    full_name = StringField('Full Name', validators=[v.DataRequired()])
    email_address = StringField('Email Address', validators=[v.DataRequired(), v.Email()])
    submit = SubmitField('Open Account')

class CloseAccountForm(FlaskForm):
    submit = SubmitField('Close Account')

class DepositFundsForm(FlaskForm):
    amount = DecimalField('Deposit Amount', validators=[v.DataRequired()])
    submit = SubmitField('Deposit Funds')

class WithdrawFundsForm(FlaskForm):
    amount = DecimalField('Withdraw Amount', validators=[v.DataRequired()])
    submit = SubmitField('Withdraw Funds')

class TransferFundsForm(FlaskForm):
    account_id = StringField('Destination Account ID', validators=[v.DataRequired(), v.UUID()])
    amount = DecimalField('Transfer Amount', validators=[v.DataRequired()])
    submit = SubmitField('Transfer Funds')

class OverdraftLimitForm(FlaskForm):
    limit = DecimalField('Overdraft Limit', validators=[v.DataRequired()])
    submit = SubmitField('Set Overdraft Limit')

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'change-me')
accounts = BankAccounts()

@app.route('/')
def home():
    open_account = OpenAccountForm()
    return render_template('home.html', open_account=open_account, get_account=get_account)

@app.route('/accounts', methods=['GET', 'POST'])
def open_account():
    open_account = OpenAccountForm()
    if open_account.validate_on_submit():
        full_name = open_account.full_name.data
        email_address = open_account.email_address.data
        account_id = accounts.open_account(full_name, email_address)
        return redirect(url_for('get_account', account_id=account_id))
    return render_template('home.html', open_account=open_account, get_account=get_account)

@app.route('/accounts/<account_id>')
def get_account(account_id):
    deposit_funds = DepositFundsForm()
    withdraw_funds = WithdrawFundsForm()
    transfer_funds = TransferFundsForm()
    overdraft_limit = OverdraftLimitForm()
    return render_template('account.html', account=accounts.get_account(UUID(account_id)),
        deposit_funds=deposit_funds, withdraw_funds=withdraw_funds, transfer_funds=transfer_funds,
        overdraft_limit=overdraft_limit)

@app.route('/accounts/<account_id>/deposit', methods=['POST'])
def deposit_funds(account_id):
    form = DepositFundsForm()
    if form.validate_on_submit():
        amount = form.amount.data
        accounts.deposit_funds(UUID(account_id), amount)
    return redirect(url_for('get_account', account_id=account_id))

@app.route('/accounts/<account_id>/withdraw', methods=['POST'])
def withdraw_funds(account_id):
    form = WithdrawFundsForm()
    if form.validate_on_submit():
        amount = form.amount.data
        accounts.withdraw_funds(UUID(account_id), amount)
    return redirect(url_for('get_account', account_id=account_id))

@app.route('/accounts/<account_id>/transfer', methods=['POST'])
def transfer_funds(account_id):
    form = TransferFundsForm()
    if form.validate_on_submit():
        credit_account_id = UUID(form.account_id.data)
        amount = form.amount.data
        accounts.transfer_funds(UUID(account_id), credit_account_id, amount)
    return redirect(url_for('get_account', account_id=account_id))

@app.route('/accounts/<account_id>/overdraft_limit', methods=['POST'])
def overdraft_limit(account_id):
    form = OverdraftLimitForm()
    if form.validate_on_submit():
        limit = form.limit.data
        accounts.set_overdraft_limit(UUID(account_id), limit)
    return redirect(url_for('get_account', account_id=account_id))

@app.route('/accounts/<account_id>/close', methods=['POST'])
def close_account(account_id):
    accounts.close_account(UUID(account_id))
    return redirect(url_for('get_account', account_id=account_id))

@app.errorhandler(bankaccounts.exceptions.AccountNotFoundError)
def handle_account_not_found(e):
    return render_template('error.html', message='Account Not Found')

@app.errorhandler(bankaccounts.exceptions.AccountClosedError)
def handle_account_closed(e):
    return render_template('error.html', message='Account Closed')

@app.errorhandler(bankaccounts.exceptions.InsufficientFundsError)
def handle_insufficient_funds(e):
    return render_template('error.html', message='Insufficient Funds')
