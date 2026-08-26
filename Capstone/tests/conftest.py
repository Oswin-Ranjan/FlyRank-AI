import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.db.base import Base
from app.models import Plan, Tenant, Subscription, UsageEvent


TEST_DATABASE_URL = (
    "postgresql://postgres:postgres@localhost:5433/metering_billing"
)


@pytest.fixture
def db():
    engine = create_engine(TEST_DATABASE_URL)

    Base.metadata.create_all(bind=engine)

    SessionLocal = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
    )

    session = SessionLocal()

    # Clear data left by an interrupted test run before creating fresh fixtures.
    session.query(UsageEvent).delete()
    session.query(Subscription).delete()
    session.query(Tenant).delete()
    session.query(Plan).delete()
    session.commit()

    try:
        yield session
    finally:
        session.rollback()

        # Remove test data after every test.
        session.query(UsageEvent).delete()
        session.query(Subscription).delete()
        session.query(Tenant).delete()
        session.query(Plan).delete()

        session.commit()
        session.close()
        engine.dispose()


@pytest.fixture
def free_tenant(db: Session):
    plan = Plan(
        name="Test Free",
        api_call_limit=3,
        ai_token_limit=100,
    )

    tenant = Tenant(
        name="Test Tenant",
    )

    db.add(plan)
    db.add(tenant)
    db.flush()

    subscription = Subscription(
        tenant_id=tenant.id,
        plan_id=plan.id,
        status="active",
    )

    db.add(subscription)
    db.commit()

    return tenant