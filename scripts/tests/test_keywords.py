from keywords import KEYWORDS_EN, KEYWORDS_FR, ALL_KEYWORDS

def test_keywords_en_not_empty():
    assert len(KEYWORDS_EN) >= 9

def test_keywords_fr_not_empty():
    assert len(KEYWORDS_FR) >= 8

def test_all_keywords_combines_both():
    assert set(KEYWORDS_EN).issubset(set(ALL_KEYWORDS))
    assert set(KEYWORDS_FR).issubset(set(ALL_KEYWORDS))

def test_no_duplicate_keywords():
    assert len(ALL_KEYWORDS) == len(set(ALL_KEYWORDS))
