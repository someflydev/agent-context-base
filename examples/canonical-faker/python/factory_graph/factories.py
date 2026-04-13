from __future__ import annotations

"""Declarative TenantCore factories.

Use factory_boy for smoke/small profiles. For medium/large profiles, use the
faker_pipeline or mimesis_pipeline directly.
"""

import importlib.util
import sys
from datetime import datetime, timedelta
from pathlib import Path

try:
    import factory
except ImportError:  # pragma: no cover - exercised by importability tests
    factory = None


def _load_domain_module():
    module_path = Path(__file__).resolve().parents[2] / "domain" / "generation_patterns.py"
    spec = importlib.util.spec_from_file_location(
        "canonical_faker_domain_generation_patterns", module_path
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load domain module from {module_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules.setdefault(spec.name, module)
    spec.loader.exec_module(module)
    return module


domain = _load_domain_module()


def _require_factory_boy() -> None:
    if factory is None:
        raise RuntimeError("factory_boy is required for the factory graph")


def use_seed(seed: int) -> None:
    _require_factory_boy()
    factory.random.reseed_random(seed)
    for locale in ("en_US", "en_GB", "de_DE", "fr_FR"):
        factory.Faker._get_faker(locale).seed_instance(seed)


if factory is not None:
    class _BaseFactory(factory.Factory):
        class Meta:
            model = dict
            abstract = True


    class OrganizationFactory(_BaseFactory):
        class Params:
            initial_member_count = 6
            enterprise_org = factory.Trait(
                plan="enterprise",
                initial_member_count=12,
            )

        id = factory.Sequence(lambda n: str(domain.uuid.UUID(int=n + 1, version=4)))
        name = factory.Faker("company")
        slug = factory.LazyAttribute(lambda obj: domain._slugify(obj["name"]))
        plan = factory.Iterator(["free", "pro", "enterprise"])
        region = factory.Iterator(["us-east", "us-west", "eu-west", "ap-southeast"])
        created_at = factory.LazyFunction(lambda: domain._iso(domain.BASE_TIME - timedelta(days=365)))
        owner_email = factory.Faker("company_email")
        sequence = factory.Sequence(int)


    class UserFactory(_BaseFactory):
        class Params:
            seed = None

        id = factory.Sequence(lambda n: str(domain.uuid.UUID(int=1000 + n, version=4)))
        email = factory.Sequence(lambda n: f"user_{n}@example.com")
        full_name = factory.Faker("name")
        locale = "en-US"
        timezone = "America/New_York"
        created_at = factory.LazyFunction(lambda: domain._iso(domain.BASE_TIME - timedelta(days=400)))
        sequence = factory.Sequence(int)


    class MembershipFactory(_BaseFactory):
        class Params:
            org = factory.SubFactory(OrganizationFactory)
            user = factory.SubFactory(UserFactory)

        id = factory.Sequence(lambda n: str(domain.uuid.UUID(int=2000 + n, version=4)))
        org_id = factory.LazyAttribute(lambda obj: obj.org["id"])
        user_id = factory.LazyAttribute(lambda obj: obj.user["id"])
        role = "member"
        joined_at = factory.LazyAttribute(
            lambda obj: domain._iso(
                datetime.fromisoformat(obj.org["created_at"].replace("Z", "+00:00"))
                + timedelta(days=7)
            )
        )
        invited_by = None
        user_email = factory.LazyAttribute(lambda obj: obj.user["email"])


    class ProjectFactory(_BaseFactory):
        class Params:
            org = factory.SubFactory(OrganizationFactory)
            creator = factory.SubFactory(UserFactory)

        id = factory.Sequence(lambda n: str(domain.uuid.UUID(int=3000 + n, version=4)))
        org_id = factory.LazyAttribute(lambda obj: obj.org["id"])
        name = factory.Sequence(lambda n: f"Project {n}")
        status = "active"
        created_by = factory.LazyAttribute(lambda obj: obj.creator["id"])
        created_at = factory.LazyAttribute(
            lambda obj: domain._iso(
                datetime.fromisoformat(obj.org["created_at"].replace("Z", "+00:00"))
                + timedelta(days=14)
            )
        )


    class ApiKeyFactory(_BaseFactory):
        class Params:
            org = factory.SubFactory(OrganizationFactory)
            creator = factory.SubFactory(UserFactory)

        id = factory.Sequence(lambda n: str(domain.uuid.UUID(int=4000 + n, version=4)))
        org_id = factory.LazyAttribute(lambda obj: obj.org["id"])
        created_by = factory.LazyAttribute(lambda obj: obj.creator["id"])
        name = factory.Faker("catch_phrase")
        key_prefix = factory.Sequence(lambda n: f"tc_{n:08x}"[:11])
        created_at = factory.LazyAttribute(
            lambda obj: domain._iso(
                datetime.fromisoformat(obj.org["created_at"].replace("Z", "+00:00"))
                + timedelta(days=21)
            )
        )
        last_used_at = factory.LazyAttribute(
            lambda obj: domain._iso(
                datetime.fromisoformat(obj.created_at.replace("Z", "+00:00"))
                + timedelta(days=1)
            )
        )


    class InvitationFactory(_BaseFactory):
        class Params:
            org = factory.SubFactory(OrganizationFactory)
            inviter = factory.SubFactory(UserFactory)

        id = factory.Sequence(lambda n: str(domain.uuid.UUID(int=5000 + n, version=4)))
        org_id = factory.LazyAttribute(lambda obj: obj.org["id"])
        invited_email = factory.Sequence(lambda n: f"invite_{n}@example.com")
        role = "member"
        invited_by = factory.LazyAttribute(lambda obj: obj.inviter["id"])
        expires_at = factory.LazyFunction(lambda: domain._iso(domain.BASE_TIME + timedelta(days=14)))
        accepted_at = None


    class AuditEventFactory(_BaseFactory):
        class Params:
            org = factory.SubFactory(OrganizationFactory)
            user = factory.SubFactory(UserFactory)
            project = factory.SubFactory(ProjectFactory)

        id = factory.Sequence(lambda n: str(domain.uuid.UUID(int=6000 + n, version=4)))
        org_id = factory.LazyAttribute(lambda obj: obj.org["id"])
        user_id = factory.LazyAttribute(lambda obj: obj.user["id"])
        project_id = factory.LazyAttribute(lambda obj: obj.project["id"])
        action = "updated"
        resource_type = "project"
        resource_id = factory.LazyAttribute(lambda obj: obj.project["id"])
        ts = factory.LazyAttribute(
            lambda obj: domain._iso(
                datetime.fromisoformat(obj.project["created_at"].replace("Z", "+00:00"))
                + timedelta(days=1)
            )
        )
else:
    class OrganizationFactory:  # pragma: no cover - dependency absent path
        pass


    class UserFactory:  # pragma: no cover - dependency absent path
        pass


    class MembershipFactory:  # pragma: no cover - dependency absent path
        pass


    class ProjectFactory:  # pragma: no cover - dependency absent path
        pass


    class ApiKeyFactory:  # pragma: no cover - dependency absent path
        pass


    class InvitationFactory:  # pragma: no cover - dependency absent path
        pass


    class AuditEventFactory:  # pragma: no cover - dependency absent path
        pass
