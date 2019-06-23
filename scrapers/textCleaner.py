import re

def clean(text):
    # text = text.replace('# ', '#')
    # text = text.replace('@ ', '@')
    text = text.replace('pic.twitter.com', '  pic.twitter.com')
    text = re.sub(r'https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&\/=]*)', '', text)
    text = re.sub(r'(pic\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&\/=]*)', '', text)
    text = re.sub(r'\w*\.\w*\.\w*\/\w*', '', text)
    text = re.sub(r'\s\.+\s','', text)
    # text = text.replace('"', '')
    text = text.replace('…', '')
    text = text.replace('“', '')

    return text