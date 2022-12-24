# -*- coding: utf-8 -*-

from datetime import date, datetime, timedelta
from odoo import models, fields, api, _
from odoo.exceptions import Warning, UserError


class HrCustody(models.Model):
    """
        Hr custody contract creation model.
        """
    _name = 'hr.custody'
    _description = 'Hr Custody Management'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    read_only = fields.Boolean(string="check field")

    @api.depends('custody_name_one2.amount')
    def _amount_all(self):
        for rec in self:
            amount_t = 0
            for line in rec.custody_name_one2:
                amount_t += line.amount
            rec.update({
                'amount_total': amount_t,
            })

    amount_total = fields.Float(string='Total', store=True, readonly=True, compute='_amount_all', tracking=4)

    recipient_partners = fields.Text()

    def get_recipient_mail(self):
        user_group = self.env.ref("hr.group_hr_user")

        recipient_partners = []
        for group in user_group:
            for recipient in group.users:
                if recipient.partner_id.email not in recipient_partners:
                    recipient_partners.append(recipient.partner_id.email)

        recipient_partners = '[%s]' % ', '.join(map(str, recipient_partners))
        if recipient_partners:
            self.recipient_partners = recipient_partners

    # b_on_create = fields.Boolean(string="check field" , compute='_compute_b_on_create', required=True,
    #                              readonly=False)

    # @api.depends('name', 'custody_name_one2')
    # def _compute_b_on_create(self):
    #     for rec in self:
    #         if len(rec.custody_name_one2) >= 1:
    #             print('len(rec.custody_name_one21221)', len(rec.custody_name_one2))
    #             rec.b_on_create = True
    #         else:
    #             print('len(rec.custody_name_one2124124)', len(rec.custody_name_one2))
    #             rec.b_on_create = False

    @api.onchange('employee')
    def _compute_read_only(self):
        """ Use this function to check weather the user has the permission to change the employee"""
        res_user = self.env['res.users'].search([('id', '=', self._uid)])
        print(res_user.has_group('hr.group_hr_user'))
        if res_user.has_group('hr.group_hr_user'):
            self.read_only = True
        else:
            self.read_only = False

    def mail_reminder(self):
        now = datetime.now() + timedelta(days=1)
        date_now = now.date()
        match = self.search([('state', '=', 'approved')])
        for i in match:
            if i.return_date:
                exp_date = fields.Date.from_string(i.return_date)
                if exp_date <= date_now:
                    base_url = self.env['ir.config_parameter'].get_param('web.base.url')
                    url = base_url + _('/web#id=%s&view_type=form&model=hr.custody&menu_id=') % i.id
                    mail_content = _('Hi %s,<br>As per the %s you took %s on %s for the reason of %s. S0 here we '
                                     'remind you that you have to return that on or before %s. Otherwise, you can '
                                     'renew the reference number(%s) by extending the return date through following '
                                     'link.<br> <div style = "text-align: center; margin-top: 16px;"><a href = "%s"'
                                     'style = "padding: 5px 10px; font-size: 12px; line-height: 18px; color: #FFFFFF; '
                                     'border-color:#875A7B;text-decoration: none; display: inline-block; '
                                     'margin-bottom: 0px; font-weight: 400;text-align: center; vertical-align: middle; '
                                     'cursor: pointer; white-space: nowrap; background-image: none; '
                                     'background-color: #875A7B; border: 1px solid #875A7B; border-radius:3px;">'
                                     'Renew %s</a></div>') % \
                                   (i.employee.name, i.name, i.custody_name.name, i.date_request, i.purpose,
                                    date_now, i.name, url, i.name)
                    main_content = {
                        'subject': _('REMINDER On %s') % i.name,
                        'author_id': self.env.user.partner_id.id,
                        'body_html': mail_content,
                        'email_to': i.employee.work_email,
                    }
                    mail_id = self.env['mail.mail'].create(main_content)
                    mail_id.mail_message_id.body = mail_content
                    mail_id.send()
                    if i.employee.user_id:
                        mail_id.mail_message_id.write(
                            {'needaction_partner_ids': [(4, i.employee.user_id.partner_id.id)]})
                        mail_id.mail_message_id.write({'partner_ids': [(4, i.employee.user_id.partner_id.id)]})

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('hr.custody')
        for rec in self:
            print('len(rec.custody_name_one2)', len(rec.custody_name_one2))
            # if rec.b_on_create == False:
            #     raise UserError(_("property is empty you have add at least one line"))
            if len(rec.custody_name_one2) < 1:
                raise UserError(_("property is empty you have add at least one line"))
        return super(HrCustody, self).create(vals)

    def sent(self):
        template_id = self.env.ref('gs_hr_custody.request_review_mail')
        print(template_id, '==============================================')
        template_id.send_mail(self.id, force_send=True)
        self.state = 'to_approve'

    def approve_request(self):
        self.state = 'approved'

    def reject_request(self):
        self.state = 'rejected'

    def send_mail(self):
        template = self.env.ref('gs_hr_custody.custody_email_notification_template')
        self.env['mail.template'].browse(template.id).send_mail(self.id)
        self.mail_send = True

    def set_to_draft(self):
        self.state = 'draft'

    def renew_approve(self):
        # for custody in self.env['hr.custody'].search([('custody_name', '=', self.custody_name.id)]):
        #     if custody.state == "approved":
        #         raise UserError(_("Custody is not available now"))
        self.return_date = self.renew_date
        self.renew_date = ''
        self.state = 'approved'

    def renew_refuse(self):
        # for custody in self.env['hr.custody'].search([('custody_name', '=', self.custody_name.id)]):
        #     if custody.state == "approved":
        #         raise UserError(_("Custody is not available now"))
        self.renew_date = ''
        self.state = 'approved'

    def approve(self):
        # for custody in self.env['hr.custody'].search([('custody_name', '=', self.custody_name.id)]):
        #     print('custody', custody.id)
        #     if custody.state == "approved":
        #         print('custody.state', custody.state)
        #         raise UserError(_("Custody isss not available now"))
        self.state = 'approved'

    def set_to_return(self):
        self.state = 'returned'
        self.return_date = date.today()

    # return date validation
    @api.constrains('return_date')
    def validate_return_date(self):
        if self.state == 'approved':
            if self.return_date < self.date_request:
                raise Warning('Please Give Valid Return Date')

    name = fields.Char(string='Code', copy=False, help="Code")
    company_id = fields.Many2one('res.company', 'Company', readonly=True, help="Company",
                                 default=lambda self: self.env.user.company_id)
    rejected_reason = fields.Text(string='Rejected Reason', copy=False, readonly=1, help="Reason for the rejection")
    renew_rejected_reason = fields.Text(string='Renew Rejected Reason', copy=False, readonly=1,
                                        help="Renew rejected reason")
    date_request = fields.Date(string='Requested Date', required=True, track_visibility='always', readonly=True,
                               help="Requested date", states={'draft': [('readonly', False)]},
                               default=datetime.now().strftime('%Y-%m-%d'))
    employee = fields.Many2one('hr.employee', string='Employee', required=True, readonly=True, help="Employee",
                               default=lambda self: self.env.user.employee_id.id,
                               states={'draft': [('readonly', False)]})
    partner_id = fields.Many2one('res.partner', string='Partner', required=True,)
    purpose = fields.Char(string='Reason', track_visibility='always', required=False, readonly=True, help="Reason",
                          states={'draft': [('readonly', False)]})
    custody_name = fields.Many2one('custody.property', string='Property', required=False, readonly=True,
                                   help="Property name",
                                   states={'draft': [('readonly', False)]})
    # _________________________________
    custody_name_one2 = fields.One2many("property.line", "custody_name_many2", string="Property",
                                        required=True, copy=True)
    # @api.multi
    def write(self,vals):
        res = super(HrCustody, self).write(vals)
        for rec in self:
            # if rec.b_on_create == False:
            #     raise UserError(_("property is empty you have add at least one line"))
            print('len(rec.custody_name_one2)', len(rec.custody_name_one2))
            if len(rec.custody_name_one2) < 1:
                raise UserError(_("property is empty you have add at least one line"))
        return res

    # @api.model
    # def create(self,vals):
    #     for rec in self:
    #         if len(rec.custody_name_one2) < 1:
    #             raise UserError(_("property is empty you have add at least one line"))
    #     new_record = super(HrCustody, self).create(vals)
    #     return new_record

    # _________________________________
    return_date = fields.Date(string='Return Date', track_visibility='always',
                              help="Return date",)
    renew_date = fields.Date(string='Renewal Return Date', track_visibility='always',
                             help="Return date for the renewal", readonly=True, copy=False)
    notes = fields.Html(string='Notes')
    renew_return_date = fields.Boolean(default=False, copy=False)
    renew_reject = fields.Boolean(default=False, copy=False)
    state = fields.Selection([('draft', 'Draft'), ('to_approve', 'Waiting For Approval'), ('approved', 'Approved'),
                              ('returned', 'Returned'), ('rejected', 'Refused')], string='Status', default='draft',
                             track_visibility='always')
    mail_send = fields.Boolean(string="Mail Send")

    # status_on_delivery_id = fields.Many2one('hr.custody.status', string='Status on Delivery',)
    # status_on_receipt_id = fields.Many2one('hr.custody.status', string='Status on Receipt',)


class HrPropertyName(models.Model):
    """
            Hr property creation model.
            """
    _name = 'custody.property'
    _description = 'Property Name'

    name = fields.Char(string='Property Name', required=True)
    image = fields.Image(string="Image",
                         help="This field holds the image used for this provider, limited to 1024x1024px")
    image_medium = fields.Binary(
        "Medium-sized image", attachment=True,
        help="Medium-sized image of this provider. It is automatically "
             "resized as a 128x128px image, with aspect ratio preserved. "
             "Use this field in form views or some kanban views.")
    image_small = fields.Binary(
        "Small-sized image", attachment=True,
        help="Small-sized image of this provider. It is automatically "
             "resized as a 64x64px image, with aspect ratio preserved. "
             "Use this field anywhere a small image is required.")
    # desc = fields.Html(string='Description', help="Description")
    company_id = fields.Many2one('res.company', 'Company', help="Company",
                                 default=lambda self: self.env.user.company_id)
    property_selection = fields.Selection([('asset', 'Asset'),
                                           ('product', 'Products')],
                                          default='asset',
                                          string='Property From', help="Select the property")

    product_id = fields.Many2one('product.product', string='Product', help="Product")
    currency_id = fields.Many2one('res.currency', string='Currency', readonly=True,
                                  default=lambda self: self.env.company.currency_id.id)

    @api.onchange('property_selection')
    def _domain_asset(self):
        domain = []
        assets_ids = []
        for rec in self:
            all_s = self.env['custody.property'].search([])
            print('all_s==', all_s)
            for s in all_s:
                print('all_s==', s.asset_id)
                print('all_s==', s.asset_id.id)
                assets_ids.append(s.asset_id.id)
                print('assets_ids==', assets_ids)
                # domain = {'asset_id': [('id', 'in', assets_ids)]}
        # return {'domain': domain}
        return {'domain': {'asset_id': [('id', 'not in', assets_ids)]}}

    asset_id = fields.Many2one('account.asset', string='Asset', domain=_domain_asset)
    original_value = fields.Monetary(string="Original Value", related='asset_id.original_value')
    # salvage_value = fields.Monetary(string='Not Depreciable Value', related='asset_id.salvage_value')
    acquisition_date = fields.Date(related='asset_id.acquisition_date')
    price = fields.Float('Price', default=0.0, related='product_id.list_price')

    # def _compute_read_only(self):
    #     """ Use this function to check weather the user has the permission to change the employee"""
    #     res_user = self.env['res.users'].search([('id', '=', self._uid)])
    #     print(res_user.has_group('hr.group_hr_user'))
    #     if res_user.has_group('hr.group_hr_user'):
    #         self.read_only = True
    #     else:
    #         self.read_only = False

    # @api.onchange('property_selection')
    # def onchange_property_selection(self):
    #     if self.property_selection == 'asset':
    #         asset_obj = self.env['ir.module.module'].search([('name', '=', 'account_asset')])
    #         if asset_obj.state != 'installed':
    #             self.asset_true = False
    #             raise UserError(_('No asset module found. Kindly install the asset module.'))
    #         else:
    #             self.asset_true = True

    @api.onchange('product_id')
    def onchange_product(self):
        # print('change prooo')
        self.name = self.product_id.name

    @api.onchange('asset_id')
    def onchange_asset_id(self):
        # print('change asset')
        self.name = self.asset_id.name


class PropertyLine(models.Model):
    _name = 'property.line'
    _description = 'property Custom line'

    custody_name_many2 = fields.Many2one('hr.custody', string='Property22', index=True,
                                         required=False, ondelete='cascade')
    bool_f = fields.Boolean(compute='_compute_func', store=True, default=False)

    @api.depends('custody_name_many2.state')
    def _compute_func(self):
        for rec in self:
            if rec.custody_name_many2.state == 'returned':
                for line in rec.custody_name_many2.custody_name_one2:
                    print('ehfhkeejk')
                    line.bool_f = True
            else:
                for line in rec.custody_name_many2.custody_name_one2:
                    print('ellllllll')
                    line.bool_f = False

    # @api.multi
    # def write(self,vals):
    #     super(PropertyLine, self).write(vals)
    #     self._compute_func()
    #     return True

    @api.onchange('check_box')
    def _domain_property_all(self):
        all_custody_ids = []
        for rec in self:
            all_custody = self.env['hr.custody'].search([])
            # print('all_custody==', all_custody)
            for s in all_custody:
                # print('all_custody===', s.custody_name_one2)
                for line in s.custody_name_one2:
                    # print('all_custody line==', line.property_all)
                    all_custody_ids.append(line.property_all.id)
                    # print('assets_ids==', all_custody_ids)
        # print('assets_ids==', all_custody_ids)
        return {'domain': {'property_all': [('id', 'not in', all_custody_ids)]}}

    property_all = fields.Many2one('custody.property', string='Property', required=True,
                                   change_default=True, domain=_domain_property_all)

    @api.onchange('property_all')
    def onchange_property_all(self):
        for rec in self:
            if rec.property_all:
                # print('property_all', rec.property_all)
                # print('property_all property_selection', rec.property_all.property_selection)
                if rec.property_all.property_selection == 'product':
                    rec.price = rec.property_all.price
                if rec.property_all.property_selection == 'asset':
                    rec.price = rec.property_all.original_value

    check_box = fields.Boolean()
    sequence = fields.Integer(string='Sequence', default=10)
    name_p = fields.Text(string='Description', required=False)

    # original_value = fields.Monetary(string="Original Value", related='property_all.original_value.value')
    acquisition_date = fields.Date(related='property_all.acquisition_date', readonly=False)
    property_selection = fields.Selection([('asset', 'Asset'), ('product', 'Products')], readonly=True, string='Type',
                                          help="Select the property", related='property_all.property_selection')
    # original_value = fields.Many2one(related='property_all.original_value', store=True, string='Currency', readonly=True)
    amount = fields.Float(string="Amount", readonly=True)

    @api.onchange('quantity', 'price')
    def onchange_amount(self):
        for rec in self:
            rec.amount = rec.price * rec.quantity

    quantity = fields.Integer(required=True, default=1)
    price = fields.Float('Price', default=0.0)

    list_price = fields.Float('Price', default=0.0)

    status_on_delivery_id_line = fields.Many2one('hr.custody.status', string='Status on Delivery',)
    status_on_receipt_id_line = fields.Many2one('hr.custody.status', string='Status on Receipt',)
    return_date_line = fields.Date(string='Return Date', track_visibility='always',
                                   help="Return date", default=datetime.now().strftime('%Y-%m-%d'))


class HrReturnDate(models.TransientModel):
    """Hr custody contract renewal wizard"""
    _name = 'wizard.return.date'
    _description = 'Hr Custody Name'

    returned_date = fields.Date(string='Renewal Date', required=1)

    # renewal date validation
    @api.constrains('returned_date')
    def validate_return_date(self):
        context = self._context
        custody_obj = self.env['hr.custody'].search([('id', '=', context.get('custody_id'))])
        if self.returned_date <= custody_obj.date_request:
            raise Warning('Please Give Valid Renewal Date')

    def proceed(self):
        context = self._context
        custody_obj = self.env['hr.custody'].search([('id', '=', context.get('custody_id'))])
        custody_obj.write({'renew_return_date': True,
                           'renew_date': self.returned_date,
                           'state': 'to_approve'})
