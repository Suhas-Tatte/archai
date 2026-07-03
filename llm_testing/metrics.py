"""
metrics.py

Utility functions for evaluating LLM retrieval performance.
"""


def precision(expected, predicted):
    """
    Precision = Correct / Returned
    """

    if len(predicted) == 0:
        return 0.0

    correct = expected.intersection(predicted)

    return len(correct) / len(predicted)


def recall(expected, predicted):
    """
    Recall = Correct / Expected
    """

    if len(expected) == 0:
        return 1.0 if len(predicted) == 0 else 0.0

    correct = expected.intersection(predicted)

    return len(correct) / len(expected)


def f1_score(expected, predicted):
    """
    Harmonic mean of Precision and Recall.
    """

    p = precision(expected, predicted)
    r = recall(expected, predicted)

    if p + r == 0:
        return 0.0

    return 2 * p * r / (p + r)


def exact_match(expected, predicted):
    """
    True only if both sets are identical.
    """

    return expected == predicted


def count_match(expected, predicted):
    """
    True if number of retrieved records matches.
    """

    return len(expected) == len(predicted)


def missing_sites(expected, predicted):
    """
    Sites expected but not returned.
    """

    return sorted(expected - predicted)


def extra_sites(expected, predicted):
    """
    Sites returned but not expected.
    """

    return sorted(predicted - expected)


def common_sites(expected, predicted):
    """
    Correctly retrieved sites.
    """

    return sorted(expected.intersection(predicted))