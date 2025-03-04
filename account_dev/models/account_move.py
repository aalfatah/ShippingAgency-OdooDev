from odoo import fields, models, api
from odoo.exceptions import ValidationError
import re

# from odoo.tools import (
#     date_utils,
#     email_re,
#     email_split,
#     float_compare,
#     float_is_zero,
#     float_repr,
#     format_amount,
#     format_date,
#     formatLang,
#     frozendict,
#     get_lang,
#     groupby,
#     is_html_empty,
#     sql
# )


class AccountMove(models.Model):
    _inherit = 'account.move'

    # _sequence_monthly_regex = r'$^(?P<prefix1>.*?)(?P<year>((?<=\D)|(?<=^))((19|20|21)\d{2}|(\d{2}(?=\D))))(?P<prefix2>\D*?)(?P<month>(0[1-9]|1[0-2]))(?P<prefix3>\D+?)(?P<seq>\d*)(?P<suffix>\D*?)'
    down_payment = fields.Boolean(string='Down Payment', tracking=True, default=False)

    @api.model_create_multi
    def create(self, vals_list):
        return super(AccountMove, self).create(vals_list)

    def write(self, vals):
        # inv_number = vals.get('name')
        # if inv_number != '/':
        #     for rec in self:
        #         vals['zip_from'], vals['zip_to'] = self._convert_zip_values(zip_from or rec.zip_from, zip_to or rec.zip_to)
        return super(AccountMove, self).write(vals)

    def action_post(self):
        self.ensure_one()
        if self.move_type == 'out_invoice' and self.name == '/':
            prefix = 'INVDP' if self.down_payment else 'INV'
            last_sequence = self._get_last_sequence(with_prefix=prefix)
            new = not last_sequence
            if new:
                self.name = self._get_starting_sequence_dev(prefix)
            else:
                self.name = self._get_sequence_next_number(prefix, last_sequence)
        res = super(AccountMove, self).action_post()
        return res

    def _get_sequence_next_number(self, prefix, last_sequence):
        sequence = int(re.findall(r'\d{4}', last_sequence)[0]) + 1
        sequence_format = self._get_starting_sequence_dev(prefix)
        sequence_format = sequence_format.replace("0001", "{:04d}".format(sequence))
        return sequence_format

    def _get_starting_sequence_dev(self, prefix):
        # EXTENDS account sequence.mixin
        self.ensure_one()
        customer_code = 'CCC' if not self.partner_id or not self.partner_id.ref else self.partner_id.ref
        month_romawi = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X', 'XI', 'XII'][self.date.month - 1]
        starting_sequence = "%s/0001/BSS-%s/%s-%s" % (prefix, customer_code, month_romawi, str(self.date.year)[2:])
        return starting_sequence

    # def _get_sequence_format_param(self, previous):
    #     if self.move_type == 'out_invoice':
    #         # sequence_number_reset = self._deduce_sequence_number_reset(previous)
    #         # regex = self._sequence_fixed_regex
    #         # if sequence_number_reset == 'year':
    #         #     regex = self._sequence_yearly_regex
    #         # elif sequence_number_reset == 'year_range':
    #         #     regex = self._sequence_year_range_regex
    #         # elif sequence_number_reset == 'month':
    #         #     regex = self._sequence_monthly_regex
    #         regex = r'^(?P<prefix1>.*?)(?P<seq>\d{0,9})(?P<suffix>\D*?)$'
    #         format_values = re.match(regex, previous).groupdict()
    #         format_values['seq_length'] = 4 # len(format_values['seq'])
    #         format_values['year_length'] = 2 # len(format_values.get('year') or '')
    #         format_values['year_end_length'] = '' # len(format_values.get('year_end') or '')
    #         if not format_values.get('seq') and 'prefix1' in format_values and 'suffix' in format_values:
    #             # if we don't have a seq, consider we only have a prefix and not a suffix
    #             format_values['prefix1'] = 'INV' # format_values['suffix']
    #             format_values['suffix'] = 'BSS-%s' % self.partner_id.ref
    #         for field in ('seq', 'year', 'month', 'year_end'):
    #             format_values[field] = int(format_values.get(field) or 0)
    #
    #         placeholders = re.findall(r'\b(prefix\d|seq|suffix\d?|year|year_end|month)\b', regex)
    #         format = ''.join(
    #             "{seq:0{seq_length}d}" if s == 'seq' else
    #             "{month:02d}" if s == 'month' else
    #             "{year:0{year_length}d}" if s == 'year' else
    #             "{year_end:0{year_end_length}d}" if s == 'year_end' else
    #             "{%s}" % s
    #             for s in placeholders
    #         )
    #         return format, format_values
    #     return super(AccountMove, self)._get_sequence_format_param(previous)

    def _get_sequence_date_range(self, reset):
        # if self.move_type == 'out_invoice':
        #     return super()._get_sequence_date_range('month')
        return super()._get_sequence_date_range(reset)

    def _get_last_sequence_domain(self, relaxed=False):
        self.ensure_one()
        if self.move_type == 'out_invoice':
            if not self.date or not self.journal_id:
                return "WHERE FALSE", {}
            where_string = "WHERE journal_id = %(journal_id)s AND name != '/'"
            param = {'journal_id': self.journal_id.id}
            is_payment = self.payment_id or self._context.get('is_payment')

            if not relaxed:
                domain = [('journal_id', '=', self.journal_id.id), ('id', '!=', self.id or self._origin.id), ('name', 'not in', ('/', '', False))]
                if self.journal_id.refund_sequence:
                    refund_types = ('out_refund', 'in_refund')
                    domain += [('move_type', 'in' if self.move_type in refund_types else 'not in', refund_types)]
                if self.journal_id.payment_sequence:
                    domain += [('payment_id', '!=' if is_payment else '=', False)]
                # reference_move_name = self.search(domain + [('date', '<=', self.date)], order='date desc', limit=1).name

                start_date = self.date.replace(day=1)
                reference_move_name = self.search(domain + [('date', '>=', start_date), ('date', '<=', self.date)],
                                                  order='date desc', limit=1).name
                if not reference_move_name:
                    # reference_move_name = self.search(domain, order='date asc', limit=1).name
                    customer_code = 'CCC' if not self.partner_id or not self.partner_id.ref else self.partner_id.ref
                    month_romawi = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X', 'XI', 'XII'][self.date.month - 1]
                    year = str(self.date.year)[2:]
                    reference_move_name = 'INV/0000/BSS-%s/%s-%s' if not self.down_payment else 'INVDP/0000/BSS-%s/%s-%s'
                    reference_move_name = reference_move_name % (customer_code, month_romawi, year)
                # sequence_number_reset = self._deduce_sequence_number_reset(reference_move_name)
                sequence_number_reset = 'month'
                # sequence_number_reset = 'year'
                date_start, date_end = self._get_sequence_date_range(sequence_number_reset)
                where_string += """ AND date BETWEEN %(date_start)s AND %(date_end)s"""
                param['date_start'] = date_start
                param['date_end'] = date_end
                # if sequence_number_reset in ('year', 'year_range'):
                # param['anti_regex'] = re.sub(r"\?P<\w+>", "?:", self._sequence_monthly_regex.split('(?P<seq>')[0]) + '$'
                # elif sequence_number_reset == 'never':
                #     param['anti_regex'] = re.sub(r"\?P<\w+>", "?:", self._sequence_yearly_regex.split('(?P<seq>')[0]) + '$'

                # if param.get('anti_regex') and not self.journal_id.sequence_override_regex:
                #     where_string += " AND sequence_prefix !~ %(anti_regex)s "

            if self.journal_id.refund_sequence:
                if self.move_type in ('out_refund', 'in_refund'):
                    where_string += " AND move_type IN ('out_refund', 'in_refund') "
                else:
                    where_string += " AND move_type NOT IN ('out_refund', 'in_refund') "
            elif self.journal_id.payment_sequence:
                if is_payment:
                    where_string += " AND payment_id IS NOT NULL "
                else:
                    where_string += " AND payment_id IS NULL "

            return where_string, param
        else:
            return super(AccountMove, self)._get_last_sequence_domain(relaxed)

    def _get_last_sequence(self, relaxed=False, with_prefix=None, lock=True):
        self.ensure_one()
        if self.move_type == 'out_invoice':
            if self._sequence_field not in self._fields or not self._fields[self._sequence_field].store:
                raise ValidationError(_('%s is not a stored field', self._sequence_field))
            where_string, param = self._get_last_sequence_domain(relaxed)
            if self._origin.id:
                where_string += " AND id != %(id)s "
                param['id'] = self._origin.id
            if with_prefix is not None:
                where_string += " AND sequence_prefix = %(with_prefix)s "
                param['with_prefix'] = with_prefix

            query = f"""
                    SELECT {{field}} FROM {self._table}
                    {where_string}
                    ORDER BY sequence_number DESC
                    LIMIT 1
            """
            if lock:
                query = f"""
                UPDATE {self._table} SET write_date = write_date WHERE id = (
                    {query.format(field='id')}
                )
                RETURNING {self._sequence_field};
                """
            else:
                query = query.format(field=self._sequence_field)

            self.flush_model([self._sequence_field, 'sequence_number', 'sequence_prefix'])
            self.env.cr.execute(query, param)
            return (self.env.cr.fetchone() or [None])[0]
        return super(AccountMove, self)._get_last_sequence(relaxed, with_prefix, lock)

    @api.depends(lambda self: [self._sequence_field])
    def _compute_split_sequence(self):
        if self.move_type == 'out_invoice':
            for record in self:
                sequence = record[record._sequence_field] or ''
                if sequence != "/" and re.findall(r'(INV/|INVDP/)(\d{4})', sequence):
                    prefix = 'INVDP' if self.down_payment else 'INV'
                    # regex = re.sub(r"\?P<\w+>", "?:", sequence.replace(prefix + "/", ""))  # make the seq the only matching group
                    # matching = re.match(regex, sequence)
                    sequence = sequence.replace(prefix + "/", "")
                    record.sequence_prefix = prefix # sequence[:matching.start(1)]
                    # record.sequence_number = int(matching.group(1) or 0)
                    record.sequence_number = int(sequence[:4])
                else:
                    record.sequence_prefix = False
                    record.sequence_number = False
        else:
            super(AccountMove, self)._compute_split_sequence()

    def _set_next_sequence(self):
        self.ensure_one()
        if self.move_type != 'out_invoice':
            super(AccountMove, self)._set_next_sequence()
