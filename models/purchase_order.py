from odoo import fields, models, api, _
class PurchaseOrder(models.Model):

    _inherit = 'purchase.order'

    name_id = fields.Many2one(comodel_name="purchase.request", string="Descreption", required=False, )
    # num_orders = fields.Integer(string="Number of orders", required=False,compute='compute_order_count' )


