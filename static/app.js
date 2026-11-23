// --- función que ayuda a interpretar errores de respuestas de la API ---
async function extractError(response) {
    try {
        const error = await response.json()
        if (typeof error.detail === "string") return error.detail;
        if (Array.isArray(error.detail)) return error.detail.map(e => e.msg).join(". ");    // FASTAPI lanza errores 422 en forma de arrays.
        return "Unexpected error";
    } catch {
        return "Could not connect to the server";      // si la respuesta no trae JSON o detail, debe ser que el servidor se ha caido o un error 500 sin formato
    }
}

// --- función que comprueba si hay un token almacenado y si ha expirado ---
function isTokenValid() {
    const token = localStorage.getItem("token");
    if (!token) return false;

    try {
        // token JWT: cabecera.payload.firma. Nos interesa el payload.
        const payload = JSON.parse(atob(token.split(".")[1]))       // atob decodifica Base64

        return payload.exp * 1000 > Date.now();         // payload.exp esta en segundos Unix y Date.now() lo devuelve en milisegundos.
    } catch {
        return false;           // token mal formado
    }
}

// --- función ayudante que hace fetch a URLs añadiendo el token almacenado en localStorage a los headers ---
async function fetchAuth(url, options = {}) {
    const token = localStorage.getItem("token");

    // crea un diccionario idéntico al introducido sumado de la clave Authorization con el token.
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

// --- display de pantallas ---
function showApp() {
    document.getElementById("login-screen").style.display = "none";
    document.getElementById("app-screen").style.display = "block";
    loadItems();
}

function showLogin() {
    document.getElementById("login-screen").style.display = "block";
    document.getElementById("app-screen").style.display = "none";
}


// --- funciones de login y registro ---
// async permite usar await, que ordena al programa esperar una respuesta
async function login() {
    const username = document.getElementById("login-username").value;
    const password = document.getElementById("login-password").value;

    const response = await fetch("/login", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({username, password})          // no es necesario escribir {username: username, password: password}. Como coinciden los nombres, se puede abreviar.
    });

    if (!response.ok) {
        document.getElementById("login-error").textContent = await extractError(response);
        return;
    }

    const data = await response.json();
    localStorage.setItem("token", data.access_token);       // guardamos el token en un almacenamiento temporal del navegador que se mantiene despues de recargar/cerrar la página o el navegador
    // El localStorage es una sección MUY VULNERABLE a ataques tipo XSS y es MUY FÁCIL ROBAR TOKENS que estén almacenados en él.
    // Una alternativa mucho más segura es usar una cookie HTTPOnly que JS no puede leer.

    document.getElementById("login-error").textContent = "";

    // limpiar los campos del login
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
    localStorage.removeItem("token");           // no se invalida el token, sólo se "olvida"
    document.getElementById('item-list').innerHTML = '';   // limpiar la lista al salir. Coherencia estado - almacenamiento.
    showLogin();
}


// --- operaciones CRUD ---
async function loadItems() {
    // Se vacía la lista de objetos antes de hacer ninguna llamada. Evitamos mostrar estados de lista desactualizados.
    const list = document.getElementById('item-list');
    list.innerHTML = '';       //vacía la lista antes de repintarla.
    //La práctica de revaciar la lista y cargar todos los objetos cada vez que hay una modificación es ineficiente y por eso se usa React

    // usamos fetch sin más argumentos, llamando así al método GET más simple de la API
    // Capturamos desde aquí el error 401 en caso de que ocurra. Esto evita UnhandledRejection que puede ser problematica para Node.js
    let response;
    try {
        response = await fetchAuth('/items');
    } catch {
        return;     // no hacemos nada, fetchAuth ya llama a logout
    }

    const items = await response.json();

    // por cada objeto, se crea:
    //  un bloque <li> (li)
    //  un <input type=checkbox checked=item.done> (checkbox) para cambiar su estado done
    //  un <span> con el título del objeto
    //  un <button> para borrar el objeto
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

        li.append(checkbox, text, deleteButton);     //añadir al bloque todos los elementos creados
        list.appendChild(li);                  //añadir a la lista el bloque
    }
}

async function createItem() {
    const input = document.getElementById('new-item');
    const title = input.value.trim();
    if (!title) return;                          // si no hay texto, no se crea nada

    // usamos de nuevo fetch, pero con el método POST
    //  los headers establecen que se va a enviar como argumento un JSON, que es lo que espera la función create_item() (clase ItemCreate(SQLModel))
    //  el cuerpo contiene el objeto en forma JSON. Solo contiene el titulo, ya que en python establecimos id con Field(default=None), y done=False
    try {
        await fetchAuth("/items", {
            method: "POST",
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ title: title })
        });
    } catch {
        return;
    }

    input.value = '';       //limpiar el campo para el próximo objeto
    loadItems();        //repinta la lista
}

async function setDone(id, done) {
    // Al clickar algun checkbox, se llama al metodo PUT de la API.
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

// --- configuración de inputs para enviarse al pulsar ENTER ---
const newItemInput = document.getElementById('new-item');
//necesario usar addeventlistener si se quieren ejecutar varias funciones
newItemInput.addEventListener('keydown', (e) => {
    if (e.key === "Enter") {
        createItem();
    }
});
newItemInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') console.log('Enter detected!');        //se muestra en la consola del navegador (Ctrl + Shift + J o F12)
});

const usernameInput = document.getElementById('login-username');
//necesario usar addeventlistener si se quieren ejecutar varias funciones
usernameInput.addEventListener('keydown', (e) => {
    if (e.key === "Enter") {
        login();
    }
});

const passwordInput = document.getElementById('login-password');
//necesario usar addeventlistener si se quieren ejecutar varias funciones
passwordInput.addEventListener('keydown', (e) => {
    if (e.key === "Enter") {
        login();
    }
});

//Al abrir la página, comprobar si hay un token en localStorage
if (isTokenValid()) {
    showApp();
} else {
    showLogin();
}
