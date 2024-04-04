import factory
from faker import Faker
from app.models import Event
from app.services import db

fake = Faker()


class EventFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Event
        sqlalchemy_session = db.get_db()  # Use your SQLAlchemy session here
        sqlalchemy_session_persistence = "commit"

    title = factory.LazyFunction(lambda: fake.sentence(nb_words=6))
    description = factory.LazyFunction(lambda: fake.text())
    start_date = factory.LazyFunction(lambda: fake.date_time())
    end_date = factory.LazyFunction(lambda: fake.date_time_between(start_date="+1d", end_date="+30d"))
