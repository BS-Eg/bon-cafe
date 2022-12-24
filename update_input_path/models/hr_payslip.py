# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from odoo.exceptions import ValidationError,UserError
from odoo.tools import float_compare, float_is_zero


class HrPayslipEmployees(models.TransientModel):
    _inherit ='hr.payslip.employees'

    def action_incentive_payslip_done(self):
        """
            Generate the accounting entries related to the selected payslips
            A move is created for each journal and for each month.
        """
        res = super(HrPayslip, self).action_payslip_done()
        precision = self.env['decimal.precision'].precision_get('Payroll')

        # Add payslip without run
        payslips_to_post = self.filtered(lambda slip: not slip.payslip_run_id)

        # Adding pay slips from a batch and deleting pay slips with a batch that is not ready for validation.
        payslip_runs = (self - payslips_to_post).mapped('payslip_run_id')
        for run in payslip_runs:
            if run._are_payslips_ready():
                payslips_to_post |= run.slip_ids

        # A payslip need to have a done state and not an accounting move.
        payslips_to_post = payslips_to_post.filtered(lambda slip: slip.state == 'done' and not slip.incentive_move_id)

        # Check that a journal exists on all the structures
        if any(not payslip.struct_id for payslip in payslips_to_post):
            raise ValidationError(_('One of the contract for these payslips has no structure type.'))
        if any(not structure.journal_id for structure in payslips_to_post.mapped('struct_id')):
            raise ValidationError(_('One of the payroll structures has no account journal defined on it.'))

        # Map all payslips by structure journal and pay slips month.
        # {'journal_id': {'month': [slip_ids]}}
        slip_mapped_data = {
            slip.struct_id.journal_id.id: {fields.Date().end_of(slip.date_to, 'month'): self.env['hr.payslip']} for slip
            in payslips_to_post}
        for slip in payslips_to_post:
            slip_mapped_data[slip.struct_id.journal_id.id][fields.Date().end_of(slip.date_to, 'month')] |= slip

        for journal_id in slip_mapped_data:  # For each journal_id.
            for slip_date in slip_mapped_data[journal_id]:  # For each month.
                line_ids = []
                debit_sum = 0.0
                credit_sum = 0.0
                date = slip_date
                move_dict = {
                    'narration': '',
                    'ref': date.strftime('%B %Y'),
                    'journal_id': journal_id,
                    'date': date,
                }

                for slip in slip_mapped_data[journal_id][slip_date]:
                    move_dict['narration'] += slip.number or '' + ' - ' + slip.employee_id.name or ''
                    move_dict['narration'] += '\n'
                    for line in slip.line_ids.filtered(lambda line: line.category_id):
                        amount = -line.total if slip.credit_note else line.total
                        if line.code == 'NET':  # Check if the line is the 'Net Salary'.
                            for tmp_line in slip.line_ids.filtered(lambda line: line.category_id):
                                if tmp_line.salary_rule_id.not_computed_in_net:  # Check if the rule must be computed in the 'Net Salary' or not.
                                    if amount > 0:
                                        amount -= abs(tmp_line.total)
                                    elif amount < 0:
                                        amount += abs(tmp_line.total)
                        if float_is_zero(amount, precision_digits=precision):
                            continue
                        debit_account_id = line.salary_rule_id.account_debit.id
                        credit_account_id = line.salary_rule_id.account_credit.id

                        if debit_account_id:  # If the rule has a debit account.
                            debit = amount if amount > 0.0 else 0.0
                            credit = -amount if amount < 0.0 else 0.0

                            existing_debit_lines = (
                                line_id for line_id in line_ids if
                                line_id['name'] == line.name
                                and line_id['account_id'] == debit_account_id
                                and ((line_id['debit'] > 0 and credit <= 0) or (line_id['credit'] > 0 and debit <= 0)))
                            debit_line = next(existing_debit_lines, False)

                            if not debit_line:
                                debit_line = {
                                    'name': line.name,
                                    'partner_id': False,
                                    'account_id': debit_account_id,
                                    'journal_id': slip.struct_id.journal_id.id,
                                    'date': date,
                                    'debit': debit,
                                    'credit': credit,
                                    'analytic_account_id': line.salary_rule_id.analytic_account_id.id or slip.contract_id.analytic_account_id.id,
                                }
                                line_ids.append(debit_line)
                            else:
                                debit_line['debit'] += debit
                                debit_line['credit'] += credit

                        if credit_account_id:  # If the rule has a credit account.
                            debit = -amount if amount < 0.0 else 0.0
                            credit = amount if amount > 0.0 else 0.0
                            existing_credit_line = (
                                line_id for line_id in line_ids if
                                line_id['name'] == line.name
                                and line_id['account_id'] == credit_account_id
                                and (line_id['debit'] > 0 and credit <= 0) or (line_id['credit'] > 0 and debit <= 0)
                            )
                            credit_line = next(existing_credit_line, False)

                            if not credit_line:
                                credit_line = {
                                    'name': line.name,
                                    'partner_id': False,
                                    'account_id': credit_account_id,
                                    'journal_id': slip.struct_id.journal_id.id,
                                    'date': date,
                                    'debit': debit,
                                    'credit': credit,
                                    'analytic_account_id': line.salary_rule_id.analytic_account_id.id or slip.contract_id.analytic_account_id.id,
                                }
                                line_ids.append(credit_line)
                            else:
                                credit_line['debit'] += debit
                                credit_line['credit'] += credit

                for line_id in line_ids:  # Get the debit and credit sum.
                    debit_sum += line_id['debit']
                    credit_sum += line_id['credit']

                # The code below is called if there is an error in the balance between credit and debit sum.
                if float_compare(credit_sum, debit_sum, precision_digits=precision) == -1:
                    acc_id = slip.journal_id.default_credit_account_id.id
                    if not acc_id:
                        raise UserError(
                            _('The Expense Journal "%s" has not properly configured the Credit Account!') % (
                                slip.journal_id.name))
                    existing_adjustment_line = (
                        line_id for line_id in line_ids if line_id['name'] == _('Adjustment Entry')
                    )
                    adjust_credit = next(existing_adjustment_line, False)

                    if not adjust_credit:
                        adjust_credit = {
                            'name': _('Adjustment Entry'),
                            'partner_id': False,
                            'account_id': acc_id,
                            'journal_id': slip.journal_id.id,
                            'date': date,
                            'debit': 0.0,
                            'credit': debit_sum - credit_sum,
                        }
                        line_ids.append(adjust_credit)
                    else:
                        adjust_credit['credit'] = debit_sum - credit_sum

                elif float_compare(debit_sum, credit_sum, precision_digits=precision) == -1:
                    acc_id = slip.journal_id.default_debit_account_id.id
                    if not acc_id:
                        raise UserError(_('The Expense Journal "%s" has not properly configured the Debit Account!') % (
                            slip.journal_id.name))
                    existing_adjustment_line = (
                        line_id for line_id in line_ids if line_id['name'] == _('Adjustment Entry')
                    )
                    adjust_debit = next(existing_adjustment_line, False)

                    if not adjust_debit:
                        adjust_debit = {
                            'name': _('Adjustment Entry'),
                            'partner_id': False,
                            'account_id': acc_id,
                            'journal_id': slip.journal_id.id,
                            'date': date,
                            'debit': credit_sum - debit_sum,
                            'credit': 0.0,
                        }
                        line_ids.append(adjust_debit)
                    else:
                        adjust_debit['debit'] = credit_sum - debit_sum

                # Add accounting lines in the move
                move_dict['line_ids'] = [(0, 0, line_vals) for line_vals in line_ids]
                move = self.env['account.move'].create(move_dict)
                for slip in slip_mapped_data[journal_id][slip_date]:
                    slip.write({'incentive_move_id': move.id, 'date': date})
        return res


    def compute_sheet(self):
        self.ensure_one()
        if not self.env.context.get('active_id'):
            from_date = fields.Date.to_date(self.env.context.get('default_date_start'))
            end_date = fields.Date.to_date(self.env.context.get('default_date_end'))
            payslip_run = self.env['hr.payslip.run'].create({
                'name': from_date.strftime('%B %Y'),
                'date_start': from_date,
                'date_end': end_date,
            })
        else:
            payslip_run = self.env['hr.payslip.run'].browse(self.env.context.get('active_id'))

        if not self.employee_ids:
            raise UserError(_("You must select employee(s) to generate payslip(s)."))

        payslips = self.env['hr.payslip']
        Payslip = self.env['hr.payslip']

        contracts = self.employee_ids._get_contracts(payslip_run.date_start, payslip_run.date_end,
                                                     states=['open', 'close'])
        contracts._generate_work_entries(payslip_run.date_start, payslip_run.date_end)
        work_entries = self.env['hr.work.entry'].search([
            ('date_start', '<=', payslip_run.date_end),
            ('date_stop', '>=', payslip_run.date_start),
            ('employee_id', 'in', self.employee_ids.ids),
        ])
        self._check_undefined_slots(work_entries, payslip_run)

        validated = work_entries.action_validate()
        if not validated:
            raise UserError(_("Some work entries could not be validated."))

        default_values = Payslip.default_get(Payslip.fields_get())
        for contract in contracts:
            values = dict(default_values, **{
                'employee_id': contract.employee_id.id,
                'credit_note': payslip_run.credit_note,
                'payslip_run_id': payslip_run.id,
                'date_from': payslip_run.date_start,
                'date_to': payslip_run.date_end,
                'contract_id': contract.id,
                'struct_id': self.structure_id.id or contract.structure_type_id.default_struct_id.id,
            })
            payslip = self.env['hr.payslip'].new(values)
            payslip._onchange_employee()
            values = payslip._convert_to_write(payslip._cache)
            payslips += Payslip.create(values)
        # payslips.compute_sheet()
        payslip_run.state = 'verify'

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'hr.payslip.run',
            'views': [[False, 'form']],
            'res_id': payslip_run.id,
        }


class HrPayslip(models.Model):
    _inherit ='hr.payslip'

    department_id=fields.Many2one('hr.department',related='employee_id.department_id',store=True)
    def _get_new_input_lines(self):
        res=[]
        lines = {}
        other_input = self.env['hr.payslip.input.type'].search([('struct_ids','in',[self.struct_id.id])])
        for line in other_input:
            lines = {
                'input_type_id': line.id,
                'amount': 0.0,
            }
            res.append(lines)
        if self.struct_id:
            input_line_values =res
            input_lines = self.input_line_ids.browse([])
            for r in input_line_values:
                input_lines |= input_lines.new(r)
            return input_lines
        else:
            return [(5, False, False)]

    @api.depends('employee_id', 'contract_id', 'struct_id', 'date_from', 'date_to', 'struct_id')
    def _compute_input_line_ids(self):
        res=super(HrPayslip, self)._compute_input_line_ids()
        for slip in self:
            slip.input_line_ids = self._get_new_input_lines()
        return res

    def _get_worked_day_lines(self):
        res=super(HrPayslip, self)._get_worked_day_lines()
        lines={}
        types=[]
        work_entry=self.env['hr.work.entry.type'].search([('appear_on_payslip','=',True)])
        for line in work_entry:
                if len(res) > 0:
                    for rec in res:
                        types.append(rec['work_entry_type_id'])
                    if line.id not in types:
                            lines = {
                                'sequence': line.sequence,
                                'work_entry_type_id': line.id,
                                'number_of_days':0.0,
                                'number_of_hours': 0.0,
                                'amount': 0.0,
                            }
                            res.append(lines)
                else:
                    lines = {
                        'sequence': line.sequence,
                        'work_entry_type_id': line.id,
                        'number_of_days':0.0,
                        'number_of_hours': 0.0,
                        'amount': 0.0,
                    }
                    res.append(lines)
        return res

class HrWorkEntryType(models.Model):
    _inherit = 'hr.work.entry.type'
    appear_on_payslip=fields.Boolean()
    number_of_days=fields.Float()
    
    @api.constrains('number_of_days')
    def not_minus(self):
        for rec in self:
            if rec.number_of_days < 0:
                raise ValidationError(_('Number Of Days Should Not Be Less Than Zero'))

class HrPayslipInputType(models.Model):
    _inherit = 'hr.payslip.input.type'
    input_path=fields.Boolean()
