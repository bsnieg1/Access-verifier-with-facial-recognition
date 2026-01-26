const phrases = [
    "Milej pracy! 💪",
    "Powodzenia! 🍀",
    "Dziś jest Twój dzień! ⭐",
    "Bądź produktywny! 💼",
    "Do roboty! 🎯",
    "Wszystko się uda! ✨",
    "Wspaniałego dnia! 🌟"
];

const MAX_PHRASES = 8;        // ile maksymalnie naraz
const INTERVAL_TIME = 500;  // co ile ms nowe hasło
const LIFETIME = 6000;       // jak długo widoczne

function createFloatingPhrase() {
    const bg = document.getElementById("background-text");
    if (!bg) return;

    // LIMIT ilości
    if (bg.children.length >= MAX_PHRASES) return;

    const phrase = phrases[Math.floor(Math.random() * phrases.length)];
    const element = document.createElement("div");

    element.className = "floating-phrase";
    element.textContent = phrase;

    element.style.left = (Math.random() * 80 + 10) + "%";
    element.style.top  = (Math.random() * 60 + 20) + "%";

    bg.appendChild(element);

    setTimeout(() => element.remove(), LIFETIME);
}

// JEDNO interval
setInterval(createFloatingPhrase, INTERVAL_TIME);

// pierwsze hasło po załadowaniu
createFloatingPhrase();
