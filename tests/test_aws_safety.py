from cloud_vm_optimizer.aws.ec2_service import EC2DemoService
from cloud_vm_optimizer.aws.safety import REQUIRED_TAGS, has_required_tags


def test_aws_demo_is_disabled_by_default(monkeypatch) -> None:
    monkeypatch.delenv("AWS_DEMO_ENABLED", raising=False)
    service = EC2DemoService.from_environment()
    assert not service.enabled
    assert service.list_demo_instances() == []


def test_every_required_tag_must_match() -> None:
    tags = [{"Key": key, "Value": value} for key, value in REQUIRED_TAGS.items()]
    assert has_required_tags(tags)
    assert not has_required_tags(tags[:-1])

