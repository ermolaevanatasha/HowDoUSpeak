from flask import Flask
from flask import url_for, render_template, request, redirect, json

app = Flask(__name__)

answer_keys = ['numbers', 'shoulder', 'strawberry', 'bread', 'perepechi', 
               'sweater', 'hair', 'bag', 'mop', 'file']

questionnaire_keys = ['name', 'age', 'sex', 'birthplace', 'live_now']

@app.route('/')
def index():
    return render_template('index.html')
    
@app.route('/form')
def get_form():
    return render_template('form.html', regions=get_regions(), answer_keys=answer_keys)

@app.route('/form', methods=['POST'])
def post_form():
    answers = {}
    questionnaire = {}

    with open('data.json','a', encoding='utf-8') as file:
        result = {}

        for name, value in request.form.items():
            value = value.strip()

            if name in questionnaire_keys:
                questionnaire[name] = value
            elif name in answer_keys:
                answers[name] = value.lower()
            else:
                pass

        # set default values
        if not questionnaire['name']:
            questionnaire['name'] = 'Unknown'

        result['answers'] = answers
        result['questionnaire'] = questionnaire

        file.write(json.dumps(result) + '\n')
    
    return redirect(url_for('thanks', name=questionnaire['name']))

@app.route('/json')
def json_result():
    return json.jsonify(get_json_data())

@app.route('/thanks')
def thanks():
    if request.args:
        name = request.args['name']
        return render_template('thanks.html', name=name)

    return redirect(url_for('index'))

@app.route('/search')
def search():
    if request.args:
        return redirect(url_for('results', text=request.args['text']))

    return render_template('search.html')

@app.route('/results')
def results():
    result = {}
    text = request.args['text'].lower()
    regions = get_regions()

    def search_region(region_id):
        for region in regions:
            if region['id'] == region_id:
                return region['title']

        return None

    for json_data in get_json_data():
        answer_data = json_data['answers']
        questionnaire_data = json_data['questionnaire']
        region_id = int(questionnaire_data['live_now'] or 0)

        for answer_id in answer_keys:
            if answer_data[answer_id] == text:
                if answer_id not in result:
                    result[answer_id] = {}

                region_name = search_region(region_id)
                count = result[answer_id].get(region_name, 0)
                count += 1
                result[answer_id][region_name] = count

    return render_template('results.html', result=result, text=text)


@app.route('/stats')
def stats():
    answers = {}
    
    for answer_id in answer_keys:
        answers[answer_id] = {}

    for json_data in get_json_data():
        answers_data = json_data['answers']
        for answer_id, user_answer in answers_data.items():
            concrete_answer = answers[answer_id]
            count_answers = concrete_answer.get(user_answer, 0)
            count_answers += 1
            answers[answer_id][user_answer] = count_answers

    return render_template('stats.html', answer_keys=answer_keys, answers=answers)


def get_json_data():
    results = []

    with open('data.json') as jsonfile:
        for line in jsonfile:
            data = json.loads(line)
            results.append(data)

    return results

def get_regions():
    with open('regions.json') as jsonfile:
        json_data = json.load(jsonfile)

    return json_data

if __name__ == '__main__':
    app.run(debug=True)
