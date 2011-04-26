# -*- coding: utf-8 -*-
"""
    testing

    Register Testing Helpers

    :copyright: © 2011 by Openlabs Technologies & Consulting (P) Limited
    :license: BSD, see LICENSE for more details.
"""
import datetime
from dateutil.relativedelta import relativedelta

from nereid.testing import testing_proxy


@testing_proxy.register()
def create_fiscal_year(obj, date=None, company=None):
    """Creates a fiscal year and requried sequences
    """
    fiscal_year_obj = obj.pool.get('account.fiscalyear')
    sequence_obj = obj.pool.get('ir.sequence')
    sequence_strict_obj = obj.pool.get('ir.sequence.strict')
    company_obj = obj.pool.get('company.company')

    if date is None:
        date = datetime.date.today()

    if company is None:
        company, = company_obj.search([], limit=1)

    invoice_sequence = sequence_obj.create({
        'code': 'account.invoice',
        'comapny': company,
        })
    fiscal_year = fiscal_year_obj.create({
        'name': '%s' % date.year,
        'start_date': date + relativedelta(month=1, day=1),
        'end_date': date + relativedelta(month=12, day=31),
        'company': company,
        'post_move_sequence': sequence_obj.create({
            'code': 'account.move',
            'company': company,
            }),
        'out_invoice_sequence': invoice_sequence,
        'in_invoice_sequence': invoice_sequence,
        'out_credit_note_sequence': invoice_sequence,
        'in_credit_note_sequence': invoice_sequence,
        })
    fiscal_year_obj.create_period([fiscal_year])
    return fiscal_year


@testing_proxy.register()
def create_coa_minimal(obj, company=None):
    """Create a minimal chart of accounts
    """
    account_template_obj = obj.pool.get('account.account.template')
    account_obj = obj.pool.get('account.account.template')
    account_journal_obj = obj.pool.get('account.journal')
    create_chart_account_obj = obj.pool.get(
        'account.account.create_chart_account', type="wizard")
    company_obj = obj.pool.get('company.company')

    account_template, = account_template_obj.search(
        [('parent', '=', False)])

    if company is None:
        company, = company_obj.search([], limit=1)

    wiz_id = create_chart_account_obj.create()
    # Stage 1
    create_chart_account_obj.execute(wiz_id, {}, 'account')
    # Stage 2
    create_chart_account_obj.execute(wiz_id, {
        'account_template': account_template,
        'company': company,
        }, 'create_account')
    # Stage 3
    receivable, = account_obj.search([
        ('kind', '=', 'receivable'),
        ('company', '=', company),
        ], limit=1)
    payable, = account_obj.search([
        ('kind', '=', 'payable'),
        ('company', '=', company),
        ], limit=1)
    create_chart_account_obj.execute(wiz_id, {
        'account_receivable': receivable,
        'account_payable': payable,
        }, 'create_properties')


@testing_proxy.register()
def create_payment_term(obj):
    """Create a simple payment term with all advance
    """
    payment_term_obj = obj.pool.get('account.invoice.payment_term')
    return payment_term_obj.create({
        'name': 'Direct',
        'lines': [('create', {'type': 'remainder'})]
        })

