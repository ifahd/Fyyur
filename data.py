    INSERT INTO public.venues(
	name, city, state, address, phone, image_link, facebook_link, genres, website, seeking_talent, seeking_description)
	VALUES ('Park Square Live Music & Coffee', 'San Francisco', 'CA', '34 Whiskey Moore Ave', '415-000-1234', 'https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80', 'https://www.facebook.com/ParkSquareLiveMusicAndCoffee', 'Rock n Roll,Jazz,Classical,Folk', 'https://www.parksquarelivemusicandcoffee.com', False, '');

    INSERT INTO public.artists(
	name, city, state, phone, image_link, facebook_link, genres, website, seeking_talent, seeking_description)
	VALUES ('Park Square Live Music & Coffee', 'San Francisco', 'CA', '415-000-1234', 'https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80', 'https://www.facebook.com/ParkSquareLiveMusicAndCoffee', 'Rock n Roll,Jazz,Classical,Folk', 'https://www.parksquarelivemusicandcoffee.com', False, '');	

# INSERT INTO public.shows(
# 	id,venue_id, artist_id, start_time)
# 	VALUES (1,1, 1, '2020-09-29 23:38:05');