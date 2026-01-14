from django.core.cache import cache
from django.db.models import Q, Case, When
from rapidfuzz import fuzz
from ..models import Task

CACHE_TIMEOUT = 60 * 5   # 5 minutes
MAX_CANDIDATES = 300
THRESHOLD = 30
TASK_SEARCH_VERSION_KEY = "task_search_version"


def search_tasks(tasks, query):
    query = query.strip().lower()
    version = cache.get_or_set("task_search_version", 1)
    cache_key = f"task_search:{version}:{query}"

    # Check cache
    cached_ids = cache.get(cache_key)
    if cached_ids is not None:
        return (
            Task.objects
            .filter(id__in=cached_ids)
            .order_by(
                Case(
                    *[When(id=pk, then=pos) for pos, pk in enumerate(cached_ids)]
                )
            )
        )
    # DB pre-filter
    qs = (
        tasks
        .filter(
            Q(name__icontains=query[:2]) |
            Q(description__icontains=query[:4])
        )
        .only("id", "name", "description")
        [:MAX_CANDIDATES]
    )
    # Fuzzy scoring
    scored = []
    for task in qs:
        score = max(
            fuzz.partial_ratio(query, task.name.lower()),
            fuzz.partial_ratio(query, (task.description or "").lower()),
        )
        if score >= THRESHOLD:
            scored.append((score, task.id))

    # Sort & extract IDs
    scored.sort(reverse=True, key=lambda x: x[0])
    ordered_ids = [task_id for _, task_id in scored]

    # Cache result
    cache.set(cache_key, ordered_ids, CACHE_TIMEOUT)

    # Return QuerySet
    return (
        Task.objects
        .filter(id__in=ordered_ids)
        .order_by(
            Case(
                *[When(id=pk, then=pos) for pos, pk in enumerate(ordered_ids)]
            )
        )
    )

def bump_task_search_version():
    cache.set(
        TASK_SEARCH_VERSION_KEY,
        cache.get_or_set(TASK_SEARCH_VERSION_KEY, 0) + 1
    )

def get_task_search_version():
    return cache.get("task_search_version", 0)