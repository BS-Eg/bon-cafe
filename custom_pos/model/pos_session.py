import logging
from odoo import api, fields, models, tools, _

class InheritPosSession(models.Model):
    _inherit = 'pos.session'

    def _get_split_receivable_vals(self, payment, amount, amount_converted):
        partial_vals = {
            'account_id': payment.payment_method_id.receivable_account_id.id,
            'move_id': self.move_id.id,      
            'partner_id': self.env["res.partner"]._find_accounting_partner(payment.partner_id).id,
            'name': '%s - %s' % (self.name, payment.payment_method_id.name),
            'delivery_partner_id':payment.pos_order_id.pos_delivery_partner.id,
        }
        return self._debit_amounts(partial_vals, amount, amount_converted)


    def _get_sale_vals(self, key, amount, amount_converted):
        res = super(InheritPosSession, self)._get_sale_vals(key, amount, amount_converted)
        if 'with' in res['name']:
            res['name'] = res['name'].replace("with", "exclusive of")
        return res


