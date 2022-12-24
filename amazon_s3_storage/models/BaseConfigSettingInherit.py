import ast
from odoo import api, fields, models
from odoo.tools.safe_eval import safe_eval
import logging
_logger = logging.getLogger(__name__)


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    def _default_s3_config(self):
        res = self.env['s3.config'].sudo().search([], limit=1)
        return res.id

    def open_s3_conf(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Amazon S3 Configuration',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 's3.config',
            'res_id': self.s3_config_id.id,
            'target': 'current',
        }

    s3_config_id = fields.Many2one('s3.config', string="S3 Config",
                                   default=_default_s3_config, ondelete='cascade')

