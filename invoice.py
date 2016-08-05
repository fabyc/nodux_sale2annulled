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

__all__ = ['Invoice']
__metaclass__ = PoolMeta

_ZERO = Decimal(0)

_STATE = [
    ('annulled','Annulled'),
]

class Invoice:
    'Invoice'
    __name__ = 'account.invoice'

    @classmethod
    def __setup__(cls):
        super(Invoice, cls).__setup__()
        new_sel = [
            ('annulled','Annulled'),
        ]
        if new_sel not in cls.state.selection:
            cls.state.selection.extend(new_sel)
