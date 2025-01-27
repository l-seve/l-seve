import json

def generate_map_html(markers):
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Carte centrée sur la France</title>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.7.1/dist/leaflet.css" />
        <style>
            #map {{
                height: 100vh;
            }}
        </style>
    </head>
    <body>
        <div id="map"></div>
        <script src="https://unpkg.com/leaflet@1.7.1/dist/leaflet.js"></script>
        <script>
            var map = L.map('map').setView([46.603354, 1.888334], 6); // Coordonnées pour centrer sur la France

            L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
                attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            }}).addTo(map);

            var markers = {json.dumps(markers)};
            markers.forEach(function(marker) {{
                L.marker([marker.lat, marker.lng]).addTo(map);
            }});
        </script>
    </body>
    </html>
    """
    with open("map.html", "w") as file:
        file.write(html_content)