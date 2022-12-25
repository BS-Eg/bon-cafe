# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = 'sale.advance.payment.inv'


    def _create_invoice(self, order, so_line, amount):
        result = super(SaleAdvancePaymentInv, self)._create_invoice(order, so_line, amount)

        branch_id = False

        if order.branch_id:
            branch_id = order.branch_id.id
        elif self.env.user.branch_id:
            branch_id = self.env.user.branch_id.id

        result.write({
            'branch_id' : branch_id
            })

        return result

class AccountPaymentRegisterInv(models.TransientModel):
    _inherit = 'account.payment.register'

    @api.model
    def default_get(self, fields):
        rec = super(AccountPaymentRegisterInv, self).default_get(fields)
        invoice_defaults = self.env['account.move'].browse(self._context.get('active_ids', []))
        if invoice_defaults and len(invoice_defaults) == 1:
            rec['branch_id'] = invoice_defaults.branch_id.id
        return rec



    branch_id = fields.Many2one('res.branch')
    analytic_account_id1 = fields.Many2one(
        comodel_name='account.analytic.account',
        string='Analytic Account',
        required=False)
    analytic_tag_id = fields.Many2many('account.analytic.tag','tags_account_rel','tags_id','accounts_id', string='Analytic Tags',readonly=False,
                                        check_company=True, copy=True)

    # overrid _create_payment_vals_from_wizard method
    def _create_payment_vals_from_wizard(self):
        print('wizerd val payment....')
        payment_vals = {
            'date': self.payment_date,
            'amount': self.amount,
            'payment_type': self.payment_type,
            'partner_type': self.partner_type,
            'ref': self.communication,
            'journal_id': self.journal_id.id,
            'analytic_account_id1': self.analytic_account_id1.id,
            'analytic_tag_id': self.analytic_tag_id.ids,
            'currency_id': self.currency_id.id,
            'partner_id': self.partner_id.id,
            'partner_bank_id': self.partner_bank_id.id,
            'payment_method_line_id': self.payment_method_line_id.id,
            'destination_account_id': self.line_ids[0].account_id.id
        }
        print('pval = ',payment_vals)

        if not self.currency_id.is_zero(self.payment_difference) and self.payment_difference_handling == 'reconcile':
            payment_vals['write_off_line_vals'] = {
                'name': self.writeoff_label,
                'amount': self.payment_difference,
                'account_id': self.writeoff_account_id.id,
            }
        return payment_vals
    # end

    @api.onchange('branch_id')
    def _onchange_branch_id(self):
        selected_brach = self.branch_id
        if selected_brach:
            user_id = self.env['res.users'].browse(self.env.uid)
            user_branch = user_id.sudo().branch_id
            if user_branch and user_branch.id != selected_brach.id:
                raise UserError("Please select active branch only. Other may create the Multi branch issue. \n\ne.g: If you wish to add other branch then Switch branch from the header and set that.") 