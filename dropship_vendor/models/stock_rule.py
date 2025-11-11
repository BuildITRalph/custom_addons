from odoo import models, fields
from odoo.exceptions import UserError

class StockRule(models.Model):
    _inherit = 'stock.rule'

    def _get_matching_supplier(self, product_id, product_qty, product_uom, company_id, values):
        supplier = False

        # Get the schedule date
        if 'date_planned' in values:
            date = max(fields.Datetime.from_string(values['date_planned']).date(), fields.Date.today())
        else:
            date = None

        # Use supplierinfo_id if present
        if values.get('supplierinfo_id'):
            supplier = values['supplierinfo_id']
        elif values.get('orderpoint_id') and values['orderpoint_id'].supplier_id:
            supplier = values['orderpoint_id'].supplier_id
        else:
            # Get the partner from preferred_supplier_id if passed
            partner_id = self.env['res.partner'].browse(values.get('preferred_supplier_id')) if values.get('preferred_supplier_id') else None

            supplier = product_id.with_company(company_id.id)._select_seller(
                partner_id=partner_id,
                quantity=product_qty,
                date=date,
                uom_id=product_uom,
                params={'force_uom': values.get('force_uom')},
            )

        # Fallback
        supplier = supplier or product_id._prepare_sellers(False).filtered(
            lambda s: not s.company_id or s.company_id == company_id
        )[:1]

        PreferredVendor = self.env['preferred.vendor']
        domain = [('product_ids', 'in', product_id)]
        if values['partner_id']:
            domain.append(('customer_ids', 'in', values['partner_id']))
        preferred_vendor = PreferredVendor.search(domain, limit=1)

        if preferred_vendor and preferred_vendor.vendor_id:
            # ensure this vendor has a supplierinfo for the product
            preferred_supplier = self.env['product.supplierinfo'].search([
                ('partner_id', '=', preferred_vendor.vendor_id.id),
                ('product_id', '=', product_id),
            ], limit=1)
            return preferred_supplier

        # raise UserError(supplier.partner_id.name)
        return supplier
