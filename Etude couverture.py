import json
import webbrowser

def generate_map_html(markers):
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Etude de couverture</title>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.7.1/dist/leaflet.css" />
        <style>
            #map {{
                height: 100vh;
            }}
            #marker-list {{
                position: absolute;
                top: 10px;
                left: 10px;
                background: white;
                padding: 10px;
                border: 1px solid #ccc;
                z-index: 1000;
                max-height: 200px;
                overflow-y: auto;
            }}
            #marker-list-header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
            }}
            #export-button, #import-button {{
                background: white;
                padding: 5px 10px;
                border: 1px solid #ccc;
                cursor: pointer;
                margin-left: 5px;
            }}
            #toggle-button {{
                position: absolute;
                bottom: 10px;
                left: 10px;
                background: white;
                padding: 5px 10px;
                border: 1px solid #ccc;
                cursor: pointer;
                z-index: 1000;
            }}
            #marker-details {{
                position: absolute;
                bottom: 10px;
                left: 10px;
                background: white;
                padding: 10px;
                border: 1px solid #ccc;
                z-index: 1000;
                display: none;
            }}
            #city-search {{
                position: absolute;
                top: 10px;
                right: 10px;
                background: white;
                padding: 10px;
                border: 1px solid #ccc;
                z-index: 1000;
            }}
        </style>
    </head>
    <body>
        <div id="map"></div>
        <div id="marker-list">
            <div id="marker-list-header">
                <h3>Marqueurs</h3>
                <input type="file" id="import-button" accept=".csv">
                <button id="export-button">Exporter en CSV</button>
            </div>
            <ul id="marker-list-items"></ul>
        </div>
        <button id="toggle-button">▼ Replier le tableau</button>
        <div id="marker-details">
            <h3>D&eacute;tails du marqueur</h3>
            <p id="marker-info"></p>
        </div>
        <div id="city-search">
            <input type="text" id="city-name" placeholder="Nom de la ville">
            <button id="search-button">Rechercher</button>
        </div>
        <script src="https://unpkg.com/leaflet@1.7.1/dist/leaflet.js"></script>
        <script>
            var map = L.map('map').setView([50.291, 2.777], 12); // Coordonnées pour centrer sur Arras

            L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
                attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            }}).addTo(map);

            var markers = {json.dumps(markers)};
            var markerData = [];
            var markerObjects = [];
            var markerCount = 0;
            var selectedMarkerIndex = null;

            function addMarker(lat, lng) {{
                var marker = L.marker([lat, lng]).addTo(map);
                var circle1 = L.circle([lat, lng], {{
                    color: 'yellow',
                    fillColor: '#FFFF99',
                    fillOpacity: 0.1,
                    radius: 1500 // 1.5 km de rayon
                }}).addTo(map);
                var circle2 = L.circle([lat, lng], {{
                    color: 'orange',
                    fillColor: '#FFA500',
                    fillOpacity: 0.3,
                    radius: 3000 // 3 km de rayon
                }}).addTo(map);

                markerCount++;
                var markerList = document.getElementById('marker-list-items');
                var listItem = document.createElement('li');
                listItem.textContent = markerCount + ' - Lat: ' + lat + ', Lng: ' + lng;
                listItem.dataset.index = markerCount - 1;
                listItem.addEventListener('click', function() {{
                    selectedMarkerIndex = this.dataset.index;
                    document.getElementById('marker-info').textContent = 'Marqueur ' + (parseInt(selectedMarkerIndex) + 1) + ' - Lat: ' + markerData[selectedMarkerIndex].lat + ', Lng: ' + markerData[selectedMarkerIndex].lng;
                    document.getElementById('marker-details').style.display = 'block';
                }});
                markerList.appendChild(listItem);

                markerData.push({{lat: lat, lng: lng}});
                markerObjects.push({{marker: marker, circle1: circle1, circle2: circle2}});
            }}

            map.on('click', function(e) {{
                var lat = e.latlng.lat;
                var lng = e.latlng.lng;
                addMarker(lat, lng);
            }});

            document.getElementById('export-button').addEventListener('click', function() {{
                var csvContent = "data:text/csv;charset=utf-8,";
                csvContent += "identification,latitude,longitude\\n";
                markerData.forEach(function(marker, index) {{
                    csvContent += (index + 1) + "," + marker.lat + "," + marker.lng + "\\n";
                }});
                var encodedUri = encodeURI(csvContent);
                var link = document.createElement("a");
                link.setAttribute("href", encodedUri);
                link.setAttribute("download", "markers.csv");
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
            }});

            document.getElementById('import-button').addEventListener('change', function(event) {{
                var file = event.target.files[0];
                if (file) {{
                    var reader = new FileReader();
                    reader.onload = function(e) {{
                        var csvContent = e.target.result;
                        var lines = csvContent.split("\\n");
                        for (var i = 1; i < lines.length; i++) {{
                            var line = lines[i];
                            if (line.trim() === "") continue;
                            var parts = line.split(",");
                            var lat = parseFloat(parts[1]);
                            var lng = parseFloat(parts[2]);
                            addMarker(lat, lng);
                        }}
                    }};
                    reader.readAsText(file);
                }}
            }});

            document.getElementById('toggle-button').addEventListener('click', function() {{
                var markerList = document.getElementById('marker-list');
                var toggleButton = document.getElementById('toggle-button');
                if (markerList.style.display === 'none') {{
                    markerList.style.display = 'block';
                    toggleButton.textContent = '▼ Replier le tableau';
                }} else {{
                    markerList.style.display = 'none';
                    toggleButton.textContent = '▲ Déplier le tableau';
                }}
            }});

            document.getElementById('search-button').addEventListener('click', function() {{
                var cityName = document.getElementById('city-name').value;
                if (cityName) {{
                    fetch(`https://nominatim.openstreetmap.org/search?city=${{cityName}}&format=json`)
                        .then(response => response.json())
                        .then(data => {{
                            if (data.length > 0) {{
                                var lat = data[0].lat;
                                var lon = data[0].lon;
                                map.setView([lat, lon], 12);
                            }} else {{
                                alert('Ville non trouvée');
                            }}
                        }})
                        .catch(error => {{
                            console.error('Erreur:', error);
                        }});
                }}
            }});
        </script>
    </body>
    </html>
    """
    with open("map.html", "w", encoding="utf-8") as file:
        file.write(html_content)
    
    # Ouvrir la carte dans le navigateur par défaut
    webbrowser.open("map.html")

# Exemple d'utilisation
markers = []
generate_map_html(markers)