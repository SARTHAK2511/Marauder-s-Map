// Initialize the map
var map = L.map('map').setView([22.7196, 75.857], 13);

// Add the OpenStreetMap_Mapnik tile layer
var OpenStreetMap_Mapnik = L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
  maxZoom: 19,
  attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);

// Define variables for start and end coordinates
var startCoords = null;
var endCoords = null;

function resetMap() {
    // Check if startMarker exists and remove it from the map
    if (startMarker) {
        map.removeLayer(startMarker);
        startMarker = null;
        startCoords = null; // Reset startCoords if it's being used outside marker logic
    }

    // Check if endMarker exists and remove it from the map
    if (endMarker) {
        map.removeLayer(endMarker);
        endMarker = null;
        endCoords = null; // Reset endCoords if it's being used outside marker logic
    }

    // Optionally, reset the map view to a default position and zoom level
    // Change the latitude, longitude, and zoom level to your desired default values
    map.setView([22.7196, 75.857], 13);
}

// Bind the reset function to a button or another UI element
document.getElementById('reset-btn').addEventListener('click', resetMap);

// Function to handle click events on the map
function onMapClick(e) {
  if (!startCoords) {
    startCoords = e.latlng;
    L.marker(startCoords).addTo(map)
      .bindPopup("<b>Start Destination</b><br>Coordinates: " + startCoords).openPopup();
  } else if (!endCoords) {
    endCoords = e.latlng;
    L.marker(endCoords).addTo(map)
      .bindPopup("<b>End Destination</b><br>Coordinates: " + endCoords).openPopup();

    // Calculate distance between start and end coordinates
    var distance = calculateDistance(startCoords.lat, startCoords.lng, endCoords.lat, endCoords.lng);
    console.log('Shortest distance between start and end points: ' + distance.toFixed(2) + ' meters');
    sendCoordinatesToFlask(startCoords.lat, endCoords.lat);
  }
}

// Add click event listener to the map
map.on('click', onMapClick);

// Function to calculate distance between two points using Haversine formula
function calculateDistance(lat1, lon1, lat2, lon2) {
  const R = 6371e3; // Radius of Earth in meters
  const φ1 = lat1 * Math.PI / 180; // Convert degrees to radians
  const φ2 = lat2 * Math.PI / 180;
  const Δφ = (lat2 - lat1) * Math.PI / 180;
  const Δλ = (lon2 - lon1) * Math.PI / 180;

  const a = Math.sin(Δφ / 2) * Math.sin(Δφ / 2) +
    Math.cos(φ1) * Math.cos(φ2) *
    Math.sin(Δλ / 2) * Math.sin(Δλ / 2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));

  const distance = R * c; // Distance in meters
  return distance;
}
function sendCoordinatesToFlask(startCoords, endCoords) {
  var xhr = new XMLHttpRequest();
  xhr.open('POST', '/process_coordinates', true);
  xhr.setRequestHeader('Content-Type', 'application/json');
  xhr.onreadystatechange = function() {
      if (xhr.readyState === 4 && xhr.status === 200) {
          var response = JSON.parse(xhr.responseText);
          console.log(response.result);
          // Process the response as needed
      }
  };
  var data = JSON.stringify({
      start_coords: startCoords,
      end_coords: endCoords
  });
  xhr.send(data);
}

// Call this function with the start and end coordinates
// after they are selected or entered by the user
// For example:
// console.log(startCoords,endCoords);

