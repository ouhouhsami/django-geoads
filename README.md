Django-geoads
=============

Django application for geolocated ad site.
This app is designed to help you build (awsome) website that will let user 
* create/read/update/delete geolocated ads
* search upon saved ads

As it is a generic app, you will have to provide custom model for Ad, that inherit from
geoads.models.Ad, and set up your urls to use the provided Class-Based Views.

These Class-Based Views will help you (or your users) to create/read/update/delete ads, 
but also search ads, and recording their search.



This app uses also https://github.com/jacobtoye/Leaflet.draw

