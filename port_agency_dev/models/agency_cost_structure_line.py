from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools.safe_eval import safe_eval


class CostStructureLine(models.Model):
    _name = 'agency.cost.structure.line'
    _description = 'Cost Structure Line'
    _inherit = ['mail.thread']

    def _key_selection(self):
        return [
            ('labor', 'Labour'),
            ('material', 'Material'),
            ('equipment', 'Equipment'),
            ('subcontract', 'Subcontractor'),
        ]

    company_id = fields.Many2one(comodel_name="res.company", string="Company", default=lambda self: self.env.company, required=True, store=True, readonly=True)
    base_currency_id = fields.Many2one(comodel_name="res.currency", string='Base Currency', default=lambda self: self.env.company.currency_id)
    currency_id = fields.Many2one(comodel_name="res.currency", string='Currency', related="bill_quantity_id.currency_id", store=True, readonly=False)
    description = fields.Char("Specification", size=128, )
    bill_quantity_id = fields.Many2one('bill.quantity',string="Bill Quantity")
    rfi = fields.Boolean(string="RFI")
    # currency_id_string = fields.Char(related="bill_quantity_id.currency_id.name", string="Currency")
    # by_finance = fields.Float(string="By Finance", digits=(1, 4), default=1)
    # lc_material_cost = fields.Float('Total', compute='_compute_lc_material')

    # @api.depends('by_finance', 'bill_quantity_id.material_cost')
    # def _compute_lc_material(self):
    #     for rec in self:
    #         if rec.key == 'lc':
    #             rec.lc_material_cost = rec.bill_quantity_id.material_cost * rec.by_finance
    #             rec._compute_price()

    # @api.depends('price_unit', 'qty', 'qty_manpower', 'shift', 'day', 'time', 'product_id', 'safety_factor', 'bill_quantity_id.currency_id')
    @api.depends('price_unit', 'qty', 'product_id')
    def _compute_price(self):
        for i in self:
            # if i.key in ('labor'):
            #     i.qty = i.qty_manpower * i.shift * i.day * i.time
            #     i.currency_id = i.work_package_id.currency_id.id if not i.currency_id else i.currency_id
            # elif i.key in ('material', 'equipment', 'overhead'):
            #     i.currency_id = i.company_id.currency_id.id if not i.currency_id else i.currency_id
            # else:
            #     i.currency_id = i.work_package_id.currency_id.id if not i.currency_id else i.currency_id
            i.price_subtotal = i.qty * i.price_unit # * (1 + i.safety_factor)
            i.bill_quantity_id._compute_amount()

    key = fields.Selection(_key_selection)
    # unit_id = fields.Many2one('work.unit', 'Unit')
    equipment_id = fields.Many2one('maintenance.equipment', string='Equipment', )
    # qty_manpower = fields.Integer("Manpower", default=1)
    # shift = fields.Integer("Shift", default=1)
    # day = fields.Integer("Day", default=1)
    # time = fields.Integer("Time", default=1)
    # safety_factor = fields.Float('Safety Factor')
    # harga_beli = fields.Float("Harga beli", digits='Account',default = 0.0, )
    name = fields.Text(string='Description')
    sequence = fields.Integer(string='Sequence', default=10)
    display_type = fields.Selection([
        ('line_section', "Section"),
        ('line_note', "Note")], default=False, help="Technical field for UX purpose.")
    boq_manpower_ids = fields.One2many('bill.quantity.line.manpower', 'boq_line_id', string='Struktur Cost')
    purchase_ids = fields.One2many("purchase.order.line", related="product_id.purchase_order_line_ids", string="Purchase order")
    selected_po = fields.Many2one('purchase.order.line', string="Selected Purchase")
    purchase_price = fields.Float(string="Purchase Price", related="selected_po.price_unit")
    margin = fields.Float('Margin (%)') #, compute='_compute_price')
    price_unit = fields.Float("Unit Price", digits='Account', default=0.0, )
    depre = fields.Float("Depre", digits='Account',default = 0.0, )
    biaya_per_bulan = fields.Float("Biaya per Bulan", digits='Account',default = 0.0, compute='_calc_biaya_per_bulan')
    line_ids = fields.One2many('bill.quantity.line.purchase', 'rfi_id', string="Line")

    @api.onchange('depre','price_subtotal')
    def _calc_biaya_per_bulan(self):
        for line in self:
            line.biaya_per_bulan = line.price_subtotal / line.depre if line.depre else 0

    @api.onchange('margin')
    def _onchange_margin(self):
        if self.rfi:
            self.price_unit = self.purchase_price * (1 + self.margin / 100)
        else:
            self.margin = 0

    def get_purchase_history(self):
        self.line_ids.unlink()
        lines = []
        for po in self.purchase_ids.filtered(lambda l: l.state in ('purchase','done')):
            lines.append((0, 0, {
                'partner_id': po.order_id.partner_id.id,
                'purchase_line_id': po.id,
                'purchase_id': po.order_id.id,
                'product_id': po.product_id.id,
                'product_qty': po.product_qty,
                'product_uom': po.product_uom.id,
                'price_unit': po.price_unit,
                'price_subtotal': po.price_subtotal,
            }))
            self.line_ids = [(6, 0, 0)] + lines

    @api.onchange("line_ids")
    def _onchange_purchase_ids(self):
        self.line_ids.write({'selected_po': False})
        self.line_ids.filtered(lambda p: p.purchase_line_id.id == self._origin.selected_po.id).selected_po = True

    @api.onchange("work_package_id")
    def _onchange_key(self):
        for rec in self:
            if rec.key in ("labor", "subcontract"):
                if rec.work_package_id:
                    # rec.price_unit = rec.work_package_id.work_package_cost;
                    rec.description = rec.work_package_id.name
                else:
                    rec.description = False

    @api.onchange("product_id")
    def _onchange_product_id(self):
        for rec in self:
            if rec.product_id:
                name = rec.product_id.name
                if rec.product_id.code:
                    name = "[{}] {}".format(name, rec.product_id.code)
                if rec.product_id.description_purchase:
                    name += "\n" + rec.product_id.description_purchase
                rec.description = name
                rec.name = name
                rec.uom_id = rec.product_id.uom_id.id
                rec.qty = 1
                rec.price_unit = rec.product_id.standard_price

    @api.onchange("equipment_id")
    def _onchange_equipment_id(self):
        for rec in self:
            if rec.key == "equipment":
                if rec.equipment_id:
                    rec.price_unit = rec.equipment_id.cost

    # def set_manpower_cost_structure(self):
    #     # search = self.env['bill.quantity.line.manpower'].sudo().search([('boq_line_id.id','=',self.id)]).ids
    #     return {
    #         'name': 'Struktur Cost %s' % self.work_package_id.name,
    #         'type': 'ir.actions.act_window',
    #         'view_mode': 'tree,form',
    #         "domain": "[('boq_line_id', '=', %s)]" % (self.id),
    #         'context': {'default_boq_line_id': self.id},
    #         'res_model': 'bill.quantity.line.manpower',
    #         "target": "current",
    #     }

    def reset_struktur_cost(self):
        for bill in self.env['bill.quantity.line.manpower'].sudo().search([('boq_line_id', '=', self.id)]):
            bill.unlink()
        for code in self.env['cost.code'].sudo().search([('cost_header_id', 'in',self.work_package_id.cost_header_ids.ids)]):
            res = {
                'boq_line_id' : self.id,
                'cost_code_id': code.id,
                'amount': code.price_unit,
            }
            manpower = self.env['bill.quantity.line.manpower'].sudo().create(res)

    def compute_struktur_cost(self):
        if self.id:
            line_manpower = self.env['bill.quantity.line.manpower'].sudo().search([('boq_line_id.id','=',self.id)])
            for line in line_manpower:
                localdict = {}
                amount = 0
                for code in self.env['cost.code'].sudo().search([('cost_header_id', 'in',self.work_package_id.cost_header_ids.ids)]):
                    for man in self.env['bill.quantity.line.manpower'].sudo().search([('cost_code_id.name','=',code.name)]):
                        localdict[str(man.cost_code_id.name)] = man.amount

                    if code.amount_select == 'code':
                        try:
                            safe_eval(code.amount_python_compute, localdict, mode="exec", nocopy=True)
                            price_unit = ('result' in localdict) and localdict['result'] or 0

                            manpower = self.env['bill.quantity.line.manpower'].sudo().search([('cost_code_id.id','=',code.id),('boq_line_id.id','=',self.id)])
                            manpower.sudo().write({'amount': price_unit})
                        except:
                            price_unit = code.price_unit
                    else:
                        price_unit = code.price_unit

                    manpower = self.env['bill.quantity.line.manpower'].sudo().search([('cost_code_id.id','=',code.id),('boq_line_id.id','=',self.id)])
                    for man in manpower:
                        if code.summed :
                            amount += man.amount

                self.write({'price_unit':amount})

        else:
            raise UserError(_('Work package is not found!'))

    def name_get(self):
        result = []
        for row in self:
            if row.bill_quantity_id :
                name = str(row.bill_quantity_id.name) +' - '+ str(row.product_id.name)
            else:
                name = row.product_id.name

            result.append((row.id, name))
        return result