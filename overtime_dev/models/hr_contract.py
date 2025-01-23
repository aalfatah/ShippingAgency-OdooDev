from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.safe_eval import safe_eval


class WageContract(models.Model):
    _inherit = 'hr.contract'

    wage_hours_python_compute = fields.Text(string='Python Code', compute="_default_wage", readonly=False)
    over_hour = fields.Float('Hour Wage', compute="_get_over_hour")

    def _default_wage(self):
        # code = ''
        for row in self:
            # code = self.env['ir.config_parameter'].sudo().get_param('wage_hours_python_compute')
            # for line in res_config:
            #     code = line.wage_hours_python_compute
            row.wage_hours_python_compute = self.env['ir.config_parameter'].sudo().get_param('wage_hours_python_compute')

    @api.onchange('wage') #, 'tunjangan_tetap') #, 'tunjangan_tidak_tetap')
    def _get_over_hour(self):
        for row in self:
            localdict = {'wage': row.sudo().wage} #, 'tunjangan_tetap': self.tunjangan_tetap} #, 'tunjangan_tidak_tetap': self.tunjangan_tidak_tetap}
            safe_eval(row.sudo().wage_hours_python_compute, localdict, mode="exec", nocopy=True)
            row.over_hour = ('result' in localdict) and localdict['result'] or 0