import { TypingDNA } from './typingdna.js';
import { AutocompleteDisabler } from './autocomplete-disabler.js';

const tdna = new TypingDNA();
const autocompleteDisabler = new AutocompleteDisabler({
    showTypingVisualizer: true,
    showTDNALogo: true,
});
autocompleteDisabler.disableAutocomplete();
autocompleteDisabler.disableCopyPaste();

const loginButton = document.getElementById("login-button");
if (loginButton) {
    loginButton.addEventListener("click", () => loginOrSignup(true));
    tdna.addTarget("email");
    tdna.addTarget("password");
}

const signUpButton = document.getElementById("sign-up-button");
if (signUpButton) {
    signUpButton.addEventListener("click", () => loginOrSignup(false));
    tdna.addTarget("email");
    tdna.addTarget("password");
}

const typingPatternsButton = document.getElementById("typing-patterns-button");
if (typingPatternsButton) {
    typingPatternsButton.addEventListener("click", () => loginOrSignup(true));
    tdna.addTarget("email");
    tdna.addTarget("password");
}

export function loginOrSignup(login = true) {
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    let endpoint;
    if (login) {
        endpoint = "/api/login";
    } else {
        endpoint = "/api/sign-up";
    }

    fetch(endpoint, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ email: email, password: password }),
    })
        .then((res) => res.json())
        .then((data) => {
            if (data.user_id) {
                sendTypingData(data.user_id, email + password);
            } else if (data.message) {
                alert(data.message);
            }
        });
}

function sendTypingData(id, text) {
    const pattern = tdna.getTypingPattern({
        type: 1,
        text: text,
    });
    fetch("/typingdna", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ pattern: pattern, user_id: id }),
    })
        .then((res) => res.json())
        .then((data) => {
            tdna.reset();
            console.log(data.result);
            if (data.message_code === 10) {
                alert(
                    "We need to collect some typing data from you for 2FA, you may be asked to fill in the credentials multiple times..."
                );
                window.location = "/typing-patterns";
            } else {
                if (data.result === 1) {
                    alert(
                        "TypinDNA indicated that the match was successful, you are now logged in"
                    )
                    window.location = "/";
                } else {
                    alert(
                        "TypinDNA indicated that the match was not successful, please try again."
                    )
                }
            }
        });
}

document.addEventListener("DOMContentLoaded", function () {
    const themeToggleButton = document.getElementById("theme-toggle");
    console.log("DOM fully loaded and parsed");
    console.log("Theme Toggle Button:", themeToggleButton);

    // Check if there's a saved theme in localStorage
    const savedTheme = localStorage.getItem("theme");
    if (savedTheme) {
        document.body.classList.add(savedTheme);
        themeToggleButton.textContent = savedTheme === "dark-mode" ? "Switch to Light Mode" : "Switch to Dark Mode";
    }

    themeToggleButton.addEventListener("click", function () {
        console.log("Theme toggle button clicked");
        document.body.classList.toggle("dark-mode");
        document.body.classList.toggle("light-mode");

        // Update button text
        if (document.body.classList.contains("dark-mode")) {
            themeToggleButton.textContent = "Switch to Light Mode";
            localStorage.setItem("theme", "dark-mode");
        } else {
            themeToggleButton.textContent = "Switch to Dark Mode";
            localStorage.setItem("theme", "light-mode");
        }
    });
});
