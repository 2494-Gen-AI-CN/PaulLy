import json
from flask import Flask, render_template,request,jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/getCharData')
def get_char_data():
    with open(r'./asset/character.json') as json_file:
        data = json.load(json_file)
        return jsonify(data)
@app.route('/getClassData')
def get_growth_data():
    with open(r'./asset/class_growth_rate.json') as json_file:
        data = json.load(json_file)
        return jsonify(data)

def calc_ev(stat : float |int, starting_level : int, ending_level : int) -> float | int:

    _stat = stat or 0
    return 0

@app.route('/calculate_ev', methods=['POST'])
def handle_calculate_ev():
    payload = request.get_json()  # Gets the inputs sent from HTML
    character_data = json.load(open('./asset/character.json')) # if you need character base rates
    # Your Python core logic will process this payload:
    # payload['character']     -> e.g. "Eshmel"
    # payload['start_level']   -> e.g. 1
    # payload['end_level']     -> e.g. 40
    # payload['current_stats'] -> e.g. {"hp": 20, "str": 8, ...}
    # payload['segments']      -> e.g. [{"segment": 1, "start_level": 1, "end_level": 20, "class_name": "Gladiator", "mount": "None / Foot"}, ...]

    current = payload.get('current_stats', {})

    # Return structure expected by the frontend:
    return jsonify({
        "status": "success",
        "expected_stats": current,  # Replace with your calculated final stats
        "stat_gains": {s: 0 for s in ['hp', 'str', 'mag', 'spd', 'dex', 'def', 'res', 'lck', 'cha']}, # Replace with calculated gains
        "segment_gains": []  # Optional: per-segment breakdown
    })

if __name__ == '__main__':
    app.run(debug=True)

