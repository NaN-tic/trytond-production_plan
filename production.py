from datetime import timedelta
from trytond.model import fields
from trytond.pool import PoolMeta, Pool
from trytond.pyson import Eval


class Production(metaclass=PoolMeta):
    __name__ = 'production'

    planned_operations_time = fields.Function(fields.TimeDelta(
            'Planned Operations Time'), 'get_planned_operations_time')

    def get_planned_operations_time(self, name):
        return sum([work.planned_time for work in self.works if work.planned_time], timedelta())


class RoutingStep(metaclass=PoolMeta):
    __name__ = 'production.routing.step'

    calculation = fields.Selection([
            (None, ''),
            ('standard', 'Standard'),
            ('fixed', 'Fixed'),
            ], 'Calculation', required=True, help='Use Standard to multiply '
        'the amount of time by the number of units produced. Use Fixed to use '
        'the indicated time in the production without considering the '
        'quantities produced. The latter is useful for a setup or cleaning '
        'operation, for example.')
    time = fields.TimeDelta('Time', states={
            'required': Eval('calculation').in_(['standard', 'fixed']),
            'invisible': ~Eval('calculation').in_(['standard', 'fixed']),
            })

    def get_work(self, production, work_center_picker):
        Uom = Pool().get('product.uom')

        work = super().get_work(production, work_center_picker)
        if self.calculation == 'standard':
            if production.product and production.quantity and production.bom:
                product = production.product
                bom_quantity = 0
                for bom_output in production.bom.outputs:
                    if bom_output.product == product:
                        # Convert using bom
                        bom_quantity += Uom.compute_qty(
                            bom_output.unit, bom_output.quantity,
                            product.default_uom, round=False)
                if bom_quantity: 
                    factor = production.quantity / bom_quantity
                    work.planned_time = self.time * factor
        elif self.calculation == 'fixed':
            work.planned_time = self.time
        return work


class Work(metaclass=PoolMeta):
    __name__ = 'production.work'

    planned_time = fields.TimeDelta('Planned Time', readonly=True)
