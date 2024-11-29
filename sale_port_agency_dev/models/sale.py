from odoo import _, api, fields, models
import dateutil.parser


class SaleOrder(models.Model):
    _inherit = "sale.order"

    cost_structure_id = fields.Many2one('agency.cost.structure', 'Cost Structure', tracking=True)
    sale_cost_structure_line_ids = fields.One2many('sale.cost.structure.line', 'sale_order_id', 'Cost Structure Lines')
    vessel_ids = fields.Many2many('agency.vessel', 'sale_order_vessel_rel', string='Vessel')
    last_port_id = fields.Many2one('agency.port', string='Last Port')
    load_port_ids = fields.Many2many('agency.port', 'sale_order_load_port_rel', string='Load Port')
    discharge_port_ids = fields.Many2many('agency.port', 'sale_order_discharge_port_rel', string='Discharge Port')

    client_order_ref = fields.Char(string='No. PO', copy=False, tracking=True)
    po_date = fields.Date(string='Tanggal PO', tracking=True)
    vo_no = fields.Char(string='No. VO', tracking=True)

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
            cost_structure_line_ids = self.env['agency.cost.structure.line'].search_read([('cost_structure_id', '=', self.cost_structure_id.id)])
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
                    'cost_structure_id': cost_structure_line_id['cost_structure_id'][0],
                    'package_id': cost_structure_line_id.get('package_id') and cost_structure_line_id['package_id'][0],
                    'header_id': cost_structure_line_id.get('header_id') and cost_structure_line_id['header_id'][0],
                    'item_id': cost_structure_line_id.get('item_id') and cost_structure_line_id['item_id'][0],
                })
                self.env['sale.cost.structure.line'].create(cost_structure_line_id | {'sale_order_id': self.id})
                # sale_cost_structure_line_ids.append((0, 0, cost_structure_line_id | {'sale_order_id': self.id}))
            # self.sale_cost_structure_line_ids = sale_cost_structure_line_ids

    def update_lines(self):
        self.update({'order_line': False,})
        if self.sale_cost_structure_line_ids:
            res = self.sale_cost_structure_line_ids.read_group(
                domain=[('estimated_cost', '!=', 0)],
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
