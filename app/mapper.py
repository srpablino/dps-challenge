import json
from datetime import timedelta, datetime

import config
from models import Process, ResultOut


def mapping(rows):
    if rows:
        return [Process(id=x[0], status=x[1], created_at=x[2], number_of_files=x[3], completed_at=x[4]) for x in rows]
    return []


def _merge_frequent_words(merged: dict, words: dict):
    words = {x:v+merged[x] if x in merged else v for x,v in words.items()}
    merged.update(words)
    return dict(sorted(merged.items(), key=lambda item: item[1], reverse=True))


def mapping_results(results, process):
    out_result = ResultOut()
    out_result.progress.processed_files = len(results)
    out_result.progress.total_files = process.number_of_files
    out_result.progress.percentage = len(results) / process.number_of_files

    if process.completed_at:
        out_result.estimated_completion = process.completed_at
    else:
        time_taken_until = (datetime.utcnow().timestamp() - process.created_at.timestamp())\
                           / out_result.progress.percentage
        out_result.estimated_completion = process.created_at + timedelta(seconds=time_taken_until)

    out_result.status = process.status
    out_result.process_id = process.id
    out_result.started_at = process.created_at

    for r in results:
        out_result.results.total_lines+=r["total_lines"]
        out_result.results.total_chars+=r["total_chars"]
        out_result.results.total_words+=r["total_words"]
        out_result.results.files_processed.append(r["file_name"])
        out_result.results.files_summary.append(r["summary"])
        out_result.results.most_frequent_words = _merge_frequent_words(out_result.results.most_frequent_words,
                                                                      json.loads(r["most_frequent_words"]))

    if config.STOP_WORDS:
        out_result.results.most_frequent_words = dict((x,v) for x,v in out_result.results.most_frequent_words.items() if
                                                  x not in config.STOP_WORDS)
    if config.TOP_NUMBER_FREQUENT_WORDS:
        out_result.results.most_frequent_words = dict(list(out_result.results.most_frequent_words.items())[
                                                 :min(config.TOP_NUMBER_FREQUENT_WORDS,
                                                      len(out_result.results.most_frequent_words))])

    return out_result.dict()