function sortTable(columnIndex) {
    const table = document.getElementById("usersTable");
    const rows = Array.from(table.rows).slice(1);
    const asc = table.dataset.sortOrder !== "asc";

    rows.sort((a, b) => {
        const valA = a.cells[columnIndex].innerText.toLowerCase();
        const valB = b.cells[columnIndex].innerText.toLowerCase();
        return asc ? valA.localeCompare(valB) : valB.localeCompare(valA);
    });

    rows.forEach(row => table.appendChild(row));
    table.dataset.sortOrder = asc ? "asc" : "desc";
}
