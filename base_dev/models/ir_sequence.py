from datetime import datetime, timedelta
import logging
import pytz
from psycopg2 import sql, OperationalError, errorcodes

from odoo import api, fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

FORMATROMAN = (
    ('M',  1000),
    ('CM', 900),
    ('D',  500),
    ('CD', 400),
    ('C',  100),
    ('XC', 90),
    ('L',  50),
    ('XL', 40),
    ('X',  10),
    ('IX', 9),
    ('V',  5),
    ('IV', 4),
    ('I',  1)
)


class IrSequence(models.Model):
    _inherit = "ir.sequence"

    def _get_prefix_suffix(self, date=None, date_range=None):

        def _convert_to_roman(n):
            result = ""
            for numeral, integer in FORMATROMAN:
                while n >= integer:
                    result += numeral
                    n -= integer
            return result

        def _interpolate(s, d):
            return (s % d) if s else ''

        def _interpolation_dict():
            now = range_date = effective_date = datetime.now(pytz.timezone(self._context.get('tz') or 'UTC'))
            if date or self._context.get('ir_sequence_date'):
                effective_date = fields.Datetime.from_string(date or self._context.get('ir_sequence_date'))
            if date_range or self._context.get('ir_sequence_date_range'):
                range_date = fields.Datetime.from_string(date_range or self._context.get('ir_sequence_date_range'))

            sequences = {
                'rom_year': 'year', 'rom_month': 'month', 'rom_day': 'day', 'year': '%Y', 'month': '%m', 'day': '%d', 'y': '%y', 'doy': '%j', 'woy': '%W',
                'weekday': '%w', 'h24': '%H', 'h12': '%I', 'min': '%M', 'sec': '%S'
            }
            res = {}
            for key, format in sequences.items():
                res[key] = _convert_to_roman(getattr(effective_date,format)) if 'rom' in key else effective_date.strftime(format)
                res['range_' + key] = _convert_to_roman(getattr(range_date,format)) if 'rom' in key else range_date.strftime(format)
                res['current_' + key] = _convert_to_roman(getattr(now,format)) if 'rom' in key else now.strftime(format)

            return res

        self.ensure_one()
        d = _interpolation_dict()

        try:
            interpolated_prefix = _interpolate(self.prefix, d)
            interpolated_suffix = _interpolate(self.suffix, d)
        except ValueError:
            raise UserError(_('Invalid prefix or suffix for sequence \'%s\'') % self.name)
        return interpolated_prefix, interpolated_suffix
