import base64
from odoo import api, models, fields, _
from . import s3_tool
import re
import logging
_logger = logging.getLogger(__name__)


_s3_bucket = False
_s3_encryption_enabled = False

class S3InheritAttachment(models.Model):

	_inherit = "ir.attachment"

	def _get_S3_bucket(self, storage):
		global _s3_encryption_enabled
		global _s3_bucket
		access_key_id, secret_key, bucket_name, do_space_url,_s3_encryption_enabled = s3_tool.parse_bucket_url(
			storage)
		s3 = s3_tool.get_resource(
			access_key_id, secret_key, do_space_url)
		_s3_bucket = s3.Bucket(bucket_name)

	@api.model
	def _file_read(self, fname):
		storage = self._storage()
		if storage[:5] == 's3://':
			if not _s3_bucket:
				self._get_S3_bucket(storage)
			try:
				s3path = self._get_s3_full_path(fname)
				s3_key = _s3_bucket.Object(s3path)
				return s3_key.get()['Body'].read()
			except Exception as e:
				_logger.error("ERROR 404: File not found on AWS S3...%r" % e)
				_logger.error("--not found file-- name %r--",self._get_s3_full_path(fname))

		return super(S3InheritAttachment, self)._file_read(fname)

	@api.model
	def _get_s3_full_path(self, path):
		dbname = self._cr.dbname
		s3path = re.sub('[.]', '', path)
		s3path = s3path.strip('/\\')
		return '/'.join([dbname, s3path])

	def _get_s3_key(self, sha):
		dbname = self._cr.dbname
		fname = sha[:2] + '/' + sha
		return fname, '/'.join([dbname, fname])

	@api.model
	def _file_write(self, bin_value, checksum):
		storage = self._storage()
		if storage[:5] == 's3://':
			if not _s3_bucket:
				self._get_S3_bucket(storage)
			fname, s3path = self._get_s3_key(checksum)
			try:
				if	_s3_encryption_enabled:
					_s3_bucket.Object(s3path).put(Body=bin_value, ServerSideEncryption='AES256')
				else:
					_s3_bucket.Object(s3path).put(Body=bin_value)
			except Exception as e:
				_logger.error("--File Write Exception as e: %r--",e)
		else:
			fname = super(S3InheritAttachment, self)._file_write(bin_value, checksum)
		return fname
	

	def _mark_for_gc(self, fname):
		storage = self._storage()
		if storage[:5] == 's3://':
			try:
				if not	_s3_bucket:
					self._get_S3_bucket(storage)
				new_key = self._get_s3_full_path('checklist/%s' % fname)
				s3_key = _s3_bucket.Object(new_key)
				s3_key.put(Body='')
				_logger.debug('S3: _mark_for_gc key:%s marked for GC', new_key)
			except Exception as e:
				_logger.error('S3: File mark as GC, Storage %r,Exception %r',storage,e)
		else:
			_logger.debug('Using file store SUPER _mark_for_gc able to save key')
			return super(S3InheritAttachment, self)._mark_for_gc(fname)

	
	@api.autovacuum
	def _gc_file_store(self):
		""" Perform the garbage collection of the filestore. """
		storage = self._storage()
		if storage[:5] == 's3://':
			cr = self._cr
			cr.commit()
			cr.execute("SET LOCAL lock_timeout TO '10s'")
			cr.execute("LOCK ir_attachment IN SHARE MODE")
			checklist = {}
			whitelist = set()
			removed = 0
			try:
				if not	_s3_bucket:
					self._get_S3_bucket(storage)
				checklistath = self._cr.dbname+'/checklist/'
				for gc_key in	_s3_bucket.objects.filter(Prefix=self._get_s3_full_path('checklist')):
					key = gc_key.key[len(checklistath):]
					checklist[key] = gc_key.key
				for names in cr.split_for_in_conditions(checklist):
					cr.execute("SELECT store_fname FROM ir_attachment WHERE store_fname IN %s", [names])
					whitelist.update(row[0] for row in cr.fetchall())
				for key, value in checklist.items():
					if key not in whitelist:
						orkey =  self._cr.dbname+'/%s'%key
						s3_key =	_s3_bucket.Object(orkey)
						s3_key.delete()
						s3_key_gc =	_s3_bucket.Object(value)
						s3_key_gc.delete()
						removed += 1
						_logger.info('S3: _file_gc_s3 deleted key:%s successfully', key)
			except Exception as e:
				_logger.error('S3: _file_gc_ method deleted key:EXCEPTION %r'% (e))
			cr.commit()
			_logger.debug("S3: filestore gc %d checked, %d removed", len(checklist), removed)
		else:
			return super(S3InheritAttachment, self)._gc_file_store()
