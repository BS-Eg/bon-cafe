# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging

from odoo.tools.translate import _
from odoo.tools import email_normalize
from odoo.exceptions import UserError

from odoo import api, fields, models, Command


_logger = logging.getLogger(__name__)


class EmployeePortalWizard(models.TransientModel):
    """
        A wizard to manage the creation/removal of portal users.
    """

    _name = 'employee.portal.wizard'
    _description = 'Grant Portal Access'

    def _default_partner_ids(self):
        employee_ids = self.env.context.get('default_employee_ids', []) or self.env.context.get('active_ids', [])
        contact_ids = set()
        for employee in self.env['hr.employee'].sudo().browse(employee_ids):
            contact_partners = employee
            contact_ids |= set(contact_partners.ids)

        return [Command.link(contact_id) for contact_id in contact_ids]

    employee_ids = fields.Many2many('hr.employee', string='Partners', default=_default_partner_ids)
    user_ids = fields.One2many('employee.portal.wizard.user', 'wizard_id', string='Users', compute='_compute_user_ids', store=True, readonly=False)
    welcome_message = fields.Text('Invitation Message', help="This text is included in the email sent to new users of the portal.")

    @api.depends('employee_ids')
    def _compute_user_ids(self):
        for portal_wizard in self:
            portal_wizard.user_ids = [
                Command.create({
                    'employee_id': employee.id,
                    'email': employee.work_email,
                })
                for employee in portal_wizard.employee_ids
            ]

    @api.model
    def action_open_wizard(self):
        """Create a "portal.wizard" and open the form view.

        We need a server action for that because the one2many "user_ids" records need to
        exist to be able to execute an a button action on it. If they have no ID, the
        buttons will be disabled and we won't be able to click on them.

        That's why we need a server action, to create the records and then open the form
        view on them.
        """
        portal_wizard = self.create({})
        return portal_wizard._action_open_modal()

    def _action_open_modal(self):
        """Allow to keep the wizard modal open after executing the action."""
        self.refresh()
        return {
            'name': _('Portal Access Management'),
            'type': 'ir.actions.act_window',
            'res_model': 'employee.portal.wizard',
            'view_type': 'form',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
        }


class EmployeePortalWizardUser(models.TransientModel):
    """
        A model to configure users in the portal wizard.
    """

    _name = 'employee.portal.wizard.user'
    _description = 'Portal User Config'

    wizard_id = fields.Many2one('employee.portal.wizard', string='Wizard', required=True, ondelete='cascade')
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True, readonly=True, ondelete='cascade')
    email = fields.Char('Email')
    user_id = fields.Many2one('res.users', string='User', compute='_compute_user_id', compute_sudo=True)
    partner_id = fields.Many2one('res.partner', related="user_id.partner_id", string="partner")
    login_date = fields.Datetime(related='user_id.login_date', string='Latest Authentication')
    is_portal = fields.Boolean('Is Portal', compute='_compute_group_details')
    is_internal = fields.Boolean('Is Internal', compute='_compute_group_details')

    @api.depends('employee_id')
    def _compute_user_id(self):
        for portal_wizard_user in self:
            user = portal_wizard_user.employee_id.with_context(active_test=False).user_id
            portal_wizard_user.user_id = user[0] if user else False

    @api.depends('user_id', 'user_id.groups_id')
    def _compute_group_details(self):
        for portal_wizard_user in self:
            user = portal_wizard_user.user_id

            if user and user.has_group('base.group_user'):
                portal_wizard_user.is_internal = True
                portal_wizard_user.is_portal = False
            elif user and user.has_group('base.group_portal'):
                portal_wizard_user.is_internal = False
                portal_wizard_user.is_portal = True
            else:
                portal_wizard_user.is_internal = False
                portal_wizard_user.is_portal = False

    def action_grant_access(self):
        """Grant the portal access to the partner.

        If the partner has no linked user, we will create a new one in the same company
        as the partner (or in the current company if not set).

        An invitation email will be sent to the partner.
        """
        self.ensure_one()
        self._assert_user_email_uniqueness()

        if self.is_portal or self.is_internal:
            raise UserError(_('The partner "%s" already has the portal access.', self.employee_id.name))

        group_portal = self.env.ref('base.group_portal')
        group_public = self.env.ref('base.group_public')

        # update partner email, if a new one was introduced
        if self.employee_id.work_email != self.email:
            self.employee_id.write({'work_email': self.email})

        user_sudo = self.user_id.sudo()

        if not user_sudo:
            # create a user if necessary and make sure it is in the portal group
            company = self.employee_id.company_id or self.env.company
            user_sudo = self.sudo().with_company(company.id)._create_user()
        if not user_sudo.active or not self.is_portal:
            user_sudo.write({'active': True, 'groups_id': [(4, group_portal.id), (3, group_public.id)]})
            # prepare for the signup process
            user_sudo.partner_id.signup_prepare()
        self.employee_id.user_id = user_sudo.id
        self.with_context(active_test=True)._send_email()

        return self.wizard_id._action_open_modal()

    def action_revoke_access(self):
        """Remove the user of the partner from the portal group.

        If the user was only in the portal group, we archive it.
        """
        self.ensure_one()
        self._assert_user_email_uniqueness()

        if not self.is_portal:
            raise UserError(_('The partner "%s" has no portal access.', self.employee_id.name))

        group_portal = self.env.ref('base.group_portal')
        group_public = self.env.ref('base.group_public')

        # update partner email, if a new one was introduced
        if self.partner_id.email != self.email:
            self.partner_id.write({'email': self.email})

        # Remove the sign up token, so it can not be used
        self.partner_id.sudo().signup_token = False

        user_sudo = self.user_id.sudo()

        # remove the user from the portal group
        if user_sudo and user_sudo.has_group('base.group_portal'):
            # if user belongs to portal only, deactivate it
            if len(user_sudo.groups_id) <= 1:
                user_sudo.write({'groups_id': [(3, group_portal.id), (4, group_public.id)], 'active': False})
            else:
                user_sudo.write({'groups_id': [(3, group_portal.id), (4, group_public.id)]})

        return self.wizard_id._action_open_modal()

    def action_invite_again(self):
        """Re-send the invitation email to the partner."""
        self.ensure_one()

        if not self.is_portal:
            raise UserError(_('You should first grant the portal access to the partner "%s".', self.partner_id.name))

        # update partner email, if a new one was introduced
        if self.partner_id.email != self.email:
            self.partner_id.write({'email': self.email})

        self.with_context(active_test=True)._send_email()

        return self.wizard_id._action_open_modal()

    def _create_user(self):
        """ create a new user for wizard_user.partner_id
            :returns record of res.users
        """
        partners = self.env['res.partner'].search([('email', '=ilike', self.email)], limit=1)
        if not partners:
            partners = self.env['res.partner'].create({
                'name': self.employee_id.name,
                'email': self.email,
                'phone': self.employee_id.work_phone
                })

        return self.env['res.users'].with_context(no_reset_password=True)._create_user_from_template({
            'email': email_normalize(self.email),
            'login': email_normalize(self.email),
            'partner_id': partners.id,
            'company_id': self.env.company.id,
            'company_ids': [(6, 0, self.env.company.ids)],
        })

    def _send_email(self):
        """ send notification email to a new portal user """
        self.ensure_one()

        # determine subject and body in the portal user's language
        template = self.env.ref('wt_portal_attendances.employee_mail_template_data_portal_welcome')
        if not template:
            raise UserError(_('The template "Portal: new user" not found for sending email to the portal user.'))

        lang = self.user_id.sudo().lang
        partner = self.user_id.sudo().partner_id

        portal_url = partner.with_context(signup_force_type_in_url='', lang=lang)._get_signup_url_for_action()[partner.id]
        partner.signup_prepare()

        template.with_context(dbname=self._cr.dbname, portal_url=portal_url, lang=lang).send_mail(self.id, force_send=True)

        return True

    def _assert_user_email_uniqueness(self):
        """Check that the email can be used to create a new user."""
        self.ensure_one()

        email = email_normalize(self.email)

        if not email:
            raise UserError(_('The contact "%s" does not have a valid email.', self.employee_id.name))

        user = self.env['res.users'].sudo().with_context(active_test=False).search([
            ('id', '!=', self.user_id.id),
            ('login', '=ilike', email),
        ])

        if user:
            raise UserError(_('The contact "%s" has the same email has an existing user (%s).', self.employee_id.name, user.name))
