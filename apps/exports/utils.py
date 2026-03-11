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


from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import matplotlib.pyplot as plt
from apps.persons.models import Person
import networkx as nx
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader

def generate_family_tree_image(family):
    """
    Generates a family tree diagram as an image.
    Returns a BytesIO buffer containing PNG image.
    """
    members = Person.objects.filter(family=family)
    G = nx.DiGraph()

    # Add nodes
    for person in members:
        G.add_node(person.id, label=f"{person.first_name} {person.last_name}")

    # Add edges for parent-child
    for person in members:
        for rel in person.relationships_from.filter(relationship_type="parent"):
            G.add_edge(person.id, rel.related_person.id)

    # Draw graph
    pos = nx.spring_layout(G)
    labels = nx.get_node_attributes(G, 'label')

    plt.figure(figsize=(12, 8))
    nx.draw(G, pos, labels=labels, with_labels=True, node_color='lightblue', node_size=3000, font_size=10, arrows=True)
    
    buf = BytesIO()
    plt.savefig(buf, format='PNG', bbox_inches='tight')
    plt.close()
    buf.seek(0)
    return buf

def generate_family_tree_pdf(family):
    """
    Generate a PDF containing the family tree diagram image.
    """
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Title
    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawCentredString(width / 2, height - 50, f"Family Tree: {family.name}")

    # Generate tree image
    tree_img_buf = generate_family_tree_image(family)
    tree_img = ImageReader(tree_img_buf)

    # Embed image
    img_width = width - 100
    img_height = height - 150
    pdf.drawImage(tree_img, 50, 50, width=img_width, height=img_height, preserveAspectRatio=True, anchor='c')

    pdf.showPage()
    pdf.save()
    buffer.seek(0)
    return buffer.getvalue()
