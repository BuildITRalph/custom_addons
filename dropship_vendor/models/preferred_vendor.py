from odoo import api, fields, models
from odoo.exceptions import ValidationError

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
        # domain=[('customer_rank', '>', 0)],
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
            existing = self.search([('id', '!=', record.id)])
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
        domain = [('id', 'not in', used_vendor_ids)]
        return domain

    @api.constrains('customer_ids', 'product_ids')
    def _check_unique_customer_product_pairs(self):
        for record in self:
            if not record.customer_ids or not record.product_ids:
                continue

            # Get all other records
            other_records = self.search([('id', '!=', record.id)])

            # Build all (customer_id, product_id) pairs in this record
            record_pairs = {(c.id, p.id) for c in record.customer_ids for p in record.product_ids}

            for other in other_records:
                other_pairs = {(c.id, p.id) for c in other.customer_ids for p in other.product_ids}

                # Detect intersection of pairs
                conflict_pairs = record_pairs & other_pairs
                if conflict_pairs:
                    # Build readable names for error message
                    customer_names = []
                    product_names = []
                    for cust_id, prod_id in conflict_pairs:
                        customer = self.env['res.partner'].browse(cust_id)
                        product = self.env['product.product'].browse(prod_id)
                        customer_names.append(customer.display_name)
                        product_names.append(product.display_name)

                    raise ValidationError(
                        "Conflict detected!\n\n"
                        "The following customer-product combinations already exist in another record:\n"
                        f"Customers: {', '.join(set(customer_names))}\n"
                        f"Products: {', '.join(set(product_names))}"
                    )
