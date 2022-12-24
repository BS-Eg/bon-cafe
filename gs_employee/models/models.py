# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResPartnerInherit(models.Model):
    _inherit = 'res.partner'
    
    building_no = fields.Char(string='Building No',)
    addition_no = fields.Char(string='Addition No',)
    unit_no = fields.Char(string='Unit No',)


class hr_contract(models.Model):
    _inherit = 'hr.contract'

    is_get_data_notification = fields.Boolean()

    @api.onchange('date_end')
    def onchange_method(self):
        for rec in self:
            if rec.is_get_data_notification:
                rec.is_get_data_notification = False
                employee = self.env['hr.employee'].search([('id', '=', rec.employee_id.id)])
                employee.is_get_data_notification = False


class hr_employee(models.Model):
    _inherit = 'hr.employee'

    work_ext = fields.Char(string="Work Ext ", required=False, )
    emergency_contact_2 = fields.Char(string="Emergency Contact 2", required=False, )
    emergency_phone_2 = fields.Char(string="Emergency Phone 2", required=False, )
    type = fields.Selection(string="",
                            selection=[('sponsorship_system', 'Sponsorship System'), ('hire_system', 'Hre System'),
                                       ('external_warranty', 'External Warranty'), ], required=False, )
    employee_owner_name = fields.Char(string="Employee Owner Name", required=False, )
    employee_owner_number = fields.Char(string="Employee Owner Number", required=False, )
    lease_contract_number = fields.Char(string="Lease Contract Number", required=False, )
    arabic_name = fields.Char(string="Arabic Name", required=False, )
    building_number = fields.Char(string="Building Number", required=False, )
    mail_box = fields.Char(string="mail box", required=False, )
    area = fields.Char(string="Area", required=False, )
    city_sr = fields.Char(string="City", required=False, )
    additional_zip_code = fields.Char(string="Additional Zip Code", required=False, )
    pants_Length = fields.Char(string=" Pants Length", required=False, )
    pants_width = fields.Char(string="Pants width", required=False, )
    shoes_size = fields.Char(string="Shoes Size", required=False, )
    coat_chest = fields.Char(string="", required=False, )
    coat_length = fields.Char(string="", required=False, )
    coat_shoulders = fields.Char(string="", required=False, )
    coat_sleeves = fields.Char(string="", required=False, )
    t_shirt_chest = fields.Char(string="", required=False, )
    t_shirt_length = fields.Char(string="", required=False, )
    t_shirt_shoulders = fields.Char(string="", required=False, )
    t_shirt_sleeves = fields.Char(string="", required=False, )
    is_sizes = fields.Boolean(string='Uniform?',)
    is_driving_license = fields.Boolean(string='Driving License?',)
    issuer_driving_license = fields.Char(string="Issuer", )
    d_l_attachment_id = fields.Many2many('ir.attachment', 'd_l_attachment_id03', 'd_l_attachment_id003', 'd_l_attachment_id0003',
                                        string="Attachment", help='Attachment of Driving License')
    expiry_driving_license_date = fields.Date(string='Expiry Date', help='Expiry date of Driving License')
    type_of_license_id= fields.Many2one('gs.type.of.license', string='Type of license')

    driving_license_restriction_id = fields.Many2one('gs.driving.license.restriction', string='Restriction',)
    is_authority_membership = fields.Boolean(string='Authority membership?', )
    authority_membership_no = fields.Char(string='Membership Number')
    a_m_attachment_id = fields.Many2many('ir.attachment', 'a_m_attachment_id03', 'a_m_attachment_id003',
                                         'a_m_attachment_id0003',
                                         string="Attachment", help='Attachment of Authority Membership')
    expiry_date = fields.Date(string='Expiry Date', help='Expiry date of Authority Membership')

    type_of_authority = fields.Many2one('gs.type.of.membership', string='Type of Authority')
    residence_profession = fields.Many2one('gs.residence.profession', string='Residence Profession',)
    issuer_identification = fields.Char(string="Issuer", )

    is_medical_card = fields.Boolean(string='Medical Card?',)
    issuer_medical_card = fields.Char(string="Issuer", )
    m_c_attachment_id = fields.Many2many('ir.attachment', 'm_c_attachment_id03', 'm_c_attachment_id003', 'm_c_attachment_id0003',
                                        string="Attachment", help='Attachment of Medical Card')
    expiry_medical_card_date = fields.Date(string='Expiry Date', help='Expiry date of Driving License')

    is_get_data_notification = fields.Boolean()

    is_get_id_expiry_date = fields.Boolean()
    is_get_expiry_driving_license = fields.Boolean()
    is_get_passport_expiry = fields.Boolean()
    is_get_expiry_medical_card = fields.Boolean()

    @api.onchange('id_expiry_date', 'expiry_driving_license_date', 'passport_expiry_date', 'expiry_medical_card_date')
    def onchange_method(self):
        if self.is_get_data_notification:
            self.is_get_data_notification = False

    @api.onchange('id_expiry_date')
    def onchange_id_expiry_date(self):
        if self.is_get_id_expiry_date:
            self.is_get_id_expiry_date = False

    @api.onchange('is_get_expiry_driving_license')
    def onchange_is_get_expiry_driving_license(self):
        if self.is_get_expiry_driving_license:
            self.is_get_expiry_driving_license = False

    @api.onchange('is_get_passport_expiry')
    def onchange_is_get_passport_expiry(self):
        if self.is_get_passport_expiry:
            self.is_get_passport_expiry = False

    @api.onchange('is_get_expiry_medical_card')
    def onchange_is_get_expiry_medical_card(self):
        if self.is_get_expiry_medical_card:
            self.is_get_expiry_medical_card = False
