from .common import BaseTest


class SyntheticsCanaryTest(BaseTest):

    def test_delete_canary(self):
        factory = self.replay_flight_data("test_cw_synthetics_delete")
        client = factory().client("synthetics")

        canary_name = "c7n-test-canary-delete"

        p = self.load_policy(
            {
                "name": "delete-canary",
                "resource": "cw-synthetics-canary",
                "filters": [{"Name": canary_name}],
                "actions": ["delete"],
            },
            session_factory=factory,
        )

        resources = p.run()
        self.assertEqual(len(resources), 1)

        canaries = client.describe_canaries()["Canaries"]
        self.assertFalse(any(c["Name"] == canary_name for c in canaries))

    def test_stop_canary(self):
        factory = self.replay_flight_data("test_cw_synthetics_stop")
        client = factory().client("synthetics")

        canary_name = "c7n-test-canary-stop"

        p = self.load_policy(
            {
                "name": "stop-canary",
                "resource": "cw-synthetics-canary",
                "filters": [{"Name": canary_name}],
                "actions": ["stop"],
            },
            session_factory=factory,
        )

        resources = p.run()
        self.assertEqual(len(resources), 1)
        desc = client.get_canary(Name=canary_name)
        self.assertEqual(desc["Canary"]["Status"]["State"], "STOPPED")

    def test_start_canary(self):
        factory = self.replay_flight_data("test_cw_synthetics_start")
        client = factory().client("synthetics")

        canary_name = "c7n-test-canary-start"

        p = self.load_policy(
            {
                "name": "start-canary",
                "resource": "cw-synthetics-canary",
                "filters": [{"Name": canary_name}],
                "actions": ["start"],
            },
            session_factory=factory,
        )

        resources = p.run()
        self.assertEqual(len(resources), 1)
        desc = client.get_canary(Name=canary_name)
        self.assertEqual(desc["Canary"]["Status"]["State"], "RUNNING")

    def test_canary_tag_filter(self):
        factory = self.replay_flight_data("test_cw_synthetics_tag_filter")
        client = factory().client("synthetics")

        canary_name = "c7n-test-canary-tag"

        p = self.load_policy(
            {
                "name": "filter-canary-tags",
                "resource": "cw-synthetics-canary",
                "filters": [
                    {"type": "value", "key": "tag:Owner", "value": "DevOps"}
                ],
            },
            session_factory=factory,
        )

        resources = p.run()
        self.assertEqual(len(resources), 1)
        self.assertEqual(resources[0].get("c7n:MatchedFilters"), ["tag:Owner"])

        def test_owner_contact_filter(self):
        factory = self.replay_flight_data("test_cw_synthetics_owner_contact")
        client = factory().client("synthetics")

        canary_name = "c7n-test-canary-ownercontact"

        p = self.load_policy(
            {
                "name": "enforce-ownercontact",
                "resource": "cw-synthetics-canary",
                "filters": [{"type": "owner-contact"}],
            },
            session_factory=factory,
        )

        resources = p.run()
        self.assertEqual(len(resources), 1)
        self.assertEqual(resources[0]["Name"], canary_name)

    def test_https_only_filter(self):
        factory = self.replay_flight_data("test_cw_synthetics_https_only")
        client = factory().client("synthetics")

        canary_name = "c7n-test-canary-http"

        p = self.load_policy(
            {
                "name": "enforce-https-canaries",
                "resource": "cw-synthetics-canary",
                "filters": [{"type": "https-only"}],
            },
            session_factory=factory,
        )

        resources = p.run()
        self.assertEqual(len(resources), 1)
        self.assertEqual(resources[0]["Name"], canary_name)
