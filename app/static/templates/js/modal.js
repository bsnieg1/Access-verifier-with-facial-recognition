function openAddUser() {
    const modal = document.getElementById("modal");

    modal.innerHTML = `
        <div style="
            background: rgba(255,255,255,0.85);
            backdrop-filter: blur(12px);
            border-radius: 14px;
            padding: 24px;
            min-width: 320px;
            box-shadow: 0 20px 40px rgba(0,0,0,.3);
        ">
            <h3>Nowy użytkownik</h3>

            <form method="POST" action="/admin/users/new">
                <input
                    type="text"
                    name="name"
                    placeholder="Imię i nazwisko"
                    required
                >
                <div style="display:flex; gap:10px; margin-top:12px">
                    <button type="submit">Dodaj</button>
                    <button type="button" class="secondary" onclick="closeModal()">
                        Anuluj
                    </button>
                </div>
            </form>
        </div>
    `;

    modal.style.position = "fixed";
    modal.style.inset = "0";
    modal.style.background = "rgba(0,0,0,0.5)";
    modal.style.display = "flex";
    modal.style.justifyContent = "center";
    modal.style.alignItems = "center";
}

function closeModal() {
    document.getElementById("modal").style.display = "none";
}
