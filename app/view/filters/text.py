import re

from markupsafe import Markup
from flask import url_for, request

from jinja2.utils import urlize


def format_text(text, first_paragraph=False):
    if not text:
        return text

    text = text.strip()
    text = urlize(text, target="_blank", rel="noreferrer nofollow")

    text = re.sub(r'\bPMGDB0*(\d+)', _replace_project_reference, text)
    text = re.sub(r'\bSMGDB0*(\d+)', _replace_study_reference, text)
    text = re.sub(r'\bEMGDB0*(\d+)', _replace_experiment_reference, text)

    if first_paragraph:
        text = f"<p>{_split_paragraphs(text)[0]}</p>"
    else:
        text = "\n\n".join([f"<p>{paragraph.strip()}</p>" for paragraph in _split_paragraphs(text)])

    return Markup(text)


def _replace_project_reference(m):
    base_url = request.host_url
    project_id = f"PMGDB{int(m[1]):06d}"

    return f"""<a href="{base_url}project/{project_id}">{project_id}</a>"""


def _replace_study_reference(m):
    base_url = request.host_url
    study_id = f"SMGDB{int(m[1]):08d}"

    return f"""<a href="{base_url}study/{study_id}">{study_id}</a>"""


def _replace_experiment_reference(m):
    base_url = request.host_url
    experiment_id = f"EMGDB{int(m[1]):09d}"

    return f"""<a href="{base_url}experiment/{experiment_id}">{experiment_id}</a>"""


def _split_paragraphs(text):
    return re.sub(r"\r\n?", "\n", text).split("\n\n")
