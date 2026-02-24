# core/services/relationship_service.py

from collections import deque
from apps.persons.models import Person
from apps.relationships.models import Relationship

class RelationshipEngine:

    RELATION_MAP = {
        # Direct relationship mapping
        "parent->child": "child",
        "child->parent": "parent",
        "spouse->spouse": "spouse",
    }

    def __init__(self, family_id):
        self.family_id = family_id
        self.graph = {}  # adjacency list

    def build_graph(self):
        """
        Build a graph from all relationships in the family.
        Nodes: person.id
        Edges: {target_id: relationship_type}
        """
        self.graph = {}
        rels = Relationship.objects.filter(family_id=self.family_id)

        for rel in rels:
            # Parent → Child
            if rel.type == 'parent':
                self.graph.setdefault(rel.person1_id, []).append(
                    {'id': rel.person2_id, 'type': 'parent->child'}
                )
                self.graph.setdefault(rel.person2_id, []).append(
                    {'id': rel.person1_id, 'type': 'child->parent'}
                )
            # Spouse
            if rel.type == 'spouse':
                self.graph.setdefault(rel.person1_id, []).append(
                    {'id': rel.person2_id, 'type': 'spouse->spouse'}
                )
                self.graph.setdefault(rel.person2_id, []).append(
                    {'id': rel.person1_id, 'type': 'spouse->spouse'}
                )

    def find_relationship(self, person_a_id, person_b_id, max_depth=10):
        """
        BFS traversal from person_a_id to person_b_id
        Returns a path of relationships
        """
        queue = deque()
        queue.append((person_a_id, []))  # (current_node, path_taken)
        visited = set()

        while queue:
            current, path = queue.popleft()
            if current in visited:
                continue
            visited.add(current)

            if current == person_b_id:
                return path  # Found, return the relationship path

            for neighbor in self.graph.get(current, []):
                neighbor_id = neighbor['id']
                rel_type = neighbor['type']
                queue.append((neighbor_id, path + [rel_type]))

        return None  # No relation found

    def interpret_path(self, path):
        """
        Convert path of relationship types into human-readable string
        Example: ["parent->parent", "parent->child"] => "grandparent's child"
        """
        if not path:
            return "Same person"

        steps = []
        for step in path:
            if step == "parent->child":
                steps.append("child")
            elif step == "child->parent":
                steps.append("parent")
            elif step == "spouse->spouse":
                steps.append("spouse")
            else:
                steps.append(step)

        # Simple rule mapping
        # For example:
        if steps == ["parent"]:
            return "parent"
        if steps == ["child"]:
            return "child"
        if steps == ["parent", "parent"]:
            return "grandparent"
        if steps == ["parent", "child"]:
            return "sibling"
        if steps == ["parent", "parent", "child", "child"]:
            return "cousin"

        # fallback: join steps
        return " -> ".join(steps)