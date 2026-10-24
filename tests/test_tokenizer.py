from uncanny.tokenizer import split_sentences


def test_basic_split():
    text = "Hello world. This is a test. And another one."
    result = split_sentences(text)
    assert len(result) == 3
    assert result[0][0] == "Hello world."
    assert result[1][0] == "This is a test."
    assert result[2][0] == "And another one."


def test_abbreviations():
    text = "Dr. Smith went to Washington. He arrived Tuesday."
    result = split_sentences(text)
    assert len(result) == 2


def test_empty():
    assert split_sentences("") == []
    assert split_sentences("   ") == []


def test_single_sentence():
    result = split_sentences("Just one sentence here")
    assert len(result) == 1


def test_offsets():
    text = "First. Second."
    result = split_sentences(text)
    for sent_text, start, end in result:
        assert text[start:end] == sent_text


def test_pdf_whitespace_preserves_sentence_offsets():
    result = split_sentences("First sentence.\n\fSecond sentence.")
    assert result == [("First sentence.", 0, 15), ("Second sentence.", 16, 32)]
