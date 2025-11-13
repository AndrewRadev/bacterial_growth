from markupsafe import Markup


def flatten(collection):
    return [item for sublist in collection for item in sublist]


def join_tag(collection, tag_name):
    text = f"<{tag_name}>"
    text += f"</{tag_name}>, <{tag_name}>".join(collection)
    text += f"</{tag_name}>"

    return Markup(text)
