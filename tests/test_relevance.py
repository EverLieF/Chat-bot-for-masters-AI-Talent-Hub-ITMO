from app.search.retriever import is_relevant

def test_relevance_filter():
    assert is_relevant("Сколько ECTS на AI Product?")
    assert not is_relevant("Какая погода в СПб завтра?")