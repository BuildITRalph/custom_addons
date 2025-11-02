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
        help="Products this vendor is preferred for."
    )

    vendor_id = fields.Many2one(
        'res.partner',
        string='Preferred Vendor',
        required=True,
        domain=[('supplier_rank', '>', 0)],
        help="The vendor to be used instead of supplierinfo for these products/customers."
    )

    active = fields.Boolean(default=True)
    note = fields.Char(string='Notes')

    _sql_constraints = [
        ('vendor_unique_constraint',
         'unique(vendor_id)',
         'Each vendor should have only one preferred vendor record.')
    ]

    @api.depends('customer_ids', 'product_ids')
    def _compute_name(self):
        for record in self:
            customer_names = ', '.join(record.customer_ids.mapped('name'))
            product_names = ', '.join(record.product_ids.mapped('name'))
            if customer_names and product_names:
                record.name = f"{customer_names} → {product_names}"
            elif customer_names:
                record.name = f"{customer_names} → (No Product)"
            elif product_names:
                record.name = f"(No Customer) → {product_names}"
            else:
                record.name = "(Unspecified)"