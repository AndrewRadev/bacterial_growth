import os
import json
from pathlib import Path


def dump_project_metadata(app):
    """
    A custom function useful for development purposes.

    This dumps project metadata, including all active routes, into a JSON file
    that can be used by a text editor (e.g. Vim) to provide navigation from a
    URL to the python function that handles it.
    """
    project_file = Path('.flask_tools.json')
    project_data = json.loads(project_file.read_text() if project_file.exists() else '{}')

    project_data['template_folder'] = os.path.relpath(app.template_folder)
    project_data['static_folder']   = os.path.relpath(app.static_folder)
    project_data['routes']          = {}

    # Code adapted from werkzeug:
    # https://github.com/pallets/werkzeug/blob/7868bef5d978093a8baa0784464ebe5d775ae92a/src/werkzeug/routing/rules.py#L920-L926
    for rule in app.url_map.iter_rules():
        parts = []
        for is_dynamic, data in rule._trace:
            if is_dynamic:
                parts.append(f"<{data}>")
            else:
                parts.append(data)
        path = "".join(parts).lstrip("|")

        view_func = app.view_functions[rule.endpoint]

        if not view_func.__module__.startswith('flask.') and view_func.__name__ != '<lambda>':
            # Store full path to view function
            project_data['routes'][path] = '.'.join((view_func.__module__, view_func.__name__))

    with project_file.open('w') as f:
        json.dump(project_data, f, indent=4)
