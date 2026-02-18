async function exportTreePDF(type="pdf") {
    const svg = document.getElementById("familyTreeSvg");
    svg.classList.add("export-mode");

    const canvas = await html2canvas(svg, {
        scale: 3,
        useCORS: true,
        backgroundColor: "#fff"
    });

    const img = canvas.toDataURL("image/png");
    const { jsPDF } = window.jspdf;

    const pdf = new jsPDF("landscape", "px", "a4");
    pdf.addImage(img, "PNG", 0, 0, pdf.internal.pageSize.getWidth(), pdf.internal.pageSize.getHeight());

    sendToServer(pdf, type);

    svg.classList.remove("export-mode");
}

function sendToServer(pdf, type) {
    fetch(`/families/export/${FAMILY_ID}/${type === "zip" ? "zip" : "save-pdf"}/`, {
        method: "POST",
        headers: {
            "X-CSRFToken": csrftoken,
            "Content-Type": "application/x-www-form-urlencoded"
        },
        body: `pdf=${encodeURIComponent(pdf.output("datauristring"))}`
    });
}
