from odoo import models, fields, _


class Purchase_wizard(models.TransientModel):
    _name = 'wizard.info'
    _description = 'Purchase wizard'

    name = fields.Char(string="name", required=False, )
    rejection_reason = fields.Char(string="Rejection reason", required=True, )

    def action_confirm(self):
        # Get the active purchase request
        request = self.env['purchase.request'].browse(self.env.context.get('active_id'))
        for rec in self:
            print("request", request)
            print("request", request.reject_reason)
            print("rec.rejection_reason", rec.rejection_reason)
            request.reject_reason = rec.rejection_reason
            request.state = "reject"
        # Set the rejection reason and reject the purchase request
        # request.write({'rejection_reason': self.rejection_reason, 'state': 'reject'})
        # request.button_reject()
        return {'type': 'ir.actions.act_window_close'}
