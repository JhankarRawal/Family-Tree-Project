// Select SVG container
const svg = d3.select("#familyTreeSvg");
const g = svg.append("g");

// Zoom and pan
svg.call(
    d3.zoom()
        .scaleExtent([0.2, 3])
        .on("zoom", (event) => {
            g.attr("transform", event.transform);
        })
);

let rootData;

// These will be passed from Django template


// Fetch tree from API
function fetchTree(showDeceased = true) {
    const apiUrl = `/families/${FAMILY_ID}/tree/api/${ROOT_ID}/?show_deceased=${showDeceased}`;

    fetch(apiUrl)
        .then((res) => {
            if (!res.ok) throw new Error(`HTTP error! Status: ${res.status}`);
            return res.json();
        })
        .then((data) => {
            rootData = d3.hierarchy(data);
            renderTree(rootData);
        })
        .catch((err) => console.error("Error fetching tree:", err));
}

// Render tree
function renderTree(root) {
    // Clear previous nodes and links
    g.selectAll("*").remove();

    const treeLayout = d3.tree().nodeSize([150, 180]); // Adjust spacing if needed
    treeLayout(root);

    // Draw links
    g.selectAll("line.link")
        .data(root.links())
        .enter()
        .append("line")
        .classed("link", true)
        .attr("x1", (d) => d.source.x)
        .attr("y1", (d) => d.source.y)
        .attr("x2", (d) => d.target.x)
        .attr("y2", (d) => d.target.y)
        .attr("stroke", "#999")
        .attr("stroke-width", 2);

    // Draw nodes
    const node = g.selectAll("g.node")
        .data(root.descendants())
        .enter()
        .append("g")
        .classed("node", true)
        .attr("transform", (d) => `translate(${d.x},${d.y})`);

    // Circle for each person
    node.append("circle")
        .attr("r", 25)
        .attr("fill", (d) =>
            d.data.gender === "male" ? "#60a5fa" :
            d.data.gender === "female" ? "#f87171" :
            "#9e9e9e"
        )
        .attr("stroke", "#333")
        .attr("stroke-width", 2);

    // Name label
    node.append("text")
        .attr("y", -35)
        .attr("text-anchor", "middle")
        .attr("font-size", "14px")
        .text((d) => d.data.name);
}

// Toggle deceased checkbox
document.getElementById("toggleDeceased").addEventListener("change", (e) => {
    fetchTree(e.target.checked);
});

// Initial render
fetchTree();
