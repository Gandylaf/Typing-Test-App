const form = document.getElementById("typing-form");
const timerDisplay = document.getElementById("timer"); // store display dom element
const testText = document.getElementById("test-text").innerText;
const typingArea = document.getElementById("typing-area");
let timeLeft = 30;
let timerStarted = false;
let timer;

typingArea.addEventListener("input", () => {
    if (!timerStarted) {
        timerStarted = true;
        timerDisplay.innerText = timeLeft;

        timer = setInterval(() => {
            timeLeft--;
            timerDisplay.innerText = timeLeft;

            if (timeLeft <= 0) {
                clearInterval(timer);
                form.submit();
            }
        }, 1000);

    }


// Real-time highlighting
    const input = typingArea.value;
    let highlighted = "";

    for (let i = 0; i < testText.length; i++) {
        if (i < input.length) {
            highlighted += input[i] === testText[i]
                ? `<span style="color: green;">${testText[i]}</span>`
                : `<span style="color: red;">${testText[i]}</span>`;
        } else {
            highlighted += `<span style="color: #F8F9FA;">${testText[i]}</span>`
        }
    }

    document.getElementById("test-text").innerHTML = highlighted;
});

// Disable pasting
typingArea.addEventListener("paste", (e) => {
    e.preventDefault();
    alert("Pasting is not allowed!");
});
// third party ai tool chatgpt used as helper to come up with anti cheat functions and research more into javascript for this typing test
// Disable dropping text
typingArea.addEventListener("drop", (e) => {
    e.preventDefault();
    alert("Dropping text is not allowed!");
});

// Optional: disable right-click context menu inside the textarea
typingArea.addEventListener("contextmenu", (e) => {
    e.preventDefault();
});
