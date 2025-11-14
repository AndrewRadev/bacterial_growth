from app.view.filters import (
    lists,
    numbers,
    time,
    urls,
    text,
)


def init_template_filters(app):
    """
    Main entry point of the module.

    Imports a number of helper functions that live in ``app.view.filters`` and
    plugs them into Jinja2 as "filters".

    New template filters should be defined there and linked here, to avoid
    non-trivial (testable) code living in the "initialization" module.
    """
    app.template_filter('flatten')(lists.flatten)
    app.template_filter('join_tag')(lists.join_tag)
    app.template_filter('relative_time')(time.relative_time)
    app.template_filter('relative_date')(time.relative_date)
    app.template_filter('map_scientific')(numbers.map_scientific)
    app.template_filter('humanize_number')(numbers.humanize_number)

    app.template_filter('ncbi_url')(urls.ncbi_url)
    app.template_filter('chebi_url')(urls.chebi_url)
    app.template_filter('external_link')(urls.external_link)
    app.template_filter('help_link')(urls.help_link)

    app.template_filter('format_text')(text.format_text)

    return app
