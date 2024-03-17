from flask import Flask, render_template, request, jsonify, redirect, url_for
from shortest import calculate_shortest
from quitest import calculate_quietest
import webbrowser
import subprocess
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process_coordinates', methods=['POST'])
def process_coordinates():
    data = request.get_json()
    start_coords = data.get('start_coords')
    end_coords = data.get('end_coords')

    print(start_coords, end_coords)
    shortest_data = calculate_shortest(start_coords,end_coords)
    quietest_data = calculate_quietest(start_coords,end_coords)
    print(shortest_data, quietest_data)
    # result = {'result': output}
    # response = jsonify(result)
    # webbrowser.quopen("shortest.html")
    # Redirect to the route for rendering the HTML file
    return quietest_data
    

@app.route('/quietest_html')
def quietest_html():
    # Render the HTML file and return it
    return render_template('quietest.html')

@app.route('/shortest_html')
def shortest_html():
    # Render the HTML file and return it
    return render_template('shortest.html')

if __name__ == '__main__':
    # webbrowser.open("http://127.0.0.1:5000/render_html")
    
    app.run(debug=True)
