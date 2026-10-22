"""Local-only QWeb entry page; never part of the deployable application."""

from odoo import http
from odoo.http import request


class LocalDevelopment(http.Controller):
    @http.route("/local-dev", type="http", auth="user")
    def launcher(self):
        if request.env.user.share or not request.env.user.has_group("gc_requirements.group_user"):
            return request.not_found()
        action = request.env.ref("gc_requirements.action_requirements")
        ticket_action = request.env.ref("helpdesk.local_tickets", raise_if_not_found=False)
        return request.render(
            "gc_local_dev.launcher",
            {"requirement_action": action.id, "ticket_action": ticket_action.id if ticket_action else False},
        )
