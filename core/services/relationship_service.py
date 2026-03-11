# core/services/relationship_service.py
from collections import deque
from apps.relationships.models import Relationship

class RelationshipEngine:

    def __init__(self, family_id):
        self.family_id = family_id
        self.graph = {}  # adjacency list

    def build_graph(self):
        """Build adjacency list for the family relationships."""
        self.graph = {}
        rels = Relationship.objects.filter(family_id=self.family_id)

        for rel in rels:
            p1 = rel.person.id
            p2 = rel.related_person.id

            if rel.relationship_type == 'parent':
                # Parent → Child
                self.graph.setdefault(p1, []).append({'id': p2, 'type': 'parent->child'})
                self.graph.setdefault(p2, []).append({'id': p1, 'type': 'child->parent'})
            elif rel.relationship_type == 'spouse':
                # Spouse
                self.graph.setdefault(p1, []).append({'id': p2, 'type': 'spouse->spouse'})
                self.graph.setdefault(p2, []).append({'id': p1, 'type': 'spouse->spouse'})

    def find_relationship(self, person_a_id, person_b_id, max_depth=10):
        """BFS to find shortest path of relationships between two people."""
        queue = deque([(person_a_id, [])])
        visited = set()

        while queue:
            current, path = queue.popleft()
            if current in visited:
                continue
            visited.add(current)

            if current == person_b_id:
                return path

            for neighbor in self.graph.get(current, []):
                queue.append((neighbor['id'], path + [neighbor['type']]))

        return None  # No relation
    

    def interpret_path(self, path):
        """Interpret relationship path to human-readable format."""
        if not path:
            return "Same person"

        # Convert edge types into steps
        steps = []
        for step in path:
            if step == 'parent->child':
                steps.append('child')
            elif step == 'child->parent':
                steps.append('parent')
            elif step == 'spouse->spouse':
                steps.append('spouse')

        # Track generations and spouse indices
        gen_steps = [s for s in steps if s in ('parent', 'child')]
        spouse_positions = [i for i,s in enumerate(steps) if s == 'spouse']

        # -----------------------
        # Direct spouse
        # -----------------------
        if not gen_steps and spouse_positions:
            return "spouse"

        # -----------------------
        # Ancestors / Descendants
        # -----------------------
        parent_count = gen_steps.count('parent')
        child_count = gen_steps.count('child')
        if parent_count > 0 and child_count == 0:
            return ("great-"*(parent_count-2) + "grandparent") if parent_count > 2 else \
                   "grandparent" if parent_count == 2 else "parent"
        if child_count > 0 and parent_count == 0:
            return ("great-"*(child_count-2) + "grandchild") if child_count > 2 else \
                   "grandchild" if child_count == 2 else "child"

        # -----------------------
        # Siblings
        # -----------------------
        if gen_steps == ['child','parent']:
            if spouse_positions:
                return "sibling-in-law"
            return "sibling"

        # -----------------------
        # Uncle/Aunt / Nephew/Niece
        # -----------------------
        if gen_steps == ['child','child','parent']:
            return "uncle/aunt"
        if gen_steps == ['child','parent','parent']:
            return "nephew/niece"

        # -----------------------
        a_up = 0
        b_up = 0
        for step in gen_steps:
            if step == 'parent':
                if a_up <= b_up:
                    a_up += 1
                else:
                    b_up += 1
            elif step == 'child':
                if a_up > b_up:
                    b_up += 1
                else:
                    a_up += 1

        cousin_level = min(a_up, b_up) - 1
        removed = abs(a_up - b_up)
        if cousin_level >= 1:
            cousin_names = ["first","second","third","fourth","fifth","sixth","seventh","eighth","ninth"]
            name = cousin_names[cousin_level-1] if cousin_level <= len(cousin_names) else f"{cousin_level}th"
            result = f"{name} cousin"
            if removed:
                result += f" {removed} times removed"
            if 'spouse' in steps:
                result += " (in-law)"
            return result

        # -----------------------
        # General in-law detection via spouse in path
        # -----------------------
        if spouse_positions:
            # Parent-in-law / Child-in-law
            if gen_steps[:2] == ['parent','spouse']:
                return "parent-in-law"
            if gen_steps[:2] == ['child','spouse']:
                return "child-in-law"
            # Cousin-in-law handled above
            # Sibling-in-law handled above
            # Spouse of sibling
            if gen_steps[:3] == ['child','parent','spouse']:
                return "brother-in-law / sister-in-law"

        # -----------------------
        # Fallback
        # -----------------------
        return " -> ".join(steps)