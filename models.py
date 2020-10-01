from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import datetime

db = SQLAlchemy()

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    genres = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(300))
    created_at = db.Column(db.DateTime, default=datetime.datetime.now())
    updated_at = db.Column(db.DateTime, default=datetime.datetime.now(), onupdate=datetime.datetime.now())    
    shows = db.relationship('Show', backref='venues', lazy=True)
    
    @property
    def toDictionary(self):
        return {
            'id': self.id,
            'name': self.name,
            'genres': self.genres.split(','),
            'address': self.address,
            'city': self.city,
            'state': self.state,
            'phone': self.phone,
            'website': self.website,
            'facebook_link': self.facebook_link,
            'seeking_talent': self.seeking_talent,
            'seeking_description': self.seeking_description,
            'image_link': self.image_link
        }
    @property
    def withUpcomingShows(self):
        return {
            'id': self.id,
            'name': self.name,
            'num_upcoming_shows': Show.query.filter(Show.start_time > datetime.datetime.now(),Show.venue_id == self.id).count()
        }

class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(300))
    available_from_date = db.Column(db.DateTime(), nullable=True)
    available_to_date = db.Column(db.DateTime(), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now())
    updated_at = db.Column(db.DateTime, default=datetime.datetime.now(), onupdate=datetime.datetime.now())
    shows = db.relationship('Show', backref='artists', lazy=True)

    @property
    def toDictionary(self):
        return {
            'id': self.id,
            'name': self.name,
            'genres': self.genres.split(','),
            'city': self.city,
            'state': self.state,
            'phone': self.phone,
            'website': self.website,
            'facebook_link': self.facebook_link,
            'seeking_venue': self.seeking_venue,
            'seeking_description': self.seeking_description,
            'image_link': self.image_link
        }
    @property
    def withUpcomingShows(self):
        return {
            'id': self.id,
            'name': self.name,
            'num_upcoming_shows': Show.query.filter(Show.start_time > datetime.datetime.now(),Show.artist_id == self.id).count()
        }
    @property
    def isAvailable(self):
        if not self.available_from_date and not self.available_to_date:
            return True
        return True if (self.available_from_date < datetime.datetime.now() and self.available_to_date > datetime.datetime.now()) else False

class Show(db.Model):
    __tablename__ = 'shows'
    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('venues.id', ondelete='CASCADE'), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('artists.id', ondelete='CASCADE'), nullable=False)
    start_time = db.Column(db.DateTime())
    created_at = db.Column(db.DateTime, default=datetime.datetime.now())
    updated_at = db.Column(db.DateTime, default=datetime.datetime.now(), onupdate=datetime.datetime.now())

    def shows(self, Model):
        model_name = Model.__name__.lower()
        model = Model.query.get(getattr(self, model_name + '_id'))
        return {
            model_name + "_id": model.id,
            model_name + "_name": model.name + ' ' + Model.__name__,
            model_name + "_image_link": model.image_link,
            "start_time": self.start_time.strftime("%Y-%m-%d %H:%M:%S")
        }



