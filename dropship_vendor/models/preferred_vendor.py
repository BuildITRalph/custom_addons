from odoo import api, fields, models

class PreferredVendor(models.Model):
    _name = 'preferred.vendor'
    _description = 'Preferred Vendor Mapping'

    name = fields.Char(
        string="Name",
        compute="_compute_name",
        store=True
    )

    customer_ids = fields.Many2many(
        'res.partner',
        'preferred_vendor_customer_rel',  # custom relation table name
        'preferred_vendor_id',            # this model column
        'customer_id',                    # res.partner column
        string='Customers',
        domain=[('customer_rank', '>', 0)],
        help="Customers this preferred vendor applies to."
    )

    product_ids = fields.Many2many(
        'product.product',
        'preferred_vendor_product_rel',   # custom relation table name
        'preferred_vendor_id',            # this model column
        'product_id',                     # product column
        string='Products',
        help="Products this vendor is preferred for (only dropship-enabled products)."
    )

    vendor_id = fields.Many2one(
        'res.partner',
        string='Preferred Vendor',
        required=True,
        domain=lambda self: self._get_unused_vendor_domain(),
        help="The vendor to be used instead of supplierinfo for these products/customers."
    )


    active = fields.Boolean(default=True)
    note = fields.Char(string='Notes')

    @api.constrains('vendor_id')
    def _check_unique_vendor(self):
        for record in self:
            # Check if any other record has the same vendor
            existing = self.search([('vendor_id', '=', record.vendor_id.id), ('id', '!=', record.id)])
            if existing:
                raise ValidationError('Each vendor should have only one preferred vendor record.')

    # ✅ Dynamically limit products to those with the Dropship route
    @api.model
    def fields_get(self, allfields=None, attributes=None):
        """Add a domain to product_ids: only products with dropship route."""
        res = super().fields_get(allfields, attributes)
        if 'product_ids' in res:
            try:
                dropship_route = self.env.ref('stock_dropshipping.route_drop_shipping')
                res['product_ids']['domain'] = [('route_ids', 'in', [dropship_route.id])]
            except Exception:
                # skip if the stock_dropshipping module isn't installed
                pass
        return res
    
    def _get_unused_vendor_domain(self):
        """Return a domain for vendor_id showing only unused vendors,
        but include the vendor already assigned to this record (if any)."""
        used_vendor_ids = self.search([('id', '!=', self.id)]).mapped('vendor_id').ids
        domain = [('supplier_rank', '>', 0), ('id', 'not in', used_vendor_ids)]
        return domain

