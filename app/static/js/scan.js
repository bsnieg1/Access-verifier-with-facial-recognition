function unlockFaceVerification(scanBtn, faceBtn) {
    scanBtn.disabled = true;

    scanBtn.style.background = "#c62828";
    scanBtn.style.color = "white";

    faceBtn.disabled = false;
    faceBtn.style.background = "#2e7d32";
    faceBtn.style.color = "white";

    faceBtn.classList.add("pulse");

    // opcjonalny dźwięk (podmienisz plik)
    const audio = new Audio("/static/assets/unlock.mp3");
    audio.play().catch(() => {});
}

document.addEventListener("DOMContentLoaded", function() {
    const video = document.getElementById("video");
    const canvas = document.getElementById("canvas");
    const scanBtn = document.getElementById("scanBtn");
    const faceBtn = document.getElementById("faceBtn");
    const result = document.getElementById("result");

    // Extract session_id from URL or data attribute
    const sessionId = document.body.getAttribute("data-session-id") || 
                      new URLSearchParams(window.location.search).get("session_id");

    scanBtn.addEventListener("click", async function() {
        result.textContent = "Skanowanie...";
        
        const entryType = document.querySelector('input[name="entry_type"]:checked').value;
        
        const context = canvas.getContext("2d");
        context.drawImage(video, 0, 0, canvas.width, canvas.height);
        
        canvas.toBlob(async function(blob) {
            const formData = new FormData();
            formData.append("file", blob, "qr.png");
            formData.append("entry_type", entryType);
            
            try {
                const response = await fetch(`/verification/${sessionId}/qr`, {
                    method: "POST",
                    body: formData
                });
                
                const data = await response.json();
                
                if (data.status === "WAITING_FOR_FACE" || data.status === "SUCCESS") {
                    result.textContent = "✓ QR zeskanowany!";
                    result.style.color = "green";
                    unlockFaceVerification(scanBtn, faceBtn);
                } else if (data.status === "QR_NOT_FOUND") {
                    result.textContent = "✗ Nie wykryto kodu QR. Spróbuj ponownie.";
                    result.style.color = "red";
                } else if (data.status === "USER_NOT_FOUND") {
                    result.textContent = "✗ Nieznany kod QR (użytkownik nie w bazie).";
                    result.style.color = "red";
                } else if (data.status === "ALREADY_INSIDE") {
                    result.textContent = "✗ Jesteś już w fabryce! Musisz najpierw wyjść.";
                    result.style.color = "red";
                } else {
                    result.textContent = data.message || "Błąd skanowania";
                    result.style.color = "red";
                }
            } catch (error) {
                console.error("Błąd:", error);
                result.textContent = "Błąd komunikacji z serwerem";
                result.style.color = "red";
            }
        }, "image/png");
    });
    
    faceBtn.addEventListener("click", async function() {
        result.textContent = "Weryfikacja twarzy...";
        
        const context = canvas.getContext("2d");
        context.drawImage(video, 0, 0, canvas.width, canvas.height);
        
        canvas.toBlob(async function(blob) {
            const formData = new FormData();
            formData.append("file", blob, "face.png");
            
            try {
                const response = await fetch(`/verification/${sessionId}/face`, {
                    method: "POST",
                    body: formData
                });
                
                const data = await response.json();
                console.log("Odpowiedź weryfikacji:", data);
                
                if (data.status === "ACCESS_GRANTED") {
                    result.textContent = "✓ Dostęp przyznany! Zaraz przekierujemy Cię dalej...";
                    result.style.color = "green";
                    result.style.fontSize = "18px";
                    result.style.marginTop = "20px";
                    setTimeout(() => {
                        window.location.href = `/verification/${sessionId}/success`;
                    }, 3000);
                } else if (data.status === "ACCESS_DENIED") {
                    result.textContent = data.message || "✗ Dostęp odrzucony.";
                    result.style.color = "red";
                } else if (data.status === "USER_NOT_FOUND") {
                    result.textContent = "✗ Użytkownik nie znaleziony.";
                    result.style.color = "red";
                } else if (data.error) {
                    result.textContent = data.error;
                    result.style.color = "red";
                } else {
                    result.textContent = data.message || "Błąd weryfikacji";
                    result.style.color = "red";
                }
            } catch (error) {
                console.error("Błąd:", error);
                result.textContent = "Błąd komunikacji z serwerem";
                result.style.color = "red";
            }
        }, "image/png");
    });
});

