def person_to_node(person):
    return {
        "id": person.id,
        "name": str(person),
        "gender": person.gender,
        "is_living": person.is_living
    }
