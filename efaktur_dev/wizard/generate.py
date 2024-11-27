from odoo import api, fields, models, _


class EfakturWizard(models.TransientModel):
    _name = 'efaktur.generate_efaktur'
    _description = 'eFaktur Wizard'
    
    start = fields.Char("Start")
    end = fields.Char("End")
    year = fields.Integer("Year")
    
    def confirm_button(self):
        start = self.start
        end = self.end
        
        #017-17-34018714
        a = start.split("-")
        b = end.split("-")
        
        for i in range(int(a[2]), int(b[2])+1):
            nomor = "%s-%s-%08d" % (a[0],a[1],i)
            data = {
                'year': self.year,
                'name': nomor,
            }
            self.env['efaktur.efaktur'].create(data)
        
        return
