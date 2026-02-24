from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.views import View
from core.services.relationship_service import RelationshipEngine
from apps.activitylog.utils import log_activity
from apps.families.models import Family
from apps.persons.models import Person
from .forms import RelationshipForm
from .models import Relationship
from django.db import IntegrityError


# Helper to reuse between parent/child/spouse
class BaseAddRelationshipView(View):
    relationship_type = None  # 'parent', 'child', 'spouse'

    def get(self, request, family_id, person_id):
        family = get_object_or_404(Family, id=family_id)
        person = get_object_or_404(Person, id=person_id, family=family)

        # Exclude the person itself
        other_persons = family.persons.exclude(id=person.id)

        # For spouse: only opposite gender
        if self.relationship_type == "spouse":
            if person.gender == "male":
                other_persons = other_persons.filter(gender="female")
            elif person.gender == "female":
                other_persons = other_persons.filter(gender="male")
            # 'other' gender can see all

        return render(request, "relationships/add_relationship.html", {
            "family": family,
            "person": person,
            "relationship_type": self.relationship_type,
            "other_persons": other_persons,
        })

    def post(self, request, family_id, person_id):
        family = get_object_or_404(Family, id=family_id)
        person = get_object_or_404(Person, id=person_id, family=family)
        related_person_id = request.POST.get("related_person")
        related_person = get_object_or_404(Person, id=related_person_id, family=family)

        # Helper: check for circular ancestry
        def is_ancestor(possible_ancestor, descendant):
            visited = set()
            queue = [descendant]
            while queue:
                current = queue.pop()
                if current == possible_ancestor:
                    return True
                if current in visited:
                    continue
                visited.add(current)
                parents = Relationship.objects.filter(
                    person=current, relationship_type='child'
                ).values_list('related_person', flat=True)
                queue.extend(Person.objects.filter(id__in=parents))
            return False

        # Helper: safely create relationship
        def safe_create(person1, person2, r_type):
            try:
                Relationship.objects.create(
                    family=family,
                    person=person1,
                    related_person=person2,
                    relationship_type=r_type,
                    created_by=request.user
                )
            except IntegrityError:
                # Relationship already exists
                pass

        # Process relationship types
        if self.relationship_type == "parent":
            if is_ancestor(related_person, person):
                messages.error(request, f"Cannot add {related_person} as parent due to circular ancestry.")
                return redirect("families:persons:person_detail", family_id=family.id, person_id=person.id)


            safe_create(related_person, person, "parent")
            safe_create(person, related_person, "child")

        elif self.relationship_type == "child":
            if is_ancestor(person, related_person):
                messages.error(request, f"Cannot add {related_person} as child due to circular ancestry.")
                return redirect("families:persons:person_detail", family_id=family.id, person_id=person.id)



            safe_create(person, related_person, "child")
            safe_create(related_person, person, "parent")

        elif self.relationship_type == "spouse":
            # Avoid self-spouse
            if person == related_person:
                messages.error(request, "Cannot add the same person as spouse.")
                return redirect("families:persons:person_detail", family_id=family.id, person_id=person.id)



            safe_create(person, related_person, "spouse")
            safe_create(related_person, person, "spouse")
        log_activity(
            family=family,
            user=request.user,
            action_type="create",
            target_type="relationship",
            target_id=person.id,
            description=f"Created {self.relationship_type} relationship between {person} and {related_person}"
            )

        messages.success(request, f"{self.relationship_type.capitalize()} relationship added successfully.")
        return redirect("families:persons:person_detail", family_id=family.id, person_id=person.id)

    
# Specific endpoints
class AddParentView(BaseAddRelationshipView):
    relationship_type = "parent"


class AddChildView(BaseAddRelationshipView):
    relationship_type = "child"


class AddSpouseView(BaseAddRelationshipView):
    relationship_type = "spouse"


# Delete relationship
class RelationshipDeleteView(View):
    template_name = "relationships/delete_confirm.html"

    def get(self, request, family_id, rel_id):
        """Show confirmation page"""
        family = get_object_or_404(Family, id=family_id)
        relationship = get_object_or_404(Relationship, id=rel_id, family=family)

        return render(request, self.template_name, {
            "family": family,
            "relationship": relationship,
        })

    def post(self, request, family_id, rel_id):
        """Delete the relationship safely and log activity"""
        family = get_object_or_404(Family, id=family_id)
        relationship = get_object_or_404(Relationship, id=rel_id, family=family)

        # Build description for log
        desc = f"Deleted {relationship.relationship_type} relationship between {relationship.person} and {relationship.related_person}"

        # Delete the specific relationship
        Relationship.objects.filter(
            id=relationship.id
        ).delete()

        # Delete the reciprocal relationship if exists
        reciprocal_qs = Relationship.objects.filter(
            person=relationship.related_person,
            related_person=relationship.person,
        )

        # For parent/child relationships, delete only matching types
        if relationship.relationship_type in ["parent", "child"]:
            reciprocal_qs = reciprocal_qs.filter(
                relationship_type__in=["parent", "child"]
            )

        reciprocal_qs.delete()

        # Log activity
        log_activity(
            family=family,
            user=request.user,
            action_type="delete",
            target_type="relationship",
            target_id=rel_id,
            description=desc
        )

        messages.success(request, "Relationship deleted successfully.")
        return redirect("families:persons:person_detail", family_id=family.id, person_id=relationship.person.id)
    
#     return redirect(
#     "persons:person_detail",
#     pk=family.id,                     # match <int:pk>
#     person_id=relationship.person.id  # match <int:person_id>
# )

def relationship_check_page(request, family_id):
    """
    Page where user clicks two nodes to check relationship.
    """
    persons = Person.objects.filter(family_id=family_id)
    return render(request, "relationships/relationship_check.html", {
        "persons": persons,
        "family_id": family_id
    })

def relationship_check_api(request, family_id, person_a_id, person_b_id):
    engine = RelationshipEngine(family_id)
    engine.build_graph()
    path = engine.find_relationship(person_a_id, person_b_id)
    relation = engine.interpret_path(path)
    return JsonResponse({
        "person_a": person_a_id,
        "person_b": person_b_id,
        "relationship": relation
    })