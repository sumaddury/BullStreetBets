
# algorithm/keyword_expansion.py

import os
from typing import List
import wikipedia
from nltk import word_tokenize, pos_tag, RegexpParser
from nltk.corpus import wordnet
from sentence_transformers import SentenceTransformer, util

# Ensure NLTK data installed:
# python -c "import nltk; nltk.download('wordnet omw-1.4 punkt averaged_perceptron_tagger')"

# Embedding model for semantic ranking
enb_model = SentenceTransformer('all-MiniLM-L6-v2')

# NLP chunker (noun phrases)
grammar = r"NP: {<JJ>*<NN.*>+}"
chunker = RegexpParser(grammar)

# --- Wikipedia link‑based expansion ---
def get_wikipedia_candidates(
    input_phrases: List[str],
    max_pages: int = 3,
    max_links_per_page: int = 50
) -> List[str]:
    """
    For each phrase:
      - search top `max_pages` Wikipedia titles
      - for each title, fetch page.links (first N) and page.categories
    Returns a de-duped list of candidate terms.
    """
    candidates = set()
    for phrase in input_phrases:
        try:
            titles = wikipedia.search(phrase, results=max_pages)
        except Exception:
            continue
        for title in titles:
            try:
                page = wikipedia.page(title, auto_suggest=False)
            except Exception:
                continue
            # include page title
            candidates.add(page.title)
            # include internal links
            for link in page.links[:max_links_per_page]:
                candidates.add(link)
            # include categories (strip 'Category:' prefix)
            for cat in page.categories:
                if cat.startswith('Category:'):
                    candidates.add(cat.replace('Category:', ''))
                else:
                    candidates.add(cat)
    return list(candidates)

# --- WordNet expansions (synonyms, hypernyms, hyponyms) ---
def get_wordnet_candidates(input_phrases: List[str]) -> List[str]:
    candidates = set()
    for phrase in input_phrases:
        key = phrase.replace(' ', '_')
        for syn in wordnet.synsets(key):
            for lemma in syn.lemmas():
                candidates.add(lemma.name().replace('_', ' '))
            for rel in syn.hypernyms() + syn.hyponyms():
                for lemma in rel.lemmas():
                    candidates.add(lemma.name().replace('_', ' '))
    return list(candidates)

# --- Main expansion function without LLM ---
def expand_to_keywords(
    input_phrases: List[str],
    num_keywords: int = 50
) -> List[str]:
    """
    1) Gather candidates from Wikipedia (links + categories) and WordNet.
    2) Rank by mean embedding similarity to input phrases.
    3) Return top `num_keywords`.
    """
    # 1) Seed pool
    wiki_cands = get_wikipedia_candidates(input_phrases)
    wn_cands = get_wordnet_candidates(input_phrases)
    seed = list({*wiki_cands, *wn_cands})
    if not seed:
        seed = input_phrases[:]

    # 2) Embed and rank
    phrase_embeds = enb_model.encode(input_phrases, convert_to_tensor=True)
    seed_embeds = enb_model.encode(seed, convert_to_tensor=True)
    query_vec = phrase_embeds.mean(dim=0, keepdim=True)
    cos_scores = util.cos_sim(query_vec, seed_embeds)[0]
    top_idxs = cos_scores.topk(k=min(len(seed), num_keywords)).indices.tolist()
    keywords = [seed[i] for i in top_idxs]
    return keywords

# --- Save to file ---
def save_keywords(
    keywords: List[str],
    filepath: str = "tmp/keywords.txt"
) -> None:
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w") as f:
        f.write("\n".join(keywords))

