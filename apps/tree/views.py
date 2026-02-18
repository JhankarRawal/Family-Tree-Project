from django.views.generic import TemplateView, View
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from apps.persons.models import Person
from apps.families.models import Family
from apps.relationships.models import Relationship
# from .views import build_tree

class FamilyTreeView(TemplateView):
    template_name = "tree/tree_view.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        family_id = self.kwargs["family_id"]
        root = Person.objects.filter(family_id=family_id).first()
        context["family_id"] = family_id
        context["root_person"] = root
        return context


class CenteredTreeView(FamilyTreeView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["root_person"] = get_object_or_404(
            Person, id=self.kwargs["person_id"]
        )
        return context


class TreeDataAPIView(View):
    """
    Returns the full family tree for a given family.
    Centered tree: parents above, children below, spouses beside.
    Handles all generations recursively.
    """

    def get(self, request, family_id, person_id=None):
        show_deceased = request.GET.get("show_deceased", "true") == "true"

        # Fetch family & persons
        family = get_object_or_404(Family, id=family_id)
        persons = Person.objects.filter(family=family)
        person_map = {p.id: p for p in persons}

        # Fetch all relationships
        relationships = Relationship.objects.filter(family=family)

        # Build relationship maps
        parent_children_map = {}
        child_parents_map = {}
        spouse_map = {}

        for rel in relationships:
            if rel.relationship_type == "parent":
                parent_children_map.setdefault(rel.person_id, []).append(rel.related_person_id)
                child_parents_map.setdefault(rel.related_person_id, []).append(rel.person_id)
            elif rel.relationship_type == "child":
                child_parents_map.setdefault(rel.person_id, []).append(rel.related_person_id)
                parent_children_map.setdefault(rel.related_person_id, []).append(rel.person_id)
            elif rel.relationship_type == "spouse":
                spouse_map.setdefault(rel.person_id, []).append(rel.related_person_id)
                spouse_map.setdefault(rel.related_person_id, []).append(rel.person_id)

        # Recursive tree builder
        def build_tree(person_id, visited=None):
            if visited is None:
                visited = set()
            if person_id in visited:
                return None
            visited.add(person_id)

            person = person_map[person_id]

            if not show_deceased and not person.is_living:
                return None

            node = {
                "id": person.id,
                "name": str(person),
                "gender": person.gender,
                "photo": person.photo.url if person.photo else None,
                "is_living": person.is_living,
                "parents": [],
                "spouses": [],
                "children": []
            }

            # Parents
            for pid in child_parents_map.get(person_id, []):
                parent_node = build_tree(pid, visited.copy())
                if parent_node:
                    node["parents"].append(parent_node)

            # Spouses
            for sid in spouse_map.get(person_id, []):
                spouse_node = build_tree(sid, visited.copy())
                if spouse_node:
                    node["spouses"].append(spouse_node)

            # Children
            for cid in parent_children_map.get(person_id, []):
                child_node = build_tree(cid, visited.copy())
                if child_node:
                    node["children"].append(child_node)

            return node

        # If a specific person is requested
        if person_id:
            if person_id not in person_map:
                return JsonResponse({"error": "Person not found"}, status=404)
            tree = build_tree(person_id)
            return JsonResponse(tree, safe=False)

        # Full family tree: find all roots (persons without parents)
        root_ids = [p.id for p in persons if p.id not in child_parents_map]
        forest = [build_tree(rid) for rid in root_ids if build_tree(rid) is not None]

        # Wrap in a dummy root for D3
        tree = {"name": "Family Tree", "children": forest}

        return JsonResponse(tree, safe=False)

