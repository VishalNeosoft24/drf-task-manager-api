from rapidfuzz import fuzz

def calculate_task_score(task, query):
    score = 0
    query = query.lower()

    # Task ID match (task #67)
    if str(task.id) in query:
        score += 100

    # Task name
    score += fuzz.partial_ratio(query, task.name.lower()) * 0.7

    # Description
    if task.description:
        score += fuzz.partial_ratio(query, task.description.lower()) * 0.3

    # Project name
    if task.project:
        score += fuzz.partial_ratio(query, task.project.name.lower()) * 0.4

    return round(score, 2)
