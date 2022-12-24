# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class GsPenaltiesAwards(models.Model):
    _name = 'gs.penalties.awards'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Penalties & Awards'
    _rec_name = 'sequence_penalties_awards'

    def get_type_state(self):
        state = {'deduction': 'Deduction',
                 'award': 'Award',}
        return state[self.type]

    name = fields.Char()
    employee_id = fields.Many2one('hr.employee', string="Name",)
    date = fields.Date(string='Date',)
    number_of_days = fields.Integer(string='Number Of Days', )
    type = fields.Selection(string='Type', selection=[('deduction', 'Deduction'), ('award', 'Award'), ],)
    penalties_awards_id = fields.Many2one('gs.penalties.awards.setting', string='Penalties & Awards ', required=False)
    amount = fields.Float(string='Amount', )
    note = fields.Char(string='Reason', )
    is_attachment = fields.Boolean(string="is Attachment?")
    attachment_ids = fields.Many2many('ir.attachment', 'gs_attachment_rel01', 'gs_template_id001', 'gs_attachment_id001' , 'Attachments',)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submit', 'Submitted'),
        ('approve', 'Approved'),
        ('refuse', 'Refused'),
        ('cancel', 'Canceled'),
    ], string="State", default='draft', track_visibility='onchange', copy=False, )
    dedication_month = fields.Date(string='Payment Due Date',)

    is_type_fixed = fields.Boolean(string='Is Fixed Amount?', required=False)
    user_id = fields.Many2one('res.users', 'Responsible', default=lambda self: self.env.user)
    is_send_by_email = fields.Boolean()

    def unlink(self):
        for asset in self:
            if asset.sequence_penalties_awards != _('New'):
                raise UserError(_('You cannot delete a Penalties & Awards that is in %s state.') % (asset.state,))
        return super(GsPenaltiesAwards, self).unlink()

    def action_reset_to_draft(self):
        self.is_send_by_email = False
        return self.write({'state': 'draft'})

    def action_refuse(self):
        return self.write({'state': 'refuse'})

    def action_submit(self):
        if self.sequence_penalties_awards == _('New'):
            self.sequence_penalties_awards = self.env['ir.sequence'].next_by_code('serial_for_penalties_awards') or _('New')
        self.write({'state': 'submit'})

    def action_cancel(self):
        self.write({'state': 'cancel'})

    def action_approve(self):
        self.write({'state': 'approve'})

    recipient_users = fields.Text()

    def send_template_email(self, users, template):
        recipient_users = []
        if users.work_email not in recipient_users:
            recipient_users.append(users.work_email)

        recipient_users = '[%s]' % ', '.join(map(str, recipient_users))
        self.recipient_users = recipient_users

        template_id = template
        template = self.env['mail.template'].browse(template_id)
        template.send_mail(self.id, force_send=True)

    # @api.model
    # def create(self, vals):
    #     if vals.get('sequence_penalties_awards', _('New')) == _('New'):
    #         vals['sequence_penalties_awards'] = self.env['ir.sequence'].next_by_code(
    #             'serial_for_penalties_awards') or _('New')
    #
    #     result = super(GsPenaltiesAwards, self).create(vals)
    #     return result

    sequence_penalties_awards = fields.Char(string='Seq', required=True, copy=False, readonly=True,
                                          index=True, default=lambda self: _('New'))

    @api.onchange('type', 'number_of_days')
    def domain_penalties_awards_id(self):
        return {'domain': {'penalties_awards_id': [('type', '=', self.type)]}}

    @api.onchange('number_of_days', 'penalties_awards_id')
    def _onchange_number_of_days(self):
        for rec in self:
            sum_amount = 0
            if rec.penalties_awards_id.is_type_fixed:
                rec.is_type_fixed = True
            else:
                rec.is_type_fixed = False
                if rec.number_of_days:
                    contract = self.env['hr.contract'].search([('state', '=', 'open'), ('employee_id', '=', rec.employee_id.id)], limit=1)
                    for line in rec.penalties_awards_id.base_amount_ids:
                        if contract._fields['house_allowance_val'].string == line.name:
                            sum_amount += contract.house_allowance_val
                        if contract._fields['trans_allowance_val'].string == line.name:
                            sum_amount += contract.trans_allowance_val
                        if contract._fields['wage'].string == line.name:
                            sum_amount += contract.wage
                        for allowances in contract.contract_allowances:
                            if allowances.allowance_id.name == line.name:
                                sum_amount += allowances.amount
                    print("sum_amount", sum_amount)
                    rec.amount = (sum_amount / rec.penalties_awards_id.base_num) * rec.number_of_days