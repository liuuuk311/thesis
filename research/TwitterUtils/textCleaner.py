import re

def clean(text):
    text = " ".join(text.splitlines())

    text = text.replace('# ', '#')
    text = text.replace('@ ', '@')
    text = re.sub(r'https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&\/=]*)', '', text)
    text = re.sub(r'\w*\.\w*\.\w*\/\w*', '', text)
    text = re.sub(r'\s\.+\s','', text)
    text = text.replace('"', '')
    text = text.replace('…', '')
    text = text.replace('“', '')
    text = text.replace('  ', ' ')

    return text

if __name__ == "__main__":
    print(clean('test\ntest'))
