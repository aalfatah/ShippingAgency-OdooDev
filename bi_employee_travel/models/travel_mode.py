# -*- coding: utf-8 -*-
# Part of Browseinfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class TravelMode(models.Model):
    _name = "travel.mode"
    _description = "Travel Mode"

    name = fields.Char('Travel Mode')
