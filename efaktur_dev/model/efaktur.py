from odoo import api, fields, models, _


class Efaktur(models.Model):
    _name = 'efaktur.efaktur'
    _description = 'eFaktur'

    name = fields.Char("eFaktur Number", required=True)
    year = fields.Integer(string="Year", required=False,)

    invoice_ids = fields.One2many(comodel_name="account.move",
                                  inverse_name="efaktur_id",
                                  string="Invoices", required=False, )
    is_used = fields.Boolean(string="Is Used", compute="_used", store=True , readonly=False)

    @api.depends('invoice_ids')
    def _used(self):
        for efaktur in self:
            if efaktur.invoice_ids:
                efaktur.is_used = True
            else:
                efaktur.is_used = False

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "eFaktur Number tidak boleh duplikat"),
    ]