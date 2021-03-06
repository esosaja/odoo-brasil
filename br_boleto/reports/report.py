# -*- coding: utf-8 -*-
##############################################################################
#
#    Account Payment Boleto module for Odoo
#    Copyright (C) 2012-2015 KMEE (http://www.kmee.com.br)
#    @author Luis Felipe Miléo <mileo@kmee.com.br>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from __future__ import with_statement

import odoo
from odoo.exceptions import UserError
from odoo.report.render import render
from odoo.report.interface import report_int
from ..boleto.document import Boleto


class external_pdf(render):
    def __init__(self, pdf):
        render.__init__(self)
        self.pdf = pdf
        self.output_type = 'pdf'

    def _render(self):
        return self.pdf


class ReportCustom(report_int):
    """
        Custom report for return boletos
    """

    def create(self, cr, uid, ids, datas, context=False):
        env = odoo.api.Environment(cr, uid, context or {})

        active_ids = context.get('active_ids')
        active_model = context.get('origin_model')

        ids_move_lines = []
        aml_obj = env['account.move.line']
        if active_model == 'account.invoice':
            ai_obj = env['account.invoice']
            for account_invoice in ai_obj.browse(active_ids):
                for move_line in account_invoice.receivable_move_line_ids:
                    ids_move_lines.append(move_line.id)
        elif active_model == 'account.move.line':
            ids_move_lines = active_ids
        else:
            raise UserError(u'Parâmetros inválidos')
        boleto_list = aml_obj.browse(ids_move_lines).action_register_boleto()
        if not boleto_list:
            raise UserError(
                """Error
Não é possível gerar os boletos
Certifique-se que a fatura esteja confirmada e o
forma de pagamento seja duplicatas""")
        pdf_string = Boleto.get_pdfs(boleto_list)
        self.obj = external_pdf(pdf_string)
        self.obj.render()
        return self.obj.pdf, 'pdf'


ReportCustom('report.br_boleto.report.print')
