const phrases = [
    "Milej pracy! 😊",
    "Powodzenia! 😊",
    "Dziś jest Twój dzień! 😊",
    "Bądź produktywny! 😊",
    "Sił ci do pracy! 😊",
    "Wszystko się uda! 😊",
    "Wspaniałego dnia! 😊",
    "Bądź najlepszy w tym co robisz! 😊",
    "Każdy krok to postęp! 😊",
    "Ty możesz! 😊",
    "Skupienie i determinacja! 😊",
    "Zrób to lepiej niż wczoraj! 😊",
    "Nie ma niemożliwych zadań! 😊",
    "Jesteś gotowy na wyzwanie! 😊",
    "Sukces czeka na Ciebie! 😊",
    "Praca to przyjemność! 😊",
    "Każdy dzień to nowa szansa! 😊"
];

const MAX_PHRASES = 4;        // ile maksymalnie naraz
const INTERVAL_TIME = 2000;   // co ile ms nowe hasło
const LIFETIME = 8000;        // jak długo widoczne
const INITIAL_STAGGER = 300;  // jak rozprzestrzenić pierwsze hasła (ms)

function createFloatingPhrase() {
    const bg = document.getElementById("background-text");
    if (!bg) return;

    // LIMIT ilości
    if (bg.children.length >= MAX_PHRASES) return;

    const phrase = phrases[Math.floor(Math.random() * phrases.length)];
    const element = document.createElement("div");

    element.className = "floating-phrase";
    element.textContent = phrase;

    element.style.left = (Math.random() * 90 + 5) + "%";
    element.style.top  = (Math.random() * 70 + 10) + "%";

    bg.appendChild(element);

    setTimeout(() => element.remove(), LIFETIME);
}

// Rozprzestrzeń pierwsze hasła w czasie
for (let i = 0; i < MAX_PHRASES; i++) {
    setTimeout(() => createFloatingPhrase(), i * INITIAL_STAGGER);
}

// Następnie regularny interval
setTimeout(() => {
    setInterval(createFloatingPhrase, INTERVAL_TIME);
}, MAX_PHRASES * INITIAL_STAGGER);
