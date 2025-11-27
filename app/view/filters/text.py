import re

from markupsafe import Markup, escape as html_escape
from flask import url_for, request

from jinja2.utils import urlize


def format_text(text, first_paragraph=False, p_class=''):
    if not text:
        return ''

    text = text.strip()
    text = urlize(text, target="_blank", rel="noreferrer nofollow")

    text = re.sub(r'\bPMGDB0*(\d+)', _replace_project_reference, text)
    text = re.sub(r'\bSMGDB0*(\d+)', _replace_study_reference, text)
    text = re.sub(r'\bEMGDB0*(\d+)', _replace_experiment_reference, text)

    if len(p_class):
        class_attr = f" class=\"{p_class}\""
    else:
        class_attr = ""

    if first_paragraph:
        text = f"<p{class_attr}>{_split_paragraphs(text)[0]}</p>"
    else:
        text = "\n\n".join([
            f"<p{class_attr}>{paragraph.strip()}</p>"
            for paragraph in _split_paragraphs(text)
        ])

    return Markup(text)

def highlight(text, words):
    if len(words) == 0:
        return text

    search_pattern = '(' + '|'.join([re.escape(w) for w in words]) + ')'
    regex = re.compile(search_pattern, re.IGNORECASE)

    highlighted_text = re.sub(
        regex,
        lambda match: f'<span class="highlight">{html_escape(match[1])}</span>',
        html_escape(text),
    )

    return Markup(highlighted_text)

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
