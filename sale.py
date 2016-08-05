#This file is part of Tryton.  The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.
from decimal import Decimal
from itertools import groupby, chain
from functools import partial
from sql import Table
from sql.functions import Overlay, Position
from sql.operators import Concat

from trytond.model import Workflow, ModelView, ModelSQL, fields
from trytond.modules.company import CompanyReport
from trytond.wizard import Wizard, StateAction, StateView, StateTransition, \
    Button
from trytond import backend
from trytond.pyson import If, Eval, Bool, PYSONEncoder, Id
from trytond.transaction import Transaction
from trytond.pool import Pool, PoolMeta

__all__ = ['Sale','AnnulSaleStart', 'AnnulSale']
__metaclass__ = PoolMeta

_ZERO = Decimal(0)

_STATE = [
    ('annulled','Annulled'),
]

class Sale:
    'Sale'
    __name__ = 'sale.sale'

    @classmethod
    def __setup__(cls):
        super(Sale, cls).__setup__()
        new_sel = [
            ('annulled','Annulled'),
        ]
        if new_sel not in cls.state.selection:
            cls.state.selection.extend(new_sel)

        new_sel_shipment = [
            ('annulled','Annulled'),
        ]
        if new_sel_shipment not in cls.shipment_state.selection:
            cls.shipment_state.selection.extend(new_sel_shipment)

        new_sel_invoice = [
            ('annulled','Annulled'),
        ]
        if new_sel_invoice not in cls.invoice_state.selection:
            cls.invoice_state.selection.extend(new_sel_invoice)


class AnnulSaleStart(ModelView):
    'Annul Sale'
    __name__ = 'sale.annul_sale.start'

class AnnulSale(Wizard):
    'Annul Sale'
    __name__ = 'sale.annul_sale'
    start = StateView('sale.annul_sale.start',
        'nodux_sale2annulled.annul_sale_start_view_form', [
            Button('Exit', 'end', 'tryton-cancel'),
            Button('Annul', 'annul_', 'tryton-ok', default=True),
            ])
    annul_ = StateAction('sale.act_sale_form')

    def do_annul_(self, action):
        pool = Pool()
        Sale = pool.get('sale.sale')
        Invoice = pool.get('account.invoice')
        sales = Sale.browse(Transaction().context['active_ids'])
        for s in sales:
            sale = s
            invoices= Invoice.search([('description', '=', sale.reference)])
            sale.state = 'annulled'
            cursor = Transaction().cursor
            for i in invoices:
                cursor.execute('DELETE FROM account_move_line WHERE move = %s' %i.move.id)
                cursor.execute('DELETE FROM account_move WHERE id = %s' %i.move.id)
                for payment in sale.payments:
                    cursor.execute('DELETE FROM account_statement_line WHERE id = %s' %payment.id)
                for move in sale.moves:
                    cursor.execute('DELETE FROM stock_move WHERE id = %s' % move.id)
                i.state = 'annulled'
                i.save()
                sale.invoice_state = 'annulled'
                sale.shipment_state = 'none'
                sale.save()
