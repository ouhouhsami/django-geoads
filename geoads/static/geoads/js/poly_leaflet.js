$(document).ready(function() {
	map = L.map('map').setView([lat, lng], 13);
	// init OSM layer using cloudmate style
	L.tileLayer('http://{s}.tile.cloudmade.com/cdf5c675c08548d1bb4ea612f3319b62/997/256/{z}/{x}/{y}.png', {
		maxZoom: 18,
		attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, <a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="http://cloudmade.com">CloudMade</a>'
	}).addTo(map);
	// init draw control to draw polygon (and only polygon)
	var drawControl = new L.Control.Draw({
		position: 'topleft',
		polygon: {
			allowIntersection: false,
			shapeOptions: {
				color: polygonStyle.strokeColor,
				fill: polygonStyle.fillColor
			}
		},
		polyline: false, rectangle: false, circle:false, marker:false
	});
	map.addControl(drawControl);
	// init the layer that hold the polygon
	var drawnItems = new L.LayerGroup();
	/*
	Fill the textarea when polygon is drawn
	*/
	map.on('draw:poly-created', function (e) {
		drawnItems.clearLayers(); // remove layers
		drawnItems.addLayer(e.poly); // add current drawn layer
		var val = 'SRID=900913;POLYGON((';
			len = e.poly.getLatLngs().length;
			v_zero = '';
			for(var i=0; i<len; i++){
				val += e.poly.getLatLngs()[i].lng+' '+e.poly.getLatLngs()[i].lat+',';
				if(i === 0){
					v_zero = e.poly.getLatLngs()[i].lng+' '+e.poly.getLatLngs()[i].lat;
				}
			}
			val = val+v_zero+'))';
	$('#id_location').val(val);
	});
	map.addLayer(drawnItems);
	/*
	Initialize map w/ polygon when textarea is filled
	*/
	if ($('#id_location').val() !== '') {
		var points = $('#id_location').val().split('SRID=900913;POLYGON((')[1].split('))')[0].split(',');
		$('#id_location').val().split('SRID=900913;POLYGON((')[1].split('))')[0].split(',');
		var latLngs = [];
		for (i = 0; i < points.length - 1; i++) {
			var point = points[i].split(" ");
			latLngs.push([parseFloat(point[1]), parseFloat(point[0])]);
		}
		poly = new L.Polygon(latLngs, {color:polygonStyle.strokeColor});
		drawnItems.clearLayers();
		drawnItems.addLayer(poly);
		map.fitBounds(poly.getBounds());
	}
	/*
	Add homes on map
	*/
	for(i=0; i<homes.length; i++){
		var home = homes[i];
		var latLng = [parseFloat(home.y), parseFloat(home.x)];
		var icon = L.icon({iconUrl:home.icon, iconSize: [32, 37], iconAnchor: [16, 36], popupAnchor: [0, -19]});
		var marker = new L.marker(latLng, {icon: icon});
		if(home.visible === 'true'){
			marker.addTo(map);
		}
		marker.html = $('.' + homes[i].id).html();
		marker.on('click', function(e){
			e.target.bindPopup(e.target.html).openPopup();
		});
		homes[i].marker = marker;
	}
});

add_home = function (x, y, url, id, visible, icon) {
	homes.push({'x': x, 'y': y, 'url': url, 'id': id, 'visible': visible, 'icon':icon});
};


open_popup = function (x, y, id) {
	for (var i = 0; i < homes.length; i++) {
		if (homes[i].id == id) {
			homes[i].marker.addTo(map);
			homes[i].marker.fire('click');
		}
	}
};
