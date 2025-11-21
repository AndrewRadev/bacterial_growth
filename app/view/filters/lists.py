from markupsafe import Markup, escape


def flatten(collection):
    return [item for sublist in collection for item in sublist]


def join_tag(collection, tag_name):
    text = f"<{tag_name}>"
    text += f"</{tag_name}>, <{tag_name}>".join([escape(item) for item in collection])
    text += f"</{tag_name}>"

    return Markup(text)
