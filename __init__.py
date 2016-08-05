#This file is part of Tryton.  The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.

from trytond.pool import Pool
from .sale import *
from .invoice import *

def register():
    Pool.register(
        Sale,
        AnnulSaleStart,
        Invoice,
        module='nodux_sale2annulled', type_='model')
    Pool.register(
        AnnulSale,
        module='nodux_sale2annulled', type_='wizard')
