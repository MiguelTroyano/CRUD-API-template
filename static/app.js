// --- función que ayuda a interpretar errores de respuestas de la API ---
async function extraerError(respuesta) {
    try {
        const error = await respuesta.json()
        if (typeof error.detail === "string") return error.detail;
        if (Array.isArray(error.detail)) return error.detail.map(e => e.msg).join(". ");    // FASTAPI lanza errores 422 en forma de arrays.
        return "Error inesperado";
    } catch {
        return "Error de conexión con el servidor";      // si la respuesta no trae JSON o detail, debe ser que el servidor se ha caido o un error 500 sin formato
    }
}

// --- función que comprueba si hay un token almacenado y si ha expirado ---
function tokenValido() {
    const token = localStorage.getItem("token");
    if (!token) return false;

    try {
        // token JWT: cabecera.payload.firma. Nos interesa el payload.
        const payload = JSON.parse(atob(token.split(".")[1]))       // atob decodifica Base64

        return payload.exp * 1000 > Date.now();         // payload.exp esta en milisegundos Unix y Date.now() lo devuelve en segundos.
    } catch {
        return false;           // token mal formado
    }
}

// --- función ayudante que hace fetch a URLs añadiendo el token almacenado en localStorage a los headers ---
async function fetchAuth(url, opciones = {}) {
    const token = localStorage.getItem("token");

    // crea un diccionario idéntico al introducido sumado de la clave Authorization con el token.
    opciones.headers = {
        ...opciones.headers,
        'Authorization': 'Bearer ' + token
    };

    const respuesta = await fetch(url, opciones);
    
    if (respuesta.status === 401) {
        cerrarSesion();
        throw new Error("Sesión Expirada");
    }
    return respuesta;
}

// --- display de pantallas ---
function mostrarApp() {
    document.getElementById("pantalla-login").style.display = "none";
    document.getElementById("pantalla-app").style.display = "block";
    cargarObjetos();
}

function mostrarLogin() {
    document.getElementById("pantalla-login").style.display = "block";
    document.getElementById("pantalla-app").style.display = "none";
}


// --- funciones de login y registro ---
// async permite usar await, que ordena al programa esperar una respuesta
async function login() {
    const username = document.getElementById("login-username").value;
    const password = document.getElementById("login-password").value;

    const respuesta = await fetch("/login", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({username, password})          // no es necesario escribir {username: username, password: password}. Como coinciden los nombres, se puede abreviar.
    });

    if (!respuesta.ok) {
        document.getElementById("login-error").textContent = await extraerError(respuesta);
        return;
    }

    const datos = await respuesta.json();
    localStorage.setItem("token", datos.access_token);       // guardamos el token en un almacenamiento temporal del navegador que se mantiene despues de recargar/cerrar la página o el navegador
    // El localStorage es una sección MUY VULNERABLE a ataques tipo XSS y es MUY FÁCIL ROBAR TOKENS que estén almacenados en él.
    // Una alternativa mucho más segura es usar una cookie HTTPOnly que JS no puede leer.

    document.getElementById("login-error").textContent = "";
    mostrarApp();
}


async function registrar() {
    const username = document.getElementById("login-username").value;
    const password = document.getElementById("login-password").value;

    const respuesta = await fetch("/register", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({username, password})
    });

    if (!respuesta.ok) {
        document.getElementById("login-error").textContent = await extraerError(respuesta);
        return;
    }

    await login();
}


function cerrarSesion() {
    localStorage.removeItem("token");           // no se invalida el token, sólo se "olvida"
    document.getElementById('lista-objetos').innerHTML = '';   // limpiar la lista al salir. Coherencia estado - almacenamiento.
    mostrarLogin();
}


// --- operaciones CRUD ---
async function cargarObjetos() {
    // Se vacía la lista de objetos antes de hacer ninguna llamada. Evitamos mostrar estados de lista desactualizados.
    const lista = document.getElementById('lista-objetos');     
    lista.innerHTML = '';       //vacía la lista antes de repintarla.
    //La práctica de revaciar la lista y cargar todos los objetos cada vez que hay una modificación es ineficiente y por eso se usa React

    // usamos fetch sin más argumentos, llamando así al método GET más simple de la API
    // Capturamos desde aquí el error 401 en caso de que ocurra. Esto evita UnhandledRejection que puede ser problematica para Node.js
    let respuesta;
    try {
        respuesta = await fetchAuth('/objetos');
    } catch {
        return;     // no hacemos nada, fetchAuth ya llama a cerrarSesion
    }

    const objetos = await respuesta.json();

    // por cada objeto, se crea:
    //  un bloque <li> (li) 
    //  un <input type=checkbox checked=obj.done> (checkbox) para cambiar su estado done
    //  un <span> con el título del objeto
    //  un <button> para borrar el objeto
    for (const obj of objetos) {
        const li = document.createElement('li');

        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.checked = obj.done;
        checkbox.onclick = () => cambiarEstado(obj.id, checkbox.checked);

        const texto = document.createElement('span')
        texto.textContent = obj.title;
        if (obj.done) {
            texto.className = 'done';
        }

        const borrar = document.createElement('button');
        borrar.textContent = '🗑';
        borrar.onclick = () => borrarObjeto(obj.id);
        
        li.append(checkbox, texto, borrar);     //añadir al bloque todos los elementos creados
        lista.appendChild(li);                  //añadir a la lista el bloque
    }
}

async function crearObjeto() {
    const input = document.getElementById('nuevo-objeto');
    const title = input.value.trim();
    if (!title) return;                          // si no hay texto, no se crea nada
    
    // usamos de nuevo fetch, pero con el método POST
    //  los headers establecen que se va a enviar como argumento un JSON, que es lo que espera la función crear_objeto() (clase Objeto(SQLModel))
    //  el cuerpo contiene el objeto en forma JSON. Solo contiene el titulo, ya que en python establecimos id con Field(default=None), y done=False
    try {
        await fetchAuth("/objetos", {
            method: "POST",
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ title: title })
        });
    } catch {
        return;
    }
    
    input.value = '';       //limpiar el campo para el próximo objeto
    cargarObjetos();        //repinta la lista
}

async function cambiarEstado(id, done) {
    // Al clickar algun checkbox, se llama al metodo PUT de la API.
    //  como en python habíamos declarado el estado done como un argumento suelto, lo introducimos en la URL, no en el body
    try {
        await fetchAuth('/objetos/' + id + '?done=' + done, {
            method: "PUT"
        });
    } catch {
        return;
    }

    cargarObjetos();
}

async function borrarObjeto(id) {
    try {
        await fetchAuth('/objetos/' + id, {
            method: "DELETE"
        });
    } catch {
        return;
    }

    cargarObjetos();
}

// --- configuración de inputs para enviarse al pulsar ENTER ---
const input_objeto = document.getElementById('nuevo-objeto');
//necesario usar addeventlistener si se quieren ejecutar varias funciones
input_objeto.addEventListener('keydown', (e) => {
    if (e.key === "Enter") {
        crearObjeto();
    }
});
input_objeto.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') console.log('¡Enter detectado!');        //se muestra en la consola del navegador (Ctrl + Shift + J o F12)
});

const input_username = document.getElementById('login-username');
//necesario usar addeventlistener si se quieren ejecutar varias funciones
input_username.addEventListener('keydown', (e) => {
    if (e.key === "Enter") {
        login();
    }
});

const input_password = document.getElementById('login-password');
//necesario usar addeventlistener si se quieren ejecutar varias funciones
input_password.addEventListener('keydown', (e) => {
    if (e.key === "Enter") {
        login();
    }
});

//Al abrir la página, comprobar si hay un token en localStorage
if (tokenValido()) {
    mostrarApp();
} else {
    mostrarLogin();
}
