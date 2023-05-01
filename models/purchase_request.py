from odoo import fields, models, api, _


class PurchaseRequest(models.Model):
    _name = "purchase.request"


    name = fields.Char(string="Request name", required=True)
    user_id = fields.Many2one("res.users", required=1, default=lambda self: self.env.user)
    date_start = fields.Date(string="Start Date", default=fields.Date.today)
    date_end = fields.Date(string="End Date")
    reject_reason = fields.Text(string="Reject Reason")
    total_price = fields.Float(string="Total Price", required=True, compute="sum_total", )
    partner_id = fields.Many2one(comodel_name="res.partner", string="vender", required=False, )
    #field name to compute in purchase order
    num_orders = fields.Integer(string="Number of orders", required=False, compute='compute_order_count')
    order_id = fields.One2many(comodel_name="purchase.order", inverse_name="name_id", string="Order ID", required=False, )

    line_ids = fields.One2many("purchase.request.line", "purchase_request_id")
    state = fields.Selection([
        ("draft", "Draft"),
        ("to be approved", "To be Approved"),
        ("approve", "Approve"),
        ("reject", "Reject"),
        ("cancel", "Cancel"),
    ], default="draft")

    @api.depends('line_ids')
    def sum_total(self):
        for rec in self:
            total_price = 0.0
            for line in rec.line_ids:
                total_price += line.total
            rec.total_price = total_price

    def button_cancel(self):
        for rec in self:
            rec.state = "cancel"

    def button_submit_for_approval(self):
        for rec in self:
            rec.state = "to be approved"

    def Reset_to_draft(self):
        for rec in self:
            rec.state = "draft"

    def button_submit_for_approval_Approve(self):
        for rec in self:
            rec.state = "approve"

    def button_submit_for_approval_Reject(self):

        view_id = self.env.ref('purchase_request.wizard_form').id
        return {
            'name': _('Reject Purchase Request'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_type': 'form',
            'res_model': 'purchase.request.wizard',
            'views': [(view_id, 'form')],
            'target': 'new',
        }

    def action_confirm_rejection(self):
        # Set the rejection reason field and reject the purchase request
        self.reject_reason = self.env.context.get('rejection_reason')
        self.button_reject()

    def send_email_templete(self):
        self.env.ref('purchase_request.email_template_edi_credit_note').send_mail(self.id, email_values={
            "email_from": "yasser@yahoo.com",
            "email_to": "yasser@gmail.com",
        })

    def button_create_PO(self):
        orders_line = []
        for line in self.line_ids:
            orders_line.append((0, 0,
                                {'name': line.product_id.display_name,
                                 'product_qty': line.qty,
                                 'product_id': line.product_id.id,
                                 'price_unit': line.cost_price,
                                 }

                                ))

        purchase_order = self.env['purchase.order'].create(
            {
                'partner_id': self.partner_id.id,
                'order_line': orders_line,
                'name_id':self.id,
            }
        )

        return {
            'name': _('Create purchase.order'),
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.order',
            'view_type': 'form',
            'view_mode': 'form',
            'domain': [('name_id', '=', self.id)],
            'res_id': purchase_order.id,
            # 'context': {
            #     "default_partner_id": self.partner_id.id
            # }

        }

    def action_view_order(self):
      return

    # compute function

    # def  compute_order_count(self):
    #     _order_group= self.env['bridge.purchase'].read_group(fields=['name_id'],groupby=['name_id'])
    #     for

    @api.depends('name')
    def compute_order_count(self):
       for record in self:
        num_orders = self.env['purchase.order'].search_count([('name_id', '=', record.id)])
        record.num_orders = num_orders

class PurchaseRequestLine(models.Model):
    _name = "purchase.request.line"

    product_id = fields.Many2one("product.product", required=1)
    description = fields.Text(string="Description")
    qty = fields.Float(default=1)
    cost_price = fields.Float(string="Cost Price", readonly=1, related="product_id.standard_price")
    total = fields.Float(string="Total", readonly=1, compute="_get_price_total")
    purchase_request_id = fields.Many2one("purchase.request")

    @api.depends("cost_price", "qty")
    def _get_price_total(self):
        for rec in self:
            rec.total = rec.qty * rec.cost_price



#     < div
#
#    class ="oe_button_box" name="button_box" >
#
#     < button
#     type = "object"
#     name = "action_view_invoice"
#
#     class ="oe_stat_button" icon="fa-pencil-square-o" attrs="{'invisible':['|', ('invoice_count', '=', 0), ('state', 'in', ('draft','sent','to approve'))]}" >
#
#     < field
#     name = "invoice_count"
#     widget = "statinfo"
#     string = "Vendor Bills" / >
#     < field
#     name = "invoice_ids"
#     invisible = "1" / >
#
# < / button >
# < / div >
