import nltk

# ----- luisa

def reading():
    with open('document.txt', 'r') as f:
        userinput = f.read()


def ie_processing():
    sentences = nltk.sent_tokenize(userinput)
    token_sentences = [nltk.word_tokenize(sent) for sent in sentences]
    tagged_sentences = [nltk.pos_tag(sent) for sent in sentences]
    chunked_sentences = nltk.ne_chunk(tagged_sentences)


#  ----- rachel


