from apps.relationships.models import Relationship

def build_tree(person, depth=0, max_depth=3, show_deceased=True):
    if depth > max_depth:
        return {"id": person.id, "has_more": True}

    children_rels = Relationship.objects.filter(
        person=person,
        relationship_type="parent"
    ).select_related("related_person")

    children = []
    for rel in children_rels:
        child = rel.related_person
        if not show_deceased and not child.is_living:
            continue

        children.append(build_tree(child, depth + 1, max_depth, show_deceased))

    return {
        "id": person.id,
        "name": str(person),
        "gender": person.gender,
        "is_living": person.is_living,
        "children": children,
        "has_more": len(children) == max_depth
    }
