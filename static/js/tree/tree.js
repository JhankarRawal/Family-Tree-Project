// Get canvas and context
const canvas = document.getElementById("treeCanvas");
const context = canvas.getContext("2d");

// Zoom behavior
const zoom = d3.zoom()
  .scaleExtent([0.2, 2])
  .on("zoom", (event) => draw(event.transform));

d3.select(canvas).call(zoom);

let treeData;

// Fetch tree data from Django API
function fetchTree(showDeceased = true) {
  const apiUrl = `/families/${FAMILY_ID}/tree/api/${ROOT_ID}/?show_deceased=${showDeceased}`;

  fetch(apiUrl)
    .then(res => {
      if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
      return res.json();
    })
    .then(data => {
      treeData = d3.hierarchy(data);
      draw(d3.zoomIdentity);  // initial draw with identity transform
    })
    .catch(err => console.error("Error fetching tree data:", err));
}

// Draw tree on canvas
function draw(transform) {
  if (!treeData) return;

  context.save();
  context.clearRect(0, 0, canvas.width, canvas.height);
  context.translate(transform.x, transform.y);
  context.scale(transform.k, transform.k);

  // Create tree layout
  const treeLayout = d3.tree().nodeSize([80, 180]);
  treeLayout(treeData);

  // Draw links
  treeData.links().forEach(link => {
    context.beginPath();
    context.moveTo(link.source.x, link.source.y);
    context.lineTo(link.target.x, link.target.y);
    context.strokeStyle = "#999";
    context.lineWidth = 2;
    context.stroke();
  });

  // Draw nodes
  treeData.descendants().forEach(d => {
    context.beginPath();
    context.fillStyle = d.data.gender === "male" ? "#4A90E2" :
                        d.data.gender === "female" ? "#E91E63" :
                        "#9E9E9E";  // unknown or other
    context.arc(d.x, d.y, 14, 0, 2 * Math.PI);
    context.fill();

    // Add label
    context.fillStyle = "#000";
    context.font = "12px sans-serif";
    context.textAlign = "center";
    context.fillText(d.data.name, d.x, d.y - 20);
  });

  context.restore();
}

// Toggle deceased members
document.getElementById("toggleDeceased").addEventListener("change", e => {
  fetchTree(e.target.checked);
});

// Fetch initial tree
fetchTree();
