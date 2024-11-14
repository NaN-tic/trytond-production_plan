# This file is part production_plan module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond.pool import Pool
from . import production

def register():
    Pool.register(
        production.Production,
        production.RoutingStep,
        production.Work,
        module='production_plan', type_='model')
