from odoo import _, api, fields, models
import dateutil.parser


class SaleOrder(models.Model):
    _inherit = "sale.order"

    cost_structure_id = fields.Many2one('agency.cost.structure', 'Cost Structure', tracking=True)
    sale_cost_structure_line_ids = fields.One2many('sale.cost.structure.line', 'sale_order_id', 'Cost Structure Lines')
    vessel_ids = fields.Many2many('agency.vessel', string='Vessel', related='cost_structure_id.vessel_ids')
    last_port_id = fields.Many2one('agency.port', 'Last Port', related='cost_structure_id.last_port_id')
    load_port_ids = fields.Many2many('agency.port', 'Load Port', related='cost_structure_id.load_port_ids')
    discharge_port_ids = fields.Many2many('agency.port', 'Discharge Port',
                                          related='cost_structure_id.discharge_port_ids')

    client_order_ref = fields.Char(string='No. PO', copy=False, tracking=True)
    po_date = fields.Date(string='Tanggal PO', tracking=True)
    vo_no = fields.Char(string='No. VO', tracking=True)

    def action_view_cost_structure(self):
        action = self.env['ir.actions.actions']._for_xml_id('sale_port_agency_dev.act_sale_open_cost_structure_view')
        action['domain'] = [('sale_order_id', '=', self.id)]
        tree_view = [(self.env.ref('sale_port_agency_dev.view_sale_cost_structure_tree').id, 'tree')]
        action['views'] = tree_view
        return action

    def write(self, vals):
        ret = super(SaleOrder, self).write(vals)
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
                              'website_message_ids', 'message_has_sms_error',
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
            line_ids = []
            for package_id, estimated_cost in packages.items():
                line_data = {
                    'product_id': self.env['agency.cost.package'].browse(package_id).product_id.id,
                    'price_unit': estimated_cost,
                }
                line_ids.append((0, 0, line_data))
            self.order_line = line_ids
    # gr_no = fields.Char(string='GR No.', tracking=True) #, readonly=True, states={'draft': [('readonly', False)]}, tracking=True)
    # gr_date = fields.Date(string='GR Date', tracking=True) #, readonly=True, states={'draft': [('readonly', False)]}, tracking=True)
    #
    # perihal = fields.Char(string="Perihal")
    # up = fields.Char(string="Up")
    # job_title = fields.Char(string="Job Title")
    #
    # signed_quotation_name = fields.Char('Signed Quotation Name')
    # signed_quotation_title = fields.Char('Signed Quotation Job Title')
    # signed_bast_name = fields.Char('Signed BAST Name')
    # signed_bast_title = fields.Char('Signed BAST Job Title')
    # signed_bast2_name = fields.Char('Signed BAST 2 Name')
    # signed_bast2_title = fields.Char('Signed BAST 2 Job Title', default='Warehouse')
    #
    # agreement_id = fields.Many2one(copy=True,)

    # def date_id1(self):
    #     if self.date_order:
    #         tanggal = dateutil.parser.parse(str(self.date_order)).date()
    #
    #         tanggal = str(tanggal)
    #         full_tanggal = (tanggal).split("-")
    #         tahun = full_tanggal[0]
    #         bulan = full_tanggal[1]
    #         if bulan == "01":
    #             bulan = "Januari"
    #         elif bulan == "02":
    #             bulan = "Februari"
    #         elif bulan == "03":
    #             bulan = "Maret"
    #         elif bulan == "04":
    #             bulan = "April"
    #         elif bulan == "05":
    #             bulan = "Mei"
    #         elif bulan == "06":
    #             bulan = "Juni"
    #         elif bulan == "07":
    #             bulan = "Juli"
    #         elif bulan == "08":
    #             bulan = "Agustus"
    #         elif bulan == "09":
    #             bulan = "September"
    #         elif bulan == "10":
    #             bulan = "Oktober"
    #         elif bulan == "11":
    #             bulan = "November"
    #         else:
    #             bulan = "Desember"
    #         tanggal = full_tanggal[2]
    #         final_tanggal = tanggal + " " + bulan + " " + tahun
    #         return final_tanggal
    #
    # def sales_person_employee(self):
    #     return self.env['hr.employee'].sudo().search([('user_id', '=', self.user_id.id)])