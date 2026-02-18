function exportGEDCOM() {
    window.location.href = `/families/${FAMILY_ID}/export/gedcom/`;
}

function exportPDFWithGEDCOM() {
    exportTreePDF();
    setTimeout(exportGEDCOM, 500);
}
