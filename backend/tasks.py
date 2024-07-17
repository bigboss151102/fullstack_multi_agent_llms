from textwrap import dedent
from crewai import Agent, Task
from .log_manager import append_event


class ResearchTask():
    def __init__(self, input_id):
        self.input_id = input_id

    def append_event_callback(self, task_output):
        print(f"Appending event for {self.input_id} with output {task_output}")
        append_event(self.input_id, task_output.exported_output)

    def manage_research(self, agent: Agent, technologies: list[str], businessareas: list[str], tasks: list[Task]):
        return Task(
            description=dedent(f"""Based on the list of technologies {technologies} and the business areas {businessareas},
                            use the results from the Research Agent to research each business area in each technology.
                            to put together a json object containing the URLs for 3 blog articles, the URLs and title
                            for 3 YouTube interviews for each business area in each technology."""),
            agent=agent,
            expected_output=dedent(
                """ A json object containing the URLs for 3 blog articles and the URLs and
                titles for 3 YouTube interviews for each business area in each technology."""),
            callback=self.append_event_callback,
            context=tasks,
            output_json=BusinessareaInfoList
        )
