# -*- coding: utf-8 -*-
# © 2010-2012  Renato Lima - Akretion
# © 2016 Danimar Ribeiro, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from openerp import models, api
from openerp.tools.translate import _
from openerp.exceptions import Warning


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.onchange("zip")
    def _onchange_field(self):
        if self.type != 'contact':
            self.zip_search()

    @api.multi
    def zip_search(self):
        self.ensure_one()
        obj_zip = self.env['br.zip']

        zip_ids = obj_zip.zip_search_multi(
            country_id=self.country_id.id,
            state_id=self.state_id.id,
            city_id=self.city_id.id,
            district=self.district,
            street=self.street,
            zip_code=self.zip,
        )

        if len(zip_ids) == 1:
            result = obj_zip.set_result(zip_ids[0])
            self.update(result)
            return True
        else:
            if len(zip_ids) > 1:
                obj_zip_result = self.env['br.zip.result']
                zip_ids = obj_zip_result.map_to_zip_result(
                    zip_ids, self._name, self.id)

                return obj_zip.create_wizard(
                    self._name,
                    self.id,
                    country_id=self.country_id.id,
                    state_id=self.state_id.id,
                    city_id=self.city_id.id,
                    district=self.district,
                    street=self.street,
                    zip_code=self.zip,
                    zip_ids=[zip.id for zip in zip_ids]
                )
            else:
                raise Warning(_('Nenhum registro encontrado'))
