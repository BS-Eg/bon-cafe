from odoo import models, fields, api, _

class stockpickin(models.Model):
    _inherit = 'stock.picking'
    account_analytic_id = fields.Many2one('account.analytic.account', string='Analytic Account',
                                        )
    analytic_tag_ids = fields.Many2many('account.analytic.tag', string='Analytic Tag',
                                        )


class  AccountMOve(models.Model):
    _inherit = 'account.move'
    account_analytic_id = fields.Many2one('account.analytic.account', string='Analytic Account',
                                        )
    analytic_tag_ids = fields.Many2many('account.analytic.tag', string='Analytic Tag',
                                        )


class StockMove(models.Model):
    _inherit = "stock.move"

    def _prepare_account_move_vals(self, credit_account_id, debit_account_id, journal_id, qty, description, svl_id, cost):
        self.ensure_one()
        move_lines = self._prepare_account_move_line(qty, cost, credit_account_id, debit_account_id, description)
        date = self._context.get('force_period_date', fields.Date.context_today(self))
        return {
            'journal_id': journal_id,
            'line_ids': move_lines,
            'date': date,
            'account_analytic_id': self.picking_id.account_analytic_id.id,
            'analytic_tag_ids': [(6, 0, self.picking_id.analytic_tag_ids.ids)],
            'ref': description,
            'stock_move_id': self.id,
            'stock_valuation_layer_ids': [(6, None, [svl_id])],
            'move_type': 'entry',
        }
