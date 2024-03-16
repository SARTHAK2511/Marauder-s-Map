from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process_coordinates', methods=['POST'])
def process_coordinates():
    data = request.get_json()
    start_coords = data.get('start_coords')
    end_coords = data.get('end_coords')

    # Perform any necessary operations with the coordinates
    # For example, you can pass them to a separate function
    # and return the result as JSON
    result = process_coordinates_function(start_coords, end_coords)

    return jsonify(result)

def process_coordinates_function(start_coords, end_coords):
    # Your logic to process the coordinates
    # This can be any Python function that you want to execute
    print(start_coords, end_coords)
    return {'result': 'Coordinates processed successfully'}

if __name__ == '__main__':
    app.run(debug=True)
