import logging

from odoo import fields
from odoo.tests import tagged

from .common import HelpdeskCase

_logger = logging.getLogger(__name__)


@tagged("post_install", "-at_install")
class TestAggregatePerformance(HelpdeskCase):
    def test_thousand_requirements_counts_are_batched(self):
        requirements = self.Requirement.with_context(
            tracking_disable=True, mail_create_nosubscribe=True
        ).create([self.values(name="Synthetic bulk %s" % index) for index in range(1000)])
        # Distinct tickets avoid masking a per-ticket N+1 behind repeated IDs.
        tickets = (
            self.env["helpdesk.ticket"]
            .sudo()
            .with_context(tracking_disable=True, mail_create_nosubscribe=True)
            .create(
                [
                    {
                        "name": "Synthetic bulk ticket %s" % index,
                        "team_id": self.team.id,
                        "partner_id": self.contact_a.id if index % 2 else self.contact_b.id,
                        "description": "<p>Synthetic bulk ticket</p>",
                    }
                    for index in range(2000)
                ]
            )
        )
        self.env["gc.requirement.ticket.source"].sudo().create(
            [
                {
                    "requirement_id": req.id,
                    "ticket_id": ticket.id,
                    "description_snapshot": "<p>Synthetic performance fixture</p>",
                    "captured_at": fields.Datetime.now(),
                    "captured_by_id": self.support.id,
                }
                for index, req in enumerate(requirements)
                for ticket in tickets[2 * index : 2 * index + 2]
            ]
        )
        self.env.flush_all()
        self.env.invalidate_all()
        start = self.cr.sql_log_count
        counts = requirements.read(["ticket_count", "customer_count"])
        queries = self.cr.sql_log_count - start
        self.assertEqual(len(counts), 1000)
        self.assertTrue(all(row["ticket_count"] == 2 and row["customer_count"] == 1 for row in counts))
        self.assertLess(queries, 50, "Aggregate reading must not query once per requirement.")
        _logger.info(
            "PERFORMANCE: 1000 requirements / 2000 distinct tickets and sources, aggregate read: %s SQL queries",
            queries,
        )
