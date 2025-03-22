const API_URL = "http://127.0.0.1:5000";

// ✅ LOGIN FUNCTION
document.addEventListener("DOMContentLoaded", function () {
    const loginForm = document.getElementById("login-form");
    if (loginForm) {
        loginForm.addEventListener("submit", async function (e) {
            e.preventDefault();
            const email = document.getElementById("email").value;
            const password = document.getElementById("password").value;

            const response = await fetch(`${API_URL}/login`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ email, password })
            });

            const data = await response.json();
            if (response.ok) {
                localStorage.setItem("user_id", data.user_id);
                window.location.href = "dashboard.html";  // Redirect to Chatbot
            } else {
                document.getElementById("error-message").textContent = data.error;
            }
        });
    }

    // ✅ REGISTER FUNCTION
    const registerForm = document.getElementById("register-form");
    if (registerForm) {
        registerForm.addEventListener("submit", async function (e) {
            e.preventDefault();
            const email = document.getElementById("email").value;
            const password = document.getElementById("password").value;

            const response = await fetch(`${API_URL}/signup`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ email, password })
            });

            const data = await response.json();
            if (response.ok) {
                alert("Signup successful! Please log in.");
                window.location.href = "index.html";  // Redirect to Login Page
            } else {
                document.getElementById("error-message").textContent = data.error;
            }
        });
    }
});


