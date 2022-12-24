import ast
from odoo import api, fields, models
from odoo.tools.safe_eval import safe_eval
import logging
from . import s3_tool
from odoo.exceptions import UserError
_logger = logging.getLogger(__name__)

ASSETS = ["text/css", "application/javascript", "application/octet-stream"]


class S3Config(models.Model):

	_name = "s3.config"
	_description = "Model For Storing S3 Config Values"

	name = fields.Char(string='Name', help="Amazon S3 Cloud Config name", readonly=True)
	amazonS3bucket_name = fields.Char(
		string='Bucket Name', help="This allows users to store data in Bucket")
	amazonS3secretkey = fields.Char(
		string='Secret key', help="Amazon S3 Cloud Connection")
	amazonS3accessKeyId = fields.Char(
		string='Access Key Id', help="Amazon S3 Cloud Connection access key Id")
	bucket_location = fields.Char(
		string='Bucket Location', help="Amazon S3 Bucket Location")
	s3_location_constraint = fields.Char(
		string='Location Constraint', help="Amazon S3 Location Constraint", compute="_getLocationConstraint")
	is_store = fields.Boolean("Is Active", default=False)

	def _getLocationConstraint(self):
		parameter = " "
		if self.is_store:
			parameter = "s3://%s:%s@%s&s3.%s.amazonaws.com" % (self.amazonS3accessKeyId,
															   self.amazonS3secretkey, self.amazonS3bucket_name, self.bucket_location)
		self.s3_location_constraint = parameter
		result = self.env['ir.config_parameter'].sudo().set_param(
			'ir_attachment.location', parameter)
		return result
