# -*- coding: utf-8 -*-
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, _


class HrContractRenew(models.Model):
    _name = 'hr.contract.renew'
    _description = 'Manage Contract Renews'

    sequence = fields.Char("#", track_visibility='onchange')
    contract_id = fields.Many2one('hr.contract')
    date_start = fields.Date("Start Date", track_visibility='onchange')
    date_end = fields.Date("End Date", track_visibility='onchange')
    date_renew = fields.Date("Renew Date", track_visibility='onchange')
    contract_period = fields.Char("Contract Period", track_visibility='onchange')

    @api.onchange('date_start', 'date_end')
    def _onchange_gs_end_date(self):
        if self.date_start and self.date_end:
            rd = relativedelta(self.date_end, self.date_start)
            self.contract_period = str(rd.years) + ' Years & ' + str(rd.months) + ' Months & ' + str(
                rd.days) + ' Days'

    # @api.model
    # def create(self, vals):
    #     latest_val = self.env['hr.contract.renew'].search([('contract_id','=',self.contract_id.id)],order='id desc',limit=1)
    #     str_val = str(int(latest_val.sequence)+1)
    #     vals['sequence'] = str_val
    #     res = super(HrContractRenew, self).create(vals)
    #     return res

    @api.onchange('date_start')
    def _onchange_date_start(self):
        for line in self:
            if line.date_start:
                no = -1
                for l in line.contract_id.renew_date_ids:
                    no += 1
                    l.sequence = no


class HrContract(models.Model):
    _inherit = 'hr.contract'

    is_renew_contract = fields.Boolean("Yearly Renew")
    eos_date = fields.Date("End Of Service Date")
    renew_date = fields.Date("Renew Date", track_visibility='onchange')
    renew_date_ids = fields.One2many('hr.contract.renew', 'contract_id', track_visibility='onchange')
    contract_serial_number = fields.Char(string="Contract Serial Number", track_visibility="onchange", required=True,
                                         copy=False, readonly=True,
                                         index=True, default=lambda self: _('New'))
    notice_period = fields.Integer(string="Notice Period", track_visibility="onchange")
    is_expire = fields.Boolean(compute="_compute_state_notif")

    def compute_gs_date_end(self):
        for rec in self:
            if rec.date_end:
                lines = []
                no = len(rec.renew_date_ids) + 1
                dates = []
                for line in rec.renew_date_ids:
                    dates.append(line.date_end)
                if dates and dates != False:
                    date_end = max(dates)
                    start_date = date_end + relativedelta(days=1)
                else:
                    date_end = self.date_end
                    start_date = self.date_start

                rd = relativedelta(self.date_end, start_date)

                val = {
                    'contract_id': rec.id,
                    'sequence': no,
                    'date_start': start_date,
                    'date_end': rec.date_end,
                    'contract_period': str(rd.years) + ' Years & ' + str(rd.months) + ' Months & ' + str(rd.days) + ' Days',
                }
                lines.append((0, 0, val))
                rec.renew_date_ids = lines

    @api.model
    def create(self, vals):
        if vals.get('contract_serial_number', _('New')) == _('New'):
            vals['contract_serial_number'] = self.env['ir.sequence'].next_by_code('contract_serial_number') or _('New')
        res = super(HrContract, self).create(vals)
        # res._onchange_gs_date_end()
        return res

    # def write(self, vals):
    #     if vals.get("state") == "open":
    #         self._onchange_gs_date_end()
    #     res = super(HrContract, self).write(vals)
    #     return res

    @api.onchange('date_end', 'notice_period')
    def _onchange_date_end(self):
        for rec in self:
            if rec.date_end and rec.notice_period:
                rec.renew_date = rec.date_end - relativedelta(days=rec.notice_period)
            elif rec.notice_period == 0:
                rec.renew_date = rec.date_end

    def make_activity_user(self, user):
        date_deadline = fields.Date.today()
        note = _("Please Review This Contract")
        summary = _("Contract")

        self.sudo().activity_schedule(
            'mail.mail_activity_data_todo', date_deadline,
            note=note,
            user_id=user.id,
            res_id=self.id,
            summary=summary
        )

    @api.depends('state')
    def _compute_state_notif(self):
        for rec in self:
            rec.is_expire = True
            if rec.renew_date == fields.Date.today() and rec.state == 'close':
                employees = self.env['res.groups'].search([('id', '=', self.env.ref('hr.group_hr_user').id)]).users
                for employee in employees:
                    self.make_activity_user(employee)

    def _cron_expire_contract_date(self):
        contracts = self.env['hr.contract'].search([('state', '=', 'open'), ('renew_date', '=', fields.Date.today())])
        if contracts:
            for contract in contracts:
                contract.state = 'close'

    def compute_renew_contract_date(self):
        for line in self:
            eos = False
            if line.eos_date:
                if fields.Date.today() < line.eos_date:
                    eos = True
            if line.is_renew_contract and eos and line.date_end - relativedelta(
                    days=line.notice_days) <= fields.Date.today():
                last_record = line.renew_date_ids.search([('contract_id', '=', line.id)], order='id desc', limit=1)
                last_date_end = last_record.date_end + relativedelta(years=1)
                line.renew_date_ids.create({'contract_id': line.id,
                                            'date_start': last_record.date_end + relativedelta(days=1),
                                            'date_end': last_date_end,
                                            'date_renew': last_date_end - relativedelta(days=line.notice_days)})
                line.date_end = last_date_end
