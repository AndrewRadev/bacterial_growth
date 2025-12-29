from markupsafe import Markup, escape


def flatten(collection):
    return [item for sublist in collection for item in sublist]


def join_tag(collection, tag_name):
    text = f"<{tag_name}>"
    text += f"</{tag_name}>, <{tag_name}>".join([escape(item) for item in collection])
    text += f"</{tag_name}>"

    return Markup(text)


def stable_groupby(collection, attribute):
    """
    Similar to the built-in "groupby" filter, but expects a sorted list and
    maintains its ordering.
    """
    groups = {}
    for item in collection:
        key = getattr(item, attribute)
        if key not in groups:
            groups[key] = []
        groups[key].append(item)

    return groups.items()
