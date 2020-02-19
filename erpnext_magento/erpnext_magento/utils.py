# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import frappe
import json
from .exceptions import MagentoSetupError

def disable_magento_sync_for_item(item, rollback=False):
	"""Disable Item if not exist on magento"""
	if rollback:
		frappe.db.rollback()
		
	item.sync_with_magento = 0
	item.sync_qty_with_magento = 0
	item.save(ignore_permissions=True)
	frappe.db.commit()

def disable_magento_sync_on_exception():
	frappe.db.rollback()
	frappe.db.set_value("Magento Settings", None, "enable_magento", 0)
	frappe.db.commit()

def is_magento_enabled():
	magento_settings = frappe.get_doc("Magento Settings")
	if not magento_settings.enable_magento:
		return False
	try:
		magento_settings.validate()
	except MagentoSetupError:
		return False
	
	return True
	
def make_magento_log(title="Sync Log", status="Queued", method="sync_magento", message=None, exception=False, 
name=None, request_data={}):
	if not name:
		name = frappe.db.get_value("Magento Log", {"status": "Queued"})
		
		if name:
			""" if name not provided by log calling method then fetch existing queued state log"""
			log = frappe.get_doc("Magento Log", name)
		
		else:
			""" if queued job is not found create a new one."""
			log = frappe.get_doc({"doctype":"Magento Log"}).insert(ignore_permissions=True)
		
		if exception:
			frappe.db.rollback()
			log = frappe.get_doc({"doctype":"Magento Log"}).insert(ignore_permissions=True)
			
		log.message = message if message else frappe.get_traceback()
		log.title = title[0:140]
		log.method = method
		log.status = status
		log.request_data= json.dumps(request_data)
		
		log.save(ignore_permissions=True)
		frappe.db.commit()