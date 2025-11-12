import humanize


def map_scientific(values):
    return ["{:.2E}".format(v) for v in values if v is not None]


def humanize_number(value):
    return humanize.intcomma(value)
