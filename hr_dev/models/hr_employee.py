from odoo import fields, models, api, _


class Employee(models.Model):
    _inherit = "hr.employee"

    nrp = fields.Char(string='NRP', groups='hr.group_hr_user')
    nrp_external = fields.Char(string='NRP External', groups='hr.group_hr_user')
    religion = fields.Selection([('islam', 'Islam'),('kristen', 'Kristen'), ('katholik', 'Katholik'),
                                 ('hindu', 'Hindu'), ('buddha', 'Buddha'), ('konghucu', 'Konghucu')],
                                groups='hr.group_hr_user')
    area_id = fields.Many2one('res.area', string="Area Kerja", groups='hr.group_hr_user')
    customer_id = fields.Many2one('res.partner', domain=[('customer_rank','>=',1), ('is_company','=',True)],
                                  string="Customer", groups='hr.group_hr_user')
    npwp = fields.Char(string="NPWP", related="address_home_id.vat", store=True, groups='hr.group_hr_user')
    identification_id = fields.Char(related="address_home_id.identification_id", store=True, groups='hr.group_hr_user')
    study_degree_id = fields.Many2one('hr.recruitment.degree', 'Degree', tracking=True, groups='hr.group_hr_user')
    bank_journal_id = fields.Many2one('account.journal', string='Bank Journal',
                                      domain="[('type', 'in', ['cash', 'bank'])]")

    def name_get(self):
        result = []
        for row in self:
            if row.nrp:
                name = row.name + ' - ' + row.nrp
            else:
                name = row.name
            result.append((row.id, name))
        return result

    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        domain = []
        if name:
            domain = ["|", ("name", operator, name), ("nrp", operator, name)]
        return self._search(domain + args, limit=limit, access_rights_uid=name_get_uid)

    @api.model
    def search(self, args, offset=0, limit=80, order='id', count=False):
        """Override to be able to search old_value_char in mail.tracking.value"""
        dotted_field = 'message_ids.tracking_value_ids.old_value_char'
        if any(filter(lambda arg: dotted_field in arg, args)):
            self = self.sudo()
        if len(args) == 3 and (args[1][0] == 'name' or args[2][0] == 'name'):
            args = ['|'] + args + [['nrp', 'ilike', args[1][2]]]
        return super().search(args, offset=offset, limit=limit, order=order, count=count)

    def update_contact(self, vals):
        if self.address_home_id:
            contact = {}
            if 'identification_id' in vals:
                contact['identification_id'] = vals.get('identification_id')
            if 'npwp' in vals:
                contact['vat'] = vals.get('npwp')
            if contact:
                self.address_home_id.update(contact)

    @api.model_create_multi
    def create(self, vals):
        ret = super(Employee, self).create(vals)
        self.update_contact(vals)
        return ret

    def write(self, vals):
        self.update_contact(vals)
        return super(Employee, self).write(vals)
