# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import base64
from PIL import Image
import io
import os
from odoo.exceptions import ValidationError

class CompanyBackground(models.Model):
    _inherit = "res.company"

    def _get_domain_leave(self):
        domain = []
        domain.append(('resource_id', '=', False))
        # domain.append(('holiday_type', '=', 'public_holiday'))
        return domain

    global_leave_ids = fields.One2many('resource.calendar.leaves', 'company_id') #, domain=_get_domain_leave) #, domain=[('calendar_id','=',False), ('resource_id','=',False)])
