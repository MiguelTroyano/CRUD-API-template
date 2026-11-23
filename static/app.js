// --- Helpers ---

// Turns an API error response into a readable message.
async function extractError(response) {
    try {
        const error = await response.json()
        if (typeof error.detail === "string") return error.detail;
        if (Array.isArray(error.detail)) return error.detail.map(e => e.msg).join(". ");    // 422 validation errors come as a list
        return "Unexpected error";
    } catch {
        return "Could not connect to the server";
    }
}

// Checks that a token is stored and has not expired yet.
function isTokenValid() {
    const token = localStorage.getItem("token");
    if (!token) return false;

    try {
        const payload = JSON.parse(atob(token.split(".")[1]))

        return payload.exp * 1000 > Date.now();         // exp is in seconds, Date.now() in milliseconds
    } catch {
        return false;
    }
}

// fetch() wrapper that sends the stored token and logs out on 401.
async function fetchAuth(url, options = {}) {
    const token = localStorage.getItem("token");

    options.headers = {
        ...options.headers,
        'Authorization': 'Bearer ' + token
    };

    const response = await fetch(url, options);

    if (response.status === 401) {
        logout();
        throw new Error("Session expired");
    }
    return response;
}

// --- Screens ---
function showApp() {
    document.getElementById("login-screen").style.display = "none";
    document.getElementById("app-screen").style.display = "block";
    loadItems();
}

function showLogin() {
    document.getElementById("login-screen").style.display = "block";
    document.getElementById("app-screen").style.display = "none";
}


// --- Authentication ---
async function login() {
    const username = document.getElementById("login-username").value;
    const password = document.getElementById("login-password").value;

    const response = await fetch("/login", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({username, password})
    });

    if (!response.ok) {
        document.getElementById("login-error").textContent = await extractError(response);
        return;
    }

    const data = await response.json();
    // Note: localStorage is readable by any script on the page (XSS risk); an HttpOnly cookie would be safer.
    localStorage.setItem("token", data.access_token);

    document.getElementById("login-error").textContent = "";

    document.getElementById("login-username").value = "";
    document.getElementById("login-password").value = "";
    showApp();
}


async function register() {
    const username = document.getElementById("login-username").value;
    const password = document.getElementById("login-password").value;

    const response = await fetch("/register", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({username, password})
    });

    if (!response.ok) {
        document.getElementById("login-error").textContent = await extractError(response);
        return;
    }

    await login();
}


function logout() {
    localStorage.removeItem("token");           // the token is only discarded client-side, not revoked
    document.getElementById('item-list').innerHTML = '';
    showLogin();
}


// --- Items (CRUD) ---
async function loadItems() {
    const list = document.getElementById('item-list');
    list.innerHTML = '';

    let response;
    try {
        response = await fetchAuth('/items');
    } catch {
        return;     // fetchAuth already logged out
    }

    const items = await response.json();

    for (const item of items) {
        const li = document.createElement('li');

        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.checked = item.done;
        checkbox.onclick = () => setDone(item.id, checkbox.checked);

        const text = document.createElement('span')
        text.textContent = item.title;
        if (item.done) {
            text.className = 'done';
        }

        const deleteButton = document.createElement('button');
        deleteButton.textContent = '🗑';
        deleteButton.onclick = () => deleteItem(item.id);

        li.append(checkbox, text, deleteButton);
        list.appendChild(li);
    }
}

async function createItem() {
    const input = document.getElementById('new-item');
    const title = input.value.trim();
    if (!title) return;

    try {
        await fetchAuth("/items", {
            method: "POST",
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ title: title })
        });
    } catch {
        return;
    }

    input.value = '';
    loadItems();
}

async function setDone(id, done) {
    try {
        await fetchAuth('/items/' + id, {
            method: "PUT",
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ done: done })
        });
    } catch {
        return;
    }

    loadItems();
}

async function deleteItem(id) {
    try {
        await fetchAuth('/items/' + id, {
            method: "DELETE"
        });
    } catch {
        return;
    }

    loadItems();
}

// --- Submit on Enter ---
const newItemInput = document.getElementById('new-item');
newItemInput.addEventListener('keydown', (e) => {
    if (e.key === "Enter") {
        createItem();
    }
});
newItemInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') console.log('Enter detected!');
});

const usernameInput = document.getElementById('login-username');
usernameInput.addEventListener('keydown', (e) => {
    if (e.key === "Enter") {
        login();
    }
});

const passwordInput = document.getElementById('login-password');
passwordInput.addEventListener('keydown', (e) => {
    if (e.key === "Enter") {
        login();
    }
});

// --- Startup ---
if (isTokenValid()) {
    showApp();
} else {
    showLogin();
}
