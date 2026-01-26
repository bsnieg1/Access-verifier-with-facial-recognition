// Modal functions for admin panel

function openAddUser() {
    const modal = document.getElementById("modal");
    if (!modal) {
        console.error("Modal element not found");
        return;
    }

    const modalContent = document.createElement("div");
    modalContent.innerHTML = `
        <div style="
            background: white;
            border-radius: 8px;
            padding: 30px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.15);
            max-width: 400px;
            width: 90%;
        ">
            <h2 style="margin: 0 0 20px 0; color: #333;">Nowy użytkownik</h2>
            <form id="addUserForm">
                <input 
                    type="text" 
                    id="userName" 
                    name="name" 
                    placeholder="Imię i nazwisko" 
                    required
                    style="
                        width: 100%;
                        padding: 10px;
                        margin-bottom: 15px;
                        border: 1px solid #ddd;
                        border-radius: 4px;
                        font-size: 14px;
                        box-sizing: border-box;
                    "
                >
                <div style="display: flex; gap: 10px;">
                    <button type="submit" style="flex: 1; padding: 10px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer; font-weight: bold;">
                        Dodaj
                    </button>
                    <button type="button" onclick="closeModal()" style="flex: 1; padding: 10px; background: #6c757d; color: white; border: none; border-radius: 4px; cursor: pointer;">
                        Anuluj
                    </button>
                </div>
            </form>
        </div>
    `;

    modal.style.position = "fixed";
    modal.style.top = "0";
    modal.style.left = "0";
    modal.style.width = "100%";
    modal.style.height = "100%";
    modal.style.backgroundColor = "rgba(0, 0, 0, 0.5)";
    modal.style.display = "flex";
    modal.style.justifyContent = "center";
    modal.style.alignItems = "center";
    modal.style.zIndex = "10000";

    modal.innerHTML = "";
    modal.appendChild(modalContent);

    document.getElementById("addUserForm").addEventListener("submit", addUserSubmit);
}

function closeModal() {
    const modal = document.getElementById("modal");
    if (modal) {
        modal.innerHTML = "";
        modal.style.display = "none";
    }
}

async function addUserSubmit(event) {
    event.preventDefault();
    
    const name = document.getElementById("userName").value.trim();
    if (!name) {
        alert("Proszę wpisać imię i nazwisko");
        return;
    }

    const formData = new FormData();
    formData.append("name", name);

    try {
        const response = await fetch("/admin/users/new", {
            method: "POST",
            body: formData
        });

        if (response.ok || response.status === 303) {
            closeModal();
            window.location.reload();
        } else {
            const errorText = await response.text();
            console.error("Error response:", errorText);
            alert("Błąd przy dodawaniu użytkownika. Status: " + response.status);
        }
    } catch (error) {
        console.error("Fetch error:", error);
        alert("Błąd przy połączeniu: " + error.message);
    }
}

