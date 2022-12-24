# -*- coding: utf-8 -*-


from odoo import fields, models, _


class PosConfig(models.Model):
    _inherit = 'pos.config'

    foodic_branch_id = fields.Char('Foodic Branch Id')
    opening_from = fields.Char('Opening From')
    opening_to = fields.Char('Opening To')
    reference = fields.Char('Reference')
    name_localized = fields.Char('Name Localized')
    phone = fields.Char('Phone')

    def set_branches_to_odoo(self, res):
        i = 0
        for branch in res.get('data'):
            i += 1
            vals = {
                'foodic_branch_id': branch.get('id'),
                'name': branch.get('name'),
                'name_localized': branch.get('name_localized'),
                'reference': branch.get('reference'),
                'phone': branch.get('phone'),
                'opening_from': branch.get('opening_from'),
                'opening_to': branch.get('opening_to'),
                'module_pos_restaurant': True,
            }
            branch_id = self.search([('foodic_branch_id', '=', branch.get('id'))], limit=1)
            if branch_id:
                branch_id.update(vals)
            else:
                branch_id.create(vals)
            if i % 100 == 0:
                self.env.cr.commit()
        self.env.cr.commit()
