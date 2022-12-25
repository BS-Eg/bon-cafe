# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare
from odoo.exceptions import Warning




class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.model
    def default_get(self, default_fields):
        res = super(AccountMove, self).default_get(default_fields)
        branch_id = False

        if self._context.get('branch_id'):
            branch_id = self._context.get('branch_id')
        elif self.env.user.branch_id:
            branch_id = self.env.user.branch_id.id
        res.update({
            'branch_id' : branch_id
        })
        return res

    branch_id = fields.Many2one('res.branch', string="Branch")

    @api.onchange('branch_id')
    def _onchange_branch_id(self):
        selected_brach = self.branch_id
        if selected_brach:
            user_id = self.env['res.users'].browse(self.env.uid)
            user_branch = user_id.sudo().branch_id
            if user_branch and user_branch.id != selected_brach.id:
                raise UserError("Please select active branch only. Other may create the Multi branch issue. \n\ne.g: If you wish to add other branch then Switch branch from the header and set that.") 


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.model
    def default_get(self, default_fields):
        res = super(AccountMoveLine, self).default_get(default_fields)
        branch_id = False

        if self._context.get('branch_id'):
            branch_id = self._context.get('branch_id')
        elif self.env.user.branch_id:
            branch_id = self.env.user.branch_id.id

        if self.move_id.branch_id :
            branch_id = self.move_id.branch_id.id
        res.update({'branch_id' : branch_id})
        return res

    branch_id = fields.Many2one('res.branch', string="Branch",related="move_id.branch_id",store=True)
    # analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account',
    #                                       index=True,related="payment_id.analytic_account_id1" , store=True,
    #                                       readonly=False, check_company=True,compute="_compute_analytic_account_id", copy=True)
    # analytic_tag_ids = fields.Many2many('account.analytic.tag', string='Analytic Tags',index=True,
    #                                    store=True, readonly=False,
    #                                     check_company=True, copy=True,compute="_compute_analytic_tag_ids",)
    # # overrid _compute_analytic_tag_ids
    # def _compute_analytic_tag_ids(self):
    #     for record in self:
    #         if record.payment_id:
    #             record.analytic_tag_ids = record.payment_id.analytic_tag_id
    #         if not record.exclude_from_invoice_tab or not record.move_id.is_invoice(include_receipts=True):
    #             rec = self.env['account.analytic.default'].account_get(
    #                 product_id=record.product_id.id,
    #                 partner_id=record.partner_id.commercial_partner_id.id or record.move_id.partner_id.commercial_partner_id.id,
    #                 account_id=record.account_id.id,
    #                 user_id=record.env.uid,
    #                 date=record.date,
    #                 company_id=record.move_id.company_id.id
    #             )
    #             if rec:
    #                 record.analytic_tag_ids = rec.analytic_tag_ids
