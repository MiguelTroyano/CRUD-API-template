// --- function that helps interpret error responses from the API ---
async function extractError(response) {
    try {
        const error = await response.json()
        if (typeof error.detail === "string") return error.detail;
        if (Array.isArray(error.detail)) return error.detail.map(e => e.msg).join(". ");    // FastAPI returns 422 errors as arrays.
        return "Unexpected error";
    } catch {
        return "Could not connect to the server";      // if the response has no JSON or no detail, the server must be down or it's an unformatted 500 error
    }
}

// --- function that checks whether there's a stored token and whether it has expired ---
function isTokenValid() {
    const token = localStorage.getItem("token");
    if (!token) return false;

    try {
        // JWT token: header.payload.signature. We're interested in the payload.
        const payload = JSON.parse(atob(token.split(".")[1]))       // atob decodes Base64

        return payload.exp * 1000 > Date.now();         // payload.exp is in Unix seconds and Date.now() returns milliseconds.
    } catch {
        return false;           // malformed token
    }
}

// --- helper function that fetches URLs adding the token stored in localStorage to the headers ---
async function fetchAuth(url, options = {}) {
    const token = localStorage.getItem("token");

    // creates a dictionary identical to the one passed in, plus the Authorization key with the token.
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

// --- screen display ---
function showApp() {
    document.getElementById("login-screen").style.display = "none";
    document.getElementById("app-screen").style.display = "block";
    loadItems();
}

function showLogin() {
    document.getElementById("login-screen").style.display = "block";
    document.getElementById("app-screen").style.display = "none";
}


// --- login and registration functions ---
// async allows using await, which tells the program to wait for a response
async function login() {
    const username = document.getElementById("login-username").value;
    const password = document.getElementById("login-password").value;

    const response = await fetch("/login", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({username, password})          // no need to write {username: username, password: password}. Since the names match, it can be shortened.
    });

    if (!response.ok) {
        document.getElementById("login-error").textContent = await extractError(response);
        return;
    }

    const data = await response.json();
    localStorage.setItem("token", data.access_token);       // we store the token in browser storage that persists after reloading/closing the page or the browser
    // localStorage is VERY VULNERABLE to XSS attacks, and it's VERY EASY TO STEAL TOKENS stored in it.
    // A much safer alternative is an HttpOnly cookie, which JS can't read.

    document.getElementById("login-error").textContent = "";

    // clear the login fields
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
    localStorage.removeItem("token");           // the token isn't invalidated, it's just "forgotten"
    document.getElementById('item-list').innerHTML = '';   // clear the list on logout. Keeps state and storage consistent.
    showLogin();
}


// --- CRUD operations ---
async function loadItems() {
    // The item list is emptied before making any call. This avoids showing out-of-date list states.
    const list = document.getElementById('item-list');
    list.innerHTML = '';       //empties the list before redrawing it.
    //Emptying the list and reloading every item after each change is inefficient, and that's why React is used

    // we use fetch with no extra arguments, which calls the simplest GET method of the API
    // We catch the 401 error here in case it happens. This avoids an UnhandledRejection, which can be a problem in Node.js
    let response;
    try {
        response = await fetchAuth('/items');
    } catch {
        return;     // we do nothing, fetchAuth already calls logout
    }

    const items = await response.json();

    // for each item, we create:
    //  an <li> block (li)
    //  an <input type=checkbox checked=item.done> (checkbox) to change its done state
    //  a <span> with the item's title
    //  a <button> to delete the item
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

        li.append(checkbox, text, deleteButton);     //add every created element to the block
        list.appendChild(li);                  //add the block to the list
    }
}

async function createItem() {
    const input = document.getElementById('new-item');
    const title = input.value.trim();
    if (!title) return;                          // if there's no text, nothing is created

    // we use fetch again, but with the POST method
    //  the headers say that a JSON will be sent, which is what the create_item() function expects (class ItemCreate(SQLModel))
    //  the body contains the item as JSON. It only has the title, since in Python we set id with Field(default=None), and done=False
    try {
        await fetchAuth("/items", {
            method: "POST",
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ title: title })
        });
    } catch {
        return;
    }

    input.value = '';       //clear the field for the next item
    loadItems();        //redraws the list
}

async function setDone(id, done) {
    // When a checkbox is clicked, the API's PUT method is called.
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

// --- input setup so they submit when pressing ENTER ---
const newItemInput = document.getElementById('new-item');
//addEventListener is needed if you want to run several functions
newItemInput.addEventListener('keydown', (e) => {
    if (e.key === "Enter") {
        createItem();
    }
});
newItemInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') console.log('Enter detected!');        //shown in the browser console (Ctrl + Shift + J or F12)
});

const usernameInput = document.getElementById('login-username');
//addEventListener is needed if you want to run several functions
usernameInput.addEventListener('keydown', (e) => {
    if (e.key === "Enter") {
        login();
    }
});

const passwordInput = document.getElementById('login-password');
//addEventListener is needed if you want to run several functions
passwordInput.addEventListener('keydown', (e) => {
    if (e.key === "Enter") {
        login();
    }
});

//When the page opens, check whether there's a token in localStorage
if (isTokenValid()) {
    showApp();
} else {
    showLogin();
}
