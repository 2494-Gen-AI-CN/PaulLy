import json
from flask import Flask, render_template,request,jsonify

app = Flask(__name__, template_folder='.')


@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    return response


@app.route('/')
def index():
    return render_template('Index.html')

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

STATS = ['hp', 'str', 'mag', 'spd', 'dex', 'def', 'res', 'lck', 'cha']


def calc_ev(
    stats: dict[str, float | int],
    char_growth: dict[str, int | float],
    class_growth: dict[str, int | float | None],
    starting_level: int,
    ending_level: int,
) -> dict[str, float]:
    updated_stats = dict(stats)
    # Leveling from starting_level to ending_level grants (ending_level - starting_level) level-ups
    for _level in range(starting_level, ending_level):
        for stat_name in STATS:
            base_rate = char_growth.get(stat_name) or 0
            cls_rate = class_growth.get(stat_name) or 0
            total_rate = max(0, base_rate + cls_rate) / 100.0
            updated_stats[stat_name] = updated_stats.get(stat_name, 0) + total_rate

    return updated_stats


@app.route('/calculate_ev', methods=['POST'])
def handle_calculate_ev():
    payload = request.get_json()  # Gets the inputs sent from HTML

    with open(r'./asset/character_growth_rate.json') as f:
        char_data = json.load(f)
    with open(r'./asset/class_growth_rate.json') as f:
        class_data = json.load(f)

    character = payload['character']
    start_level = int(payload['start_level'])
    end_level = int(payload['end_level'])
    initial_stats = dict(payload['current_stats'])
    current_stats = dict(initial_stats)
    segments = payload.get('segments') or []

    char_growth = char_data.get(character, {})
    segment_gains = []

    if segments:
        current_lvl = start_level
        for section in segments:
            until_lvl = min(int(section['until_level']), end_level)
            if until_lvl <= current_lvl:
                continue

            class_name = section['class_name']
            cls_growth = class_data.get(class_name, {})

            before_seg = dict(current_stats)
            current_stats = calc_ev(current_stats, char_growth, cls_growth, current_lvl, until_lvl)

            segment_gains.append({
                "segment": section['segment'],
                "class_name": class_name,
                "from_level": current_lvl,
                "until_level": until_lvl,
                "gains": {s: round(current_stats[s] - before_seg[s], 2) for s in STATS}
            })
            current_lvl = until_lvl
    else:
        current_stats = calc_ev(current_stats, char_growth, {}, start_level, end_level)

    expected_stats = {s: round(current_stats[s], 2) for s in STATS}
    stat_gains = {s: round(current_stats[s] - initial_stats[s], 2) for s in STATS}

    # Return structure expected by the frontend:
    return jsonify({
        "status": "success",
        "expected_stats": expected_stats,
        "stat_gains": stat_gains,
        "segment_gains": segment_gains
    })

if __name__ == '__main__':
    app.run(debug=True)

