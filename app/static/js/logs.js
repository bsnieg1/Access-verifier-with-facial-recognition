function openImage(src) {
    const overlay = document.createElement("div");

    overlay.innerHTML = `
        <img src="${src}" style="
            max-width: 90%;
            max-height: 90%;
            border-radius: 12px;
            box-shadow: 0 0 40px rgba(0,0,0,.8);
        ">
    `;

    Object.assign(overlay.style, {
        position: "fixed",
        inset: "0",
        background: "rgba(0,0,0,0.85)",
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        zIndex: "9999",
        cursor: "pointer"
    });

    overlay.onclick = () => overlay.remove();
    document.body.appendChild(overlay);
}
