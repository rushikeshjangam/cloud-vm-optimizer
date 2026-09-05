"""Read-only EC2 listing, disabled unless AWS_DEMO_ENABLED=true."""

from __future__ import annotations

import os
from dataclasses import dataclass

from cloud_vm_optimizer.aws.safety import REQUIRED_TAGS, has_required_tags


@dataclass(frozen=True)
class DemoInstance:
    instance_id: str
    instance_type: str
    state: str
    public_ip: str | None


class EC2DemoService:
    """Only inspects instances carrying every required project tag."""

    def __init__(self, enabled: bool, region: str) -> None:
        self.enabled = enabled
        self.region = region

    @classmethod
    def from_environment(cls) -> "EC2DemoService":
        enabled = os.getenv("AWS_DEMO_ENABLED", "false").strip().lower() == "true"
        region = os.getenv("AWS_REGION", "ap-south-1")
        return cls(enabled=enabled, region=region)

    def list_demo_instances(self) -> list[DemoInstance]:
        if not self.enabled:
            return []

        # Import lazily: local demos in safe mode never initialize an AWS client.
        import boto3

        ec2 = boto3.client("ec2", region_name=self.region)
        filters = [
            {"Name": f"tag:{key}", "Values": [value]}
            for key, value in REQUIRED_TAGS.items()
        ]
        response = ec2.describe_instances(Filters=filters)
        instances: list[DemoInstance] = []
        for reservation in response.get("Reservations", []):
            for instance in reservation.get("Instances", []):
                if not has_required_tags(instance.get("Tags")):
                    continue
                instances.append(
                    DemoInstance(
                        instance_id=instance["InstanceId"],
                        instance_type=instance.get("InstanceType", "unknown"),
                        state=instance.get("State", {}).get("Name", "unknown"),
                        public_ip=instance.get("PublicIpAddress"),
                    )
                )
        return instances

