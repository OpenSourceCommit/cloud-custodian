I am contributing to **Cloud Custodian** and my task is to **add support for AWS CloudWatch Synthetics (Canaries)**.

Currently, Cloud Custodian already supports CloudWatch features such as **event rules** and **alarms**, but there is no direct support for **CloudWatch Synthetics**. My goal is to extend Cloud Custodian to integrate this functionality. In inclusion to that role, i am also expected to include enhance:

1) Filtering all the tags on the CW synthetics/canaries. All CloudWatch synthetics/canaries resources must be tagged with a valid OwnerContact 
2) And always configure canaries to connect to endpoints using encrypted protocols like HTTPS (ports 443/8443) instead of HTTP (port 80).

### References / Resources

- **Contribution guidelines**:

  - https://cloudcustodian.io/docs/contribute.html
  - https://github.com/cloud-custodian/cloud-custodian/blob/main/README.md

- **Example PRs and commits**:

  - https://github.com/cloud-custodian/cloud-custodian/pull/10021/files#diff-6dd7596ceaa389fc83e3a2cab3822c83e313116cfc661714b510d163eef33627
  - https://github.com/cloud-custodian/cloud-custodian/pull/6353/files#diff-b96e9a04b1f67d436ad99511869d3391b68c7e97cddd434e7bf226742c3f3920
  - https://github.com/cloud-custodian/cloud-custodian/commit/2fdce5a8bf47940e110b4f3d857173c3835c0316#diff-225eb111d98bf46a9b616e423f701cae96b1dd2ffff860345bde68022e619305
  - https://github.com/cloud-custodian/cloud-custodian/commits/main/c7n/resources/cw.py

- **AWS CloudWatch Synthetics documentation**:

  - https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/CloudWatch_Synthetics_Canaries.html
  - https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/synthetics.html

### What i have done so far:
1. I have included my integration into the "cloud-custodian\c7n\resources\cw.py" as follow:
# ========================================================================
# CloudWatch Synthetics Canaries
# ========================================================================

@resources.register('cw-synthetics-canary')
class SyntheticsCanary(QueryResourceManager):
    """AWS CloudWatch Synthetics Canary

    Example:
        .. code-block:: yaml

            policies:
              - name: stop-failed-canaries
                resource: aws.cw-synthetics-canary
                filters:
                  - State.CurrentStatus.State: FAILED
                actions:
                  - type: delete
    """

    class resource_type(TypeInfo):
        service = 'synthetics'
        enum_spec = ('describe_canaries', 'Canaries', None)
        id = 'Id'
        name = 'Name'
        date = 'LastModified'
        arn_type = 'canary'
        dimension = 'CanaryName'
        cfn_type = 'AWS::Synthetics::Canary'
        universal_taggable = True

    permissions = ("synthetics:DescribeCanaries",)



@SyntheticsCanary.action_registry.register('delete')
class DeleteCanary(BaseAction):
    """Delete a CloudWatch Synthetics Canary

    Example:
        .. code-block:: yaml

            policies:
              - name: delete-stopped-canaries
                resource: aws.cw-synthetics-canary
                filters:
                  - State.CurrentStatus.State: STOPPED
                actions:
                  - delete
    """

    schema = type_schema('delete')
    permissions = ("synthetics:DeleteCanary",)

    def process(self, resources):
        client = local_session(self.manager.session_factory).client('synthetics')
        for r in resources:
            try:
                client.delete_canary(Name=r['Name'])
            except client.exceptions.ResourceNotFoundException:
                continue


@SyntheticsCanary.action_registry.register('stop')
class StopCanary(BaseAction):
    """Stop a running CloudWatch Synthetics Canary

    Example:
        .. code-block:: yaml

            policies:
              - name: stop-running-canaries
                resource: aws.cw-synthetics-canary
                filters:
                  - State.CurrentStatus.State: RUNNING
                actions:
                  - stop
    """

    schema = type_schema('stop')
    permissions = ("synthetics:StopCanary",)

    def process(self, resources):
        client = local_session(self.manager.session_factory).client('synthetics')
        for r in resources:
            try:
                client.stop_canary(Name=r['Name'])
            except client.exceptions.ResourceNotFoundException:
                continue


@SyntheticsCanary.action_registry.register('start')
class StartCanary(BaseAction):
    """Start a CloudWatch Synthetics Canary

    Example:
        .. code-block:: yaml

            policies:
              - name: start-canaries
                resource: aws.cw-synthetics-canary
                filters:
                  - State.CurrentStatus.State: STOPPED
                actions:
                  - start
    """

    schema = type_schema('start')
    permissions = ("synthetics:StartCanary",)

    def process(self, resources):
        client = local_session(self.manager.session_factory).client('synthetics')
        for r in resources:
            try:
                client.start_canary(Name=r['Name'])
            except client.exceptions.ResourceNotFoundException:
                continue


@SyntheticsCanary.filter_registry.register('value')
class CanaryValueFilter(ValueFilter):
    """Filter canaries based on any field value (Name, State, Runtime, etc.)"""

    schema = type_schema('value', rinherit=ValueFilter.schema)
    permissions = ('synthetics:DescribeCanaries',)


@SyntheticsCanary.filter_registry.register('name')
class CanaryNameFilter(ValueFilter):
    """Filter canaries by their Name"""

    schema = type_schema('name', rinherit=ValueFilter.schema)
    permissions = ('synthetics:DescribeCanaries',)

    def __call__(self, r):
        return self.match(r.get('Name'))


@SyntheticsCanary.filter_registry.register('arn')
class CanaryArnFilter(ValueFilter):
    """Filter canaries by their ARN"""

    schema = type_schema('arn', rinherit=ValueFilter.schema)
    permissions = ('synthetics:DescribeCanaries',)

    def __call__(self, r):
        return self.match(r.get('Arn'))


@SyntheticsCanary.filter_registry.register('state')
class CanaryStateFilter(ValueFilter):
    """Filter canaries by their current state"""

    schema = type_schema('state', rinherit=ValueFilter.schema)
    permissions = ('synthetics:DescribeCanaries',)

    def __call__(self, r):
        return self.match(r.get('Status', {}).get('State'))


@SyntheticsCanary.filter_registry.register('runtime-version')
class CanaryRuntimeVersionFilter(ValueFilter):
    """Filter canaries by Runtime Version"""

    schema = type_schema('runtime-version', rinherit=ValueFilter.schema)
    permissions = ('synthetics:DescribeCanaries',)

    def __call__(self, r):
        return self.match(r.get('RuntimeVersion'))


@SyntheticsCanary.filter_registry.register('last-run')
class CanaryLastRunFilter(ValueFilter):
    """Filter canaries by Last Run status/state/result"""

    schema = type_schema('last-run', rinherit=ValueFilter.schema)
    permissions = ('synthetics:DescribeCanaries',)

    def __call__(self, r):
        return self.match(r.get('LastRun', {}))


# -------------------------
# Tagging Filters / Actions
# -------------------------

SyntheticsCanary.filter_registry.register('marked-for-op', MarkForOp)
SyntheticsCanary.action_registry.register('tag', Tag)
SyntheticsCanary.action_registry.register('remove-tag', RemoveTag)
SyntheticsCanary.action_registry.register('mark-for-op', TagDelayedAction)

2. I have also added this test in the "cloud-custodian\tests\test_cw_synthetics.py":

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

### What I Need from You
I want you to review my requirements, compare it with the previous contributors implementation on cloud custodian, tell me what i have done right to attain my goal, what i did wrong and what i have left to do to ensure my objective is attained perfectly.