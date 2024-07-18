from threading import Thread
from flask import Flask, jsonify, request, abort
from uuid import uuid4
from .crews import TechnologyResearchCrew
from .log_manager import *
import json

app = Flask(__name__)


@app.route('/api/multiagent/<input_id>', methods=['GET'])
def get_status(input_id):
    with outputs_lock:
        output = outputs.get(input_id)
        if output is outputs:
            abort(404, description="Output not found")
        # Convert output sang json object
        try:
            result_json = json.loads(output.result)
        except json.JSONDecodeError:
            # Nếu fails thì xét kết quả như output ban đầu luôn :))) kiểu str
            result_json = output.result
        return jsonify({
            "input_id": input_id,
            "status": output.status,
            "result": result_json,
            "events": [{
                'timestamp': event.timestamp.isoformat(),
                'data': event.data
            } for event in output.events]
        })
    # return jsonify({"status": f"Getting status for {input_id}"}), 200


def kickoff_crew(input_id, technologies: list[str], businessareas: list[str]):
    print(
        f"Running crew for {input_id} with technologies {technologies} and businessareas {businessareas}")

    results = None
    try:
        technology_research_crew = TechnologyResearchCrew(input_id)
        technology_research_crew.setup_crew(technologies, businessareas)
        results = technology_research_crew.kickoff()
    except Exception as e:
        print(f"CREW FAILED : {str(e)}")
        append_event(input_id, f"CREW FAILED: {str(e)}")
        with outputs_lock:
            outputs[input_id].status = 'EROER'
            outputs[input_id].result = str(e)

    with outputs_lock:
        outputs[input_id].status = 'COMPLETE'
        outputs[input_id].result = results
        outputs[input_id].events.append(
            Event(timestamp=datetime.now(), data="Crew Complete"))


@app.route('/api/multiagent', methods=['POST'])
def run_multiagent():
    data = request.json
    if not data or 'technologies' not in data or 'businessareas' not in data:
        abort(400, description="Invalid request with missing data.")

    input_id = str(uuid4())
    technologies = data['technologies']
    businessareas = data['businessareas']

    thread = Thread(target=kickoff_crew, args=(
        input_id, technologies, businessareas))
    thread.start()
    # return jsonify({"status": "success"}), 200
    return jsonify({"input_id": input_id}), 200


if __name__ == '__main__':
    app.run(debug=True, port=3001)
