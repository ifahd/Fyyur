#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from sqlalchemy import func, or_, and_
import datetime
from models import db, Venue, Artist, Show

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')

db.init_app(app)
migrate = Migrate(app, db)


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  # last added venues 
  venues = Venue.query.order_by(Venue.created_at.desc()).limit(10).all()
  # last added artists
  artists = Artist.query.order_by(Artist.created_at.desc()).limit(10).all()
  # data object
  data = {
    'venues': venues,
    'venues_count': len(venues),
    'artists': artists,
    'artists_count': len(artists),
  }

  return render_template('pages/home.html', recent=data)

#----------------------------------------------------------------------------#
#  Venues
#----------------------------------------------------------------------------#

#  All Venues
#----------------------------------------------------------------------------#
@app.route('/venues')
def venues():
  
  # get all unique state 
  city_state = Venue.query.distinct(Venue.city, Venue.state).all()
  
  data = []
  
  # loop in all unique state
  for cs in city_state:
    obj = {}
    obj['state'] = cs.state
    obj['city'] = cs.city
    obj['venues'] = [v.withUpcomingShows for v in Venue.query.filter_by(state=cs.state).all()]
    data.append(obj)
  
  return render_template('pages/venues.html', areas=data)

#  Search in Venues
#----------------------------------------------------------------------------#
@app.route('/venues/search', methods=['POST'])
def search_venues():

  search_term = request.form.get('search_term', '')
  
  # search by name or state or city or city with state
  venues = Venue.query.filter(or_(
    Venue.name.ilike('%' + search_term + '%'),
    Venue.state.ilike('%' + search_term + '%'), 
    Venue.city.ilike('%' + search_term + '%'), 
    (Venue.city + ', ' + Venue.state).like('{0}%'.format(search_term))
  )).all()
  
  response = {
    'count': len(venues),
    'data': [v.withUpcomingShows for v in venues]
  }

  return render_template('pages/search_venues.html', results=response, search_term=search_term)

#  Show Venue
#----------------------------------------------------------------------------#
@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # get venue by id 
  venue = Venue.query.get(venue_id)

  # get venue data as dictionary
  data = venue.toDictionary
  
  # past show 
  past_show = Show.query.filter(Show.start_time < datetime.datetime.now(), Show.venue_id == venue.id).all()
  data['past_shows'] = [s.shows(Model=Artist) for s in past_show]
  data['past_shows_count'] = len(past_show)

  # upcoming shows 
  upcoming_shows = Show.query.filter(Show.start_time > datetime.datetime.now(), Show.venue_id == venue.id).all()
  data['upcoming_shows'] = [s.shows(Model=Artist) for s in upcoming_shows]
  data['upcoming_shows_count'] = len(upcoming_shows)
  
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():

  failed = False
  try:
    venue = Venue(
      name = request.form['name'],
      city = request.form['city'],
      state = request.form['state'],
      address = request.form['address'],
      phone = request.form['phone'],
      image_link = request.form['image_link'],
      facebook_link = request.form['facebook_link'],
      genres = ','.join(request.form.getlist('genres')),
      website = request.form['website'],
      seeking_talent =  int(request.form['seeking_talent']),
      seeking_description = request.form['seeking_description'],
      created_at = datetime.datetime.now(),
      updated_at = datetime.datetime.now()
    )
    db.session.add(venue)
    db.session.commit()
  except:
    failed = True
    db.session.rollback()
  finally:
    if failed: 
      flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
    else:
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
    db.session.close()  
  return redirect(url_for('index'))

#  Delete Venue
#----------------------------------------------------------------------------#
@app.route('/venues/<venue_id>', methods=['POST'])
def delete_venue(venue_id):
  failed = False
  try:
    Venue.query.filter_by(id=venue_id).delete()
    db.session.commit()
  except:
    failed = True
    db.session.rollback()
  finally:
    if failed: 
      flash('An error occurred. Venue could not be deleted.')
    else:
      flash('Venue was successfully deleted!')
    db.session.close()
  return redirect(url_for('index'))

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  data = Artist.query.with_entities(Artist.id, Artist.name)
  return render_template('pages/artists.html', artists=data)

#  Search in Artists
#  ----------------------------------------------------------------
@app.route('/artists/search', methods=['POST'])
def search_artists():
  
  search_term = request.form.get('search_term', '')
  
  # search by name or state or city or city with state
  artists = Artist.query.filter(or_(
    Artist.name.ilike('%' + search_term + '%'),
    Artist.state.ilike('%' + search_term + '%'), 
    Artist.city.ilike('%' + search_term + '%'), 
    (Artist.city + ', ' + Artist.state).like('{0}%'.format(search_term))
  )).all()

  response = {
    'count': len(artists),
    'data': [a.withUpcomingShows for a in artists]
  }

  return render_template('pages/search_artists.html', results=response, search_term=search_term)

#  Show Artist
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):

  # get artist by id 
  artist = Artist.query.get(artist_id)

  # get artist data as dictionary
  data = artist.toDictionary
  
  # past show 
  past_show = Show.query.filter(Show.start_time < datetime.datetime.now(), Show.artist_id == artist.id).all()
  data['past_shows'] = [s.shows(Model=Venue) for s in past_show]
  data['past_shows_count'] = len(past_show)

  # upcoming shows 
  upcoming_shows = Show.query.filter(Show.start_time > datetime.datetime.now(), Show.artist_id == artist.id).all()
  data['upcoming_shows'] = [s.shows(Model=Venue) for s in upcoming_shows]
  data['upcoming_shows_count'] = len(upcoming_shows)

  return render_template('pages/show_artist.html', artist=data)

#  Update Artist
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist = Artist.query.get(artist_id)
  form = ArtistForm(
    name=artist.name,
    city=artist.city,
    phone=artist.phone,
    image_link=artist.image_link,
    facebook_link=artist.facebook_link,
    genres=artist.genres.split(','),
    website=artist.website,
    seeking_venue= int(artist.seeking_venue),
    seeking_description=artist.seeking_description,
    available_from_date = artist.available_from_date,
    available_to_date = artist.available_to_date,
  )

  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  failed = False
  try:
    artist = Artist.query.get(artist_id)
    artist.name = request.form['name']
    artist.city = request.form['city']
    artist.state = request.form['state']
    artist.phone = request.form['phone']
    artist.image_link = request.form['image_link']
    artist.facebook_link = request.form['facebook_link']
    artist.genres = ','.join(request.form.getlist('genres'))
    artist.website = request.form['website']
    artist.seeking_venue =  int(request.form['seeking_venue'])
    artist.seeking_description = request.form['seeking_description']
    artist.available_from_date = request.form['available_from_date'],
    artist.available_to_date = request.form['available_to_date'],
    artist.updated_at = datetime.datetime.now()
    db.session.add(artist)
    db.session.commit()
  except:
    failed = True
    db.session.rollback()
  finally:
    if failed: 
      flash('An error occurred. Artist ' + artist.name + ' could not be updated.')
    else:
      flash('Artist ' + artist.name + ' was successfully updated!')  
    db.session.close()  

  return redirect(url_for('show_artist', artist_id=artist_id))

#  Update Venue
#  ----------------------------------------------------------------
@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue = Venue.query.get(venue_id)
  form = VenueForm(
    name=venue.name,
    city=venue.city,
    address=venue.address,
    phone=venue.phone,
    image_link=venue.image_link,
    facebook_link=venue.facebook_link,
    genres=venue.genres.split(','),
    website=venue.website,
    seeking_talent= int(venue.seeking_talent),
    seeking_description=venue.seeking_description,
  )

  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  failed = False
  try:
    venue = Venue.query.get(venue_id)
    venue.name = request.form['name']
    venue.city = request.form['city']
    venue.state = request.form['state']
    venue.address = request.form['address']
    venue.phone = request.form['phone']
    venue.image_link = request.form['image_link']
    venue.facebook_link = request.form['facebook_link']
    venue.genres = ','.join(request.form.getlist('genres'))
    venue.website = request.form['website']
    venue.seeking_talent =  int(request.form['seeking_talent'])
    venue.seeking_description = request.form['seeking_description']
    venue.updated_at = datetime.datetime.now()
    db.session.add(venue)
    db.session.commit()
  except:
    failed = True
    db.session.rollback()
  finally:
    if failed: 
      flash('An error occurred. Venue ' + venue.name + ' could not be updated.')
    else:
      flash('Venue ' + venue.name + ' was successfully updated!')
    db.session.close()
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  failed = False
  try:
    artist = Artist(
      name = request.form['name'],
      city = request.form['city'],
      state = request.form['state'],
      phone = request.form['phone'],
      image_link = request.form['image_link'],
      facebook_link = request.form['facebook_link'],
      genres = ','.join(request.form.getlist('genres')),
      website = request.form['website'],
      seeking_venue =  int(request.form['seeking_venue']),
      seeking_description = request.form['seeking_description'],
      available_from_date = request.form['available_from_date'],
      available_to_date = request.form['available_to_date'],
      created_at = datetime.datetime.now(),
      updated_at = datetime.datetime.now()
    )
    db.session.add(artist)
    db.session.commit()
  except:
    failed = True
    db.session.rollback()
  finally:
    if failed: 
      flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
    else:
      flash('Artist ' + request.form['name'] + ' was successfully listed!')
    db.session.close()    
  return redirect(url_for('index'))

#  Delete Artist
#  ----------------------------------------------------------------
@app.route('/artists/<artist_id>', methods=['POST'])
def delete_artist(artist_id):
  failed = False
  try:
    Artist.query.filter_by(id=artist_id).delete()
    db.session.commit()
  except:
    failed = True
    db.session.rollback()
  finally:
    if failed: 
      flash('An error occurred. Artist could not be deleted.')
    else:
      flash('Artist was successfully deleted!')
    db.session.close()
  return redirect(url_for('index'))

#  Shows
#  ----------------------------------------------------------------
@app.route('/shows')
def shows():
  data = []
  shows = Show.query.all()
  for s in shows:
    venue = Venue.query.get(s.venue_id)
    artist = Artist.query.get(s.artist_id)
    data.append({
      'venue_id': venue.id,
      'venue_name': venue.name,
      'artist_id': artist.id,
      'artist_name': artist.name,
      'artist_image_link': artist.image_link,
      'start_time': s.start_time.strftime("%Y-%m-%d %H:%M:%S")
    })
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  artist_id = request.form['artist_id']
  artist = Artist.query.get(artist_id)
  if not artist.isAvailable:
    flash('Sorry, The Artist ' + artist.name + ' not available in this time, only available from ' + artist.available_from_date.strftime("%Y-%m-%d %H:%M:%S") + ' to ' + artist.available_to_date.strftime("%Y-%m-%d %H:%M:%S"))
    return redirect(url_for('create_shows'))

  failed = False
  try:
    artist_id = artist_id
    venue_id = request.form['venue_id']
    start_time = request.form['start_time']
    show = Show(
      artist_id=artist_id, 
      venue_id=venue_id, 
      start_time=start_time,
      created_at = datetime.datetime.now(),
      updated_at = datetime.datetime.now()
      )
    db.session.add(show)
    db.session.commit()
  except:
    failed = True
    db.session.rollback()
  finally:
    if failed: 
      flash('An error occurred. Show could not be listed.')
    else:
      flash('Show was successfully listed!')
    db.session.close()  
  return redirect(url_for('index'))

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
