from odoo import _, api, fields, models
import dateutil.parser


class SaleOrder(models.Model):
    _inherit = "sale.order"

    cost_structure_id = fields.Many2one('agency.cost.structure', 'Cost Structure', tracking=True)
    sale_cost_structure_line_ids = fields.One2many('sale.cost.structure.line', 'sale_order_id', 'Cost Structure Lines')
    vessel_ids = fields.Many2many('agency.vessel', 'sale_order_vessel_rel', string='Vessel')
    vessel_name = fields.Char(string='Vessel Name', compute='_get_vessel_name')
    last_port_id = fields.Many2one('agency.port', string='Last Port')
    load_port_ids = fields.Many2many('agency.port', 'sale_order_load_port_rel', string='Load Port')
    discharge_port_ids = fields.Many2many('agency.port', 'sale_order_discharge_port_rel', string='Discharge Port')

    client_order_ref = fields.Char(string='No. PO', copy=False, tracking=True)
    po_date = fields.Date(string='Tanggal PO', tracking=True)
    vo_no = fields.Char(string='No. VO', tracking=True)

    grt = fields.Float('GRT', compute='_get_vessel_grt', tracking=True)

    remaining_cost_to_expense = fields.Float('To Expense', compute='_remaining_cost_to_expense')

    def _get_vessel_name(self):
        for s in self:
            vessel_name = False
            if s.vessel_ids:
                vessel_name = ', '.join(s.vessel_ids.mapped('name'))
            s.vessel_name = vessel_name

    @api.onchange('vessel_ids')
    def _get_vessel_grt(self):
        for s in self:
            s.grt = sum(s.vessel_ids.mapped('grt')) if s.vessel_ids else 0

    def _remaining_cost_to_expense(self):
        for order in self:
            order.remaining_cost_to_expense = sum(order.sale_cost_structure_line_ids.filtered(
                                                  lambda c: c.allow_expense and not c.expense_id)
                                                  .mapped('estimated_cost'))

    @api.onchange('cost_structure_id')
    def _onchange_cost_structure_id(self):
        self.vessel_ids = False
        self.last_port_id = False
        self.load_port_ids = False
        self.discharge_port_ids = False
        if self.cost_structure_id:
            self.vessel_ids = [(6, 0, self.cost_structure_id.vessel_ids.ids)]
            self.last_port_id = self.cost_structure_id.last_port_id.id
            self.load_port_ids = [(6, 0, self.cost_structure_id.load_port_ids.ids)]
            self.discharge_port_ids = [(6, 0, self.cost_structure_id.discharge_port_ids.ids)]

    def action_view_cost_structure(self):
        action = self.env['ir.actions.actions']._for_xml_id('sale_port_agency_dev.act_sale_open_cost_structure_view')
        action['domain'] = [('sale_order_id', '=', self.id)]
        tree_view = [(self.env.ref('sale_port_agency_dev.view_sale_cost_structure_tree').id, 'tree')]
        action['views'] = tree_view
        return action

    @api.model_create_multi
    def create(self, vals):
        sale = super(SaleOrder, self).create(vals)
        if 'cost_structure_id' in vals[0]:
            sale.update_cost_structure()
        return sale

    def write(self, vals):
        ret = super(SaleOrder, self).write(vals)
        if 'cost_structure_id' in vals:
            self.update_cost_structure()
        return ret

    def update_cost_structure(self):
        self.env['sale.cost.structure.line'].search([('sale_order_id', '=', self.id)]).unlink()
        if self.cost_structure_id:
            cost_structure_line_ids = self.env['agency.cost.structure.line'].search_read([('cost_structure_id', '=',
                                                                                           self.cost_structure_id.id)])
            # sale_cost_structure_line_ids = []
            for cost_structure_line_id in cost_structure_line_ids:
                rem_fields = ['id', 'message_is_follower', 'message_follower_ids', 'message_partner_ids', 'message_ids',
                              'has_message', 'message_needaction', 'message_needaction_counter', 'message_has_error',
                              'message_has_error_counter', 'message_attachment_count', 'message_main_attachment_id',
                              'website_message_ids', 'message_has_sms_error', 'estimated_cost',
                              '__last_update', 'create_uid', 'create_date', 'write_uid', 'write_date']
                for cost in rem_fields:
                    cost_structure_line_id.pop(cost)
                cost_structure_line_id.update({
                    'sequence': cost_structure_line_id['sequence'],
                    'cost_structure_id': cost_structure_line_id['cost_structure_id'][0],
                    'package_id': cost_structure_line_id.get('package_id') and cost_structure_line_id['package_id'][0],
                    'header_id': cost_structure_line_id.get('header_id') and cost_structure_line_id['header_id'][0],
                    'item_id': cost_structure_line_id.get('item_id') and cost_structure_line_id['item_id'][0],
                    'product_id': cost_structure_line_id.get('product_id') and cost_structure_line_id['product_id'][0],
                })
                self.env['sale.cost.structure.line'].create(cost_structure_line_id | {'sale_order_id': self.id})

    def update_lines(self):
        self.update({'order_line': False})
        if self.sale_cost_structure_line_ids:
            res = self.sale_cost_structure_line_ids.read_group(
                domain=[('sale_order_id', '=', self.id), ('estimated_cost', '!=', 0)],
                fields=['package_id', 'estimated_cost'],
                groupby=['package_id'],
            )
            packages = dict((data['package_id'][0], data['estimated_cost']) for data in res)
            lines = {}
            for package_id, estimated_cost in packages.items():
                package = self.env['agency.cost.package'].browse(package_id)
                if package.product_id.id not in lines:
                    lines[package.product_id.id] = {'product_id': package.product_id.id,
                                                    'name': package.name,
                                                    'price_unit': estimated_cost,
                                                    }
                else:
                    lines[package.product_id.id].update({
                        'name': '%s, %s' % (lines[package.product_id.id]['name'], package.name),
                        'price_unit': lines[package.product_id.id]['price_unit'] + estimated_cost
                    })
            line_ids = []
            for product_id, line in lines.items():
                line_ids.append((0, 0, line))
            self.order_line = line_ids

    def sync_rate_card(self):
        self.ensure_one()
        wizard = self.env.ref("sale_port_agency_dev.sync_rate_card_wizard_view_form")
        return {
            "name": _("Sync. Rate Card"),
            "res_model": "sync.rate.card.wizard",
            "view_mode": "form",
            "view_type": 'form',
            "views": [[wizard.id, 'form']],
            "view_id": wizard.id,
            "target": "new",
            "context": {'default_order_id': self.id},
            # "domain": domain,
            "type": "ir.actions.act_window",
        }

    def sync_cost_structure(self):
        self.env['sale.cost.structure.line'].search([('sale_order_id', '=', self.id)]).update({'standard_cost': 0,
                                                                                               'quantity': 0})
        cost_structure_line_ids = self.env['agency.cost.structure.line'].search_read([('cost_structure_id', '=',
                                                                                       self.cost_structure_id.id)])
        for cost_structure_line_id in cost_structure_line_ids:
            rem_fields = ['id', 'message_is_follower', 'message_follower_ids', 'message_partner_ids', 'message_ids',
                          'has_message', 'message_needaction', 'message_needaction_counter', 'message_has_error',
                          'message_has_error_counter', 'message_attachment_count', 'message_main_attachment_id',
                          'website_message_ids', 'message_has_sms_error', 'estimated_cost',
                          '__last_update', 'create_uid', 'create_date', 'write_uid', 'write_date']
            for cost in rem_fields:
                cost_structure_line_id.pop(cost)
            cost_structure_id = self.env['sale.cost.structure.line'].search([('sale_order_id', '=', self.id),
                                                                             ('item_id', '=',
                                                                              cost_structure_line_id['item_id'][0])])
            if cost_structure_id:
                cost_structure_id.update({'sequence': cost_structure_line_id['sequence'],
                                          'standard_cost': cost_structure_line_id['standard_cost'],
                                          'quantity': cost_structure_line_id['quantity']})
            else:
                cost_structure_line_id.update({
                    'sequence': cost_structure_line_id['sequence'],
                    'cost_structure_id': cost_structure_line_id['cost_structure_id'][0],
                    'package_id': cost_structure_line_id.get('package_id') and cost_structure_line_id['package_id'][0],
                    'header_id': cost_structure_line_id.get('header_id') and cost_structure_line_id['header_id'][0],
                    'item_id': cost_structure_line_id.get('item_id') and cost_structure_line_id['item_id'][0],
                    'product_id': cost_structure_line_id.get('product_id') and cost_structure_line_id['product_id'][0],
                })
                self.env['sale.cost.structure.line'].create(cost_structure_line_id | {'sale_order_id': self.id})

        self.env['sale.cost.structure.line'].search([('sale_order_id', '=', self.id),
                                                     ('standard_cost', '=', 0),
                                                     ('expense_id', '=', False)]).unlink()
