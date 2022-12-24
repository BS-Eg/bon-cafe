# -*- coding: utf-8 -*-

from odoo import models, fields, api


class GsPenaltiesAwardsSetting(models.Model):
    _name = 'gs.penalties.awards.setting'
    _description = 'Penalties & Awards Setting'

    name = fields.Char()
    type = fields.Selection(string='Type', selection=[('deduction', 'Deduction'), ('award', 'Award'),
                                                      ],)

    is_type_fixed = fields.Boolean(string='Is Fixed Amount?', required=False)

    base_amount_ids = fields.Many2many('allowances.collect', 'base_amount_ids01', 'base_amount_ids001',
                                       'base_amount_ids0001')

    base_num = fields.Integer(string='Base Number',)