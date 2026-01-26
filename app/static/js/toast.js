function showToast(message) {
    const toast = document.createElement("div");
    toast.className = "fade-toast";
    toast.innerText = message;

    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 3000);
}
