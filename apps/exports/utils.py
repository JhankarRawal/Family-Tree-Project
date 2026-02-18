def generate_gedcom(family):
    lines = [
        "0 HEAD",
        "1 SOUR FamilyTreeApp",
        "1 GEDC",
        "2 VERS 5.5.1",
        "1 CHAR UTF-8"
    ]

    for person in family.persons.all():
        lines += [
            f"0 @I{person.id}@ INDI",
            f"1 NAME {person.first_name} /{person.last_name}/",
            f"1 SEX {person.gender[:1].upper()}",
        ]

        if person.birth_date:
            lines += ["1 BIRT", f"2 DATE {person.birth_date}"]

        if person.death_date:
            lines += ["1 DEAT", f"2 DATE {person.death_date}"]

    lines.append("0 TRLR")
    return "\n".join(lines)
