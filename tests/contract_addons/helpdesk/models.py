from odoo import fields, models


class HelpdeskTeam(models.Model):
    _name = "helpdesk.team"
    _description = "SYNTHETIC TEST TEAM"

    name = fields.Char(required=True)


class HelpdeskStage(models.Model):
    _name = "helpdesk.stage"
    _description = "SYNTHETIC TEST STAGE"

    name = fields.Char(required=True)
    fold = fields.Boolean()


class HelpdeskTicket(models.Model):
    _name = "helpdesk.ticket"
    _description = "SYNTHETIC TEST TICKET – NOT ENTERPRISE"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(required=True)
    description = fields.Html(sanitize=True)
    partner_id = fields.Many2one("res.partner")
    team_id = fields.Many2one("helpdesk.team")
    stage_id = fields.Many2one("helpdesk.stage")
    priority = fields.Selection([(str(i), str(i)) for i in range(4)], default="0")
    active = fields.Boolean(default=True)
