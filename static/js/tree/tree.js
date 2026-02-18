// ===============================
// Config: set these from Django template
// ===============================
const FAMILY_ID = window.FAMILY_ID || 1; // Example default
const ROOT_ID = window.ROOT_ID || 17;    // Example default

// ===============================
// Fetch family tree JSON from backend
// ===============================
async function fetchFamilyTree(showDeceased = true) {
    const apiUrl = `/families/${FAMILY_ID}/tree/api/${window.ROOT_ID}/?show_deceased=${showDeceased}`;
    console.log("Fetching URL:", apiUrl);  // 👈 ADD THIS

    const res = await fetch(apiUrl);
    console.log("Response status:", res.status); // 👈 ADD THIS

    if (!res.ok) throw new Error(`Failed to fetch tree: ${res.status}`);
    return res.json();
}

// ===============================
// Convert JSON tree to Cytoscape elements
// ===============================
function jsonToCytoscapeElements(json) {
    const elements = [];
    const visited = new Set();

    function traverse(node) {
        if (!node || visited.has(node.id)) return;
        visited.add(node.id);

        // Add node
        elements.push({
            data: {
                id: node.id,
                label: node.name,
                gender: node.gender,
                is_living: node.is_living,
                image: node.photo || null
            }
        });

        // Parents
        if (node.parents) {
            node.parents.forEach(parent => {
                traverse(parent);
                elements.push({
                    data: { source: parent.id, target: node.id, type: 'parent' }
                });
            });
        }

        // Children
        if (node.children) {
            node.children.forEach(child => {
                traverse(child);
                elements.push({
                    data: { source: node.id, target: child.id, type: 'child' }
                });
            });
        }

        // Spouses
        if (node.spouses) {
            node.spouses.forEach(spouse => {
                traverse(spouse);
                elements.push({
                    data: { source: node.id, target: spouse.id, type: 'spouse' }
                });
            });
        }
    }

    traverse(json);
    return elements;
}

// ===============================
// Render tree with Cytoscape
// ===============================
let cy; // Cytoscape instance

async function renderFamilyTree(showDeceased = true) {
    const treeJson = await fetchFamilyTree(showDeceased);
    const elements = jsonToCytoscapeElements(treeJson);

    if (!cy) {
        cy = cytoscape({
            container: document.getElementById('familyTreeContainer'),
            elements: elements,
            style: [
                {
                    selector: 'node',
                    style: {
                        'shape': 'ellipse',
                        'width': 80,
                        'height': 80,
                        'background-color': ele => {
                            if (!ele.data('is_living')) return '#999';
                            return ele.data('gender') === 'male' ? '#60a5fa'
                                : ele.data('gender') === 'female' ? '#f87171'
                                : '#9e9e9e';
                        },
                        'background-image': ele => ele.data('image') || null,
                        'background-fit': 'cover',
                        'border-color': '#333',
                        'border-width': 2,
                        'label': 'data(label)',
                        'text-valign': 'bottom',
                        'text-halign': 'center',
                        'font-size': 12,
                        'text-wrap': 'wrap',
                        'text-max-width': 70
                    }
                },
                {
                    selector: 'edge',
                    style: {
                        'width': 2,
                        'line-color': ele => {
                            if (ele.data('type') === 'spouse') return '#ffa500';
                            return '#999';
                        },
                        'curve-style': 'bezier'
                    }
                }
            ],
            layout: { name: 'dagre', rankDir: 'TB', nodeSep: 150, edgeSep: 50 },
            zoomingEnabled: true,
            panningEnabled: true
        });
    } else {
        cy.elements().remove();
        cy.add(elements);
        cy.layout({ name: 'dagre', rankDir: 'TB', nodeSep: 150, edgeSep: 50 }).run();
    }

    // Node click: show side panel
    cy.on('tap', 'node', function(evt) {
        const data = evt.target.data();
        const panel = document.getElementById('nodeDetails');
        document.getElementById('detailName').textContent = data.label;
        document.getElementById('detailGender').textContent = data.gender;
        document.getElementById('detailLiving').textContent = data.is_living ? 'Living' : 'Deceased';
        document.getElementById('detailPhoto').src = data.image || '/static/images/default_profile.jpg';
        panel.style.display = 'block';
    });
}

// ===============================
// Toggle deceased checkbox
// ===============================
document.getElementById('toggleDeceased').addEventListener('change', (e) => {
    renderFamilyTree(e.target.checked);
});

// ===============================
// Initial render
// ===============================
renderFamilyTree(true);
