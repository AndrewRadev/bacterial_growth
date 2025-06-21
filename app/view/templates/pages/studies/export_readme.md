# Data export of study {{ study.publicId }}

## {{ study.name }}

{{ study.description }}

## Exported experiments

{% for experiment in study.experiments: -%}
- {{ experiment.name }}: {{ experiment.description }}
{% endfor %}
{% if study.url: %}
## More information

URL: <{{ study.url }}>
{% endif %}
