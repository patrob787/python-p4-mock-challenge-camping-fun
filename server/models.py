from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

convention = {
  "ix": "ix_%(column_0_label)s",
  "uq": "uq_%(table_name)s_%(column_0_name)s",
  "ck": "ck_%(table_name)s_%(constraint_name)s",
  "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
  "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)

db = SQLAlchemy(metadata=metadata)

class Activity(db.Model, SerializerMixin):
    __tablename__ = 'activities'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    difficulty = db.Column(db.Integer)

    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    signups = db.relationship("Signup", backref="activity")

    # deletes signups using "cascade" instead
    # signups = db.relationship("Signup", cascade="all,delete", backref="activity")

    serialize_rules = ("-signups.activity",)
    serialize_only = ("id", "name", "difficulty")

    def __repr__(self):
        return f'<Activity {self.id}: {self.name}>'

class Camper(db.Model, SerializerMixin):
    __tablename__ = 'campers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    age = db.Column(db.Integer)

    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    signups = db.relationship("Signup", backref="camper")

    # will grab ONLY activity from signups and assign it to an "activities" property
    # activities = association_proxy("signups", "activity")

    serialize_rules = ("-signups.camper",)
    serialize_only = ("id", "name", "age")

    @validates('name')
    def validates_name(self, key, name):
        if name == None or len(name) < 1:
            raise ValueError("Camper Name must exist!")
        return name
    
    @validates('age')
    def validates_age(self, key, age):
        if age < 8 or age > 18:
            raise ValueError("Age must be between 8 and 18")
        return age
            

    def __repr__(self):
        return f'<Camper {self.id}: {self.name}>'
    
class Signup(db.Model, SerializerMixin):
    __tablename__ = 'signups'

    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.Integer, nullable=False)

    camper_id = db.Column(db.Integer, db.ForeignKey('campers.id'))
    activity_id = db.Column(db.Integer, db.ForeignKey('activities.id'))

    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    serialize_rules = ("-camper.signups", "-activity.signups")

    @validates('time')
    def validates_time(self, key, time):
        if time < 0 or time > 23:
            raise ValueError("Signup time must be between 0 and 23 hrs")
        return time

    def __repr__(self):
        return f'<Signup {self.id}>'


# add any models you may need. 