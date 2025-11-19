from odoo import models, fields
from odoo.exceptions import UserError

class StockRule(models.Model):
    _inherit = 'stock.rule'

    def _get_matching_supplier(self, product_id, product_qty, product_uom, company_id, values):

        # 1. Odoo default supplier
        supplier = super()._get_matching_supplier(
            product_id, product_qty, product_uom, company_id, values
        )

        # 2. Preferred vendor override
        PreferredVendor = self.env['preferred.vendor']

        domain = [('product_ids', 'in', product_id.id)]
        if values.get('partner_id'):
            domain.append(('customer_ids', 'in', values['partner_id']))

        preferred_vendor = PreferredVendor.search(domain, limit=1)

        if preferred_vendor and preferred_vendor.vendor_id:
            preferred_supplier = self.env['product.supplierinfo'].search([
                ('partner_id', '=', preferred_vendor.vendor_id.id),
                ('product_id', '=', product_id.id),
            ], limit=1)

            if preferred_supplier:
                return preferred_supplier

        # 3. Fallback to Odoo’s normal supplier
        return supplier
