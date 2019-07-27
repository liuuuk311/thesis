def get_hashtags(text):
    return get_tags(text, '#')

def get_mentions(text):
    return get_tags(text, '@')

def get_tags(text, symbol):
    text = text.split()
    tags = []
    [tags.append(w) if symbol in w and len(w) > 1 else 0 for w in text]
    return tags

def clean(text):
    text = text.replace('.', '. ')
    text = text.replace(',', ', ')
    text = text.replace('  ', ' ')
    return text

if __name__ == "__main__":
    print(get_hashtags('prova #abc #def prova #'))
    print(get_mentions('prova #abc #def prova @abc'))