import json
from openai import OpenAI
import textstat
from wordfreq import tokenize
from collections import Counter
from app.shared.models import Result
from app.shared.config import get_logger, OPEN_AI_KEY

client = OpenAI(api_key=OPEN_AI_KEY)
_logger = get_logger("DOC PROCESSING")

def _summarize_text(text, model="gpt-4"):
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "Give a one line summary of the user's provided text"},
            {"role": "user", "content": f"Summarize the following text:\n\n{text}"}
        ],
        temperature=0.3,
        max_tokens=50,
    )

    return response.choices[0].message.content


def _get_word_frequencies(text):
    tokens = tokenize(text, 'en')  # English tokenizer
    return json.dumps(Counter(tokens))


def _get_text_stats(text):
    result = Result()
    result.total_words = textstat.lexicon_count(text)
    result.total_chars = textstat.char_count(text, ignore_spaces=True)
    result.total_lines = textstat.sentence_count(text)
    result.most_frequent_words = _get_word_frequencies(text)
    return result


def process_text(text):
    try:
        result = _get_text_stats(text)
    except Exception as ex:
        _logger.error(f"Error getting text stats for file - {ex}")
        raise

    try:
        result.summary = _summarize_text(text)
    except Exception as ex:
        print(f"Error: summarization not supported: - {ex}")
        result.summary = "ERROR: NOT SUPPORTED"

    return result
