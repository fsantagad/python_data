from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

db = SQLAlchemy()

class Person(db.Model):
  """
  Person Model
  """
  __tablename__ = "persons"
  id = db.Column(db.Integer, primary_key=True)
  first_name = db.Column(db.String(45))
  last_name = db.Column(db.String(45))
  email = db.Column(db.String(255))
  gender = db.Column(db.String(45))
  ip_address = db.Column(db.String(16))
  country = db.relationship('Country', uselist=False, backref=db.backref('persons', uselist=False))
  
  def __init__(self, id, first_name, last_name, email, gender, ip_address, country=None):
    self.id = id
    self.first_name = first_name
    self.last_name = last_name
    self.email = email
    self.gender = gender
    self.ip_address = ip_address
    self.country = country

  def __repr__(self):
    return '<Person %r>' % self.id
  

class Country(db.Model):
    __tablename__ = "countries"
    id = db.Column(db.Integer, primary_key=True)
    country = db.Column(db.String(4))
    person_id = db.Column(db.Integer, db.ForeignKey('persons.id'))

    def __repr__(self):
        return f'<Country %r>' % self.id

ma = Marshmallow()
class CountrySchema(ma.Schema):
  """
  Schema
  """
  class Meta:
        fields = (
        'id', 
        'person_id', 
        'country'
        )

class PersonSchema(ma.Schema):
  """
  Schema
  """
  class Meta:
        fields = (
        'id', 
        'first_name', 
        'last_name', 
        'email', 
        'gender',
        'ip_address',
        'country'
        )
  
  country = ma.Nested(CountrySchema)

class PersonsPerCountrySchema(ma.Schema):
  """
  Schema
  """
  class Meta:
        fields = (
        'country', 
        'persons'
        )

class PersonsPerGenderSchema(ma.Schema):
  """
  Schema
  """
  class Meta:
        fields = (
        'gender', 
        'persons'
        )
