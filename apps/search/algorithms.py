from collections import deque
from apps.relationships.models import Relationship

def bfs_relationship_path(start, end):
    queue = deque([[start]])
    visited = set()
    while queue:
        path = queue.popleft()
        current = path[-1]
        if current == end:
            return path
        if current in visited:
            continue
        visited.add(current)
        neighbors = [rel.related_person for rel in Relationship.objects.filter(person=current)]
        for n in neighbors:
            queue.append(path + [n])
    return None


def dfs_ancestors(person, visited=None):
    if visited is None:
        visited = set()
    parents = Relationship.objects.filter(person=person, relationship_type="child")
    for rel in parents:
        parent = rel.related_person
        if parent not in visited:
            visited.add(parent)
            dfs_ancestors(parent, visited)
    return visited


def dfs_descendants(person, visited=None):
    if visited is None:
        visited = set()
    children = Relationship.objects.filter(person=person, relationship_type="parent")
    for rel in children:
        child = rel.related_person
        if child not in visited:
            visited.add(child)
            dfs_descendants(child, visited)
    return visited
