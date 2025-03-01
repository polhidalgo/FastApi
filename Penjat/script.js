let palabraSecreta = '';
let palabraMostrar = [];
let intentos = 10;
let puntos = 0;
let letrasUsadas = [];
let game_id = null;

const palabraInput = document.getElementById('palabraInput');
const palabraOculta = document.getElementById('palabraOculta');
const intentosRestantes = document.getElementById('intentosRestantes');
const botonesLetras = document.getElementById('botonesLetras');
const registerForm = document.getElementById('registerForm');
const registerMessage = document.getElementById('registerMessage');
const loginForm = document.getElementById('loginForm');
const loginMessage = document.getElementById('loginMessage');

document.addEventListener("DOMContentLoaded", () => {
    // Cargar las estadísticas del usuario 1 al cargar la página
    loadUserStats(1);
});

function togglePassword() {
    palabraInput.type = palabraInput.type === 'password' ? 'text' : 'password';
}

registerForm.addEventListener('submit', (e) => {
    e.preventDefault();
  
    const nom = document.getElementById('regNom').value;
    const email = document.getElementById('regEmail').value;
    const password = document.getElementById('regPassword').value;
  
    fetch('http://127.0.0.1:8000/users', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ nom, email, password })
    })
    .then(response => {
      if (!response.ok) {
        throw new Error('Error al crear el usuario');
      }
      return response.json();
    })
    .then(data => {
      registerMessage.style.color = 'green';
      registerMessage.textContent = `Registrado con ID: ${data.id}`;
      registerForm.reset();
    })
    .catch(error => {
      registerMessage.style.color = 'red';
      registerMessage.textContent = error.message;
    });
  });

  loginForm.addEventListener('submit', (e) => {
    e.preventDefault();
  
    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;
  
    fetch('http://127.0.0.1:8000/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ email, password })
    })
    .then(response => {
      if (!response.ok) {
        throw new Error('Credenciales inválidas');
      }
      return response.json();
    })
    .then(data => {
      loginMessage.style.color = 'green';
      loginMessage.textContent = `Bienvenido, ${data.nom} (ID: ${data.id})`;
      // Guarda el id del usuario (o token) en localStorage para usarlo en la partida
      localStorage.setItem("userId", data.id);
    })
    .catch(error => {
      loginMessage.style.color = 'red';
      loginMessage.textContent = error.message;
    });
  });
  

  function iniciarJuego() {
    const selectTematicas = document.getElementById("tematicas");
    const theme = selectTematicas.value.toUpperCase();

    if (!theme) {
        alert("Selecciona una temática para la partida");
        return;
    }

    // Obtener el id del usuario logeado desde localStorage
    const userId = localStorage.getItem("userId");
    if (!userId) {
        alert("Debes iniciar sesión para comenzar la partida");
        return;
    }

    // Llamada al backend para iniciar la partida con una palabra aleatoria
    fetch("http://127.0.0.1:8000/start", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        // Se usa el id del usuario logeado
        body: JSON.stringify({ usuari_id: parseInt(userId), theme: theme })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error("Error al iniciar la partida");
        }
        return response.json();
    })
    .then(data => {
        console.log("Partida iniciada:", data);
        game_id = data.game_id;

        // Obtener la palabra secreta aleatoria
        fetch(`http://127.0.0.1:8000/game/${game_id}/secret`)
        .then(resp => {
            if (!resp.ok) {
                throw new Error("Error al obtener la palabra secreta");
            }
            return resp.json();
        })
        .then(secretData => {
            palabraSecreta = secretData.secret_word.toUpperCase();
            console.log("Palabra secreta seleccionada:", palabraSecreta);

            palabraMostrar = Array(palabraSecreta.length).fill('_');
            mostrarPalabra();

            intentos = 10;
            letrasUsadas = [];
            intentosRestantes.innerHTML = `<img src="/img/img_${intentos}.jpg" alt="Intentos restantes">`;

            document.getElementById("comenzarJuego").disabled = true;
            palabraOculta.style.backgroundColor = 'white';

            generarBotonesLetras();
        })
        .catch(error => {
            alert(error);
            console.error(error);
        });
    })
    .catch(error => {
        alert(error);
        console.error(error);
    });
}


function cargarTematicas() {
    fetch("http://127.0.0.1:8000/penjat/tematica/opcions")
    .then(response => {
        if (!response.ok) {
            throw new Error("Error al cargar temáticas");
        }
        return response.json();
    })
    .then(data => {
        const selectTematicas = document.getElementById("tematicas");
        // Vaciar el select
        selectTematicas.innerHTML = "";
        // Suponiendo que cada opción es un objeto con la clave "option" (ajusta según tu respuesta)
        data.forEach(item => {
            const option = document.createElement("option");
            option.value = item.option;
            option.textContent = item.option;
            selectTematicas.appendChild(option);
        });
    })
    .catch(error => {
        console.error(error);
        alert("No se pudieron cargar las temáticas");
    });
}

// Ejecutar la carga de temáticas al iniciar la aplicación
document.addEventListener("DOMContentLoaded", () => {
    cargarTematicas();
});

function mostrarPalabra() {
    palabraOculta.textContent = palabraMostrar.join(' ');
}


function generarBotonesLetras() {
    const extendido = document.getElementById("extenderAbecedario").checked; // Verifica si el checkbox está marcado
    const url = `http://127.0.0.1:8000/alphabet?extended=${extendido}`;

    fetch(url)
    .then(response => {
        if (!response.ok) {
            throw new Error("Error al obtener el abecedario");
        }
        return response.json();
    })
    .then(data => {
        const letras = data.alphabet; // El backend devuelve un array con las letras
        botonesLetras.innerHTML = ''; // Limpiar botones anteriores

        letras.forEach(letra => {
            const boton = document.createElement('button');
            boton.textContent = letra;
            boton.onclick = () => verificarLetra(letra);
            boton.id = `boton-${letra}`;
            botonesLetras.appendChild(boton);
        });
    })
    .catch(error => {
        console.error(error);
        alert("No se pudo cargar el abecedario.");
    });
}

function loadUserStats(userId) {
    fetch(`http://127.0.0.1:8000/users/${userId}/stats`)
    .then(response => {
        if (!response.ok) {
            throw new Error("Error al obtener estadísticas");
        }
        return response.json();
    })
    .then(data => {
        const userStatsBox = document.getElementById("userStatsBox");
        let bestGameDateStr = data.best_game_date ? new Date(data.best_game_date).toLocaleString() : "N/A";
        userStatsBox.innerHTML = `
            <h2>JUGADOR ${data.user_id}</h2>
            <p>PUNTS PARTIDES ACTUALS: ${data.total_points}</p>
            <p>TOTAL PARTIDES: ${data.total_games}</p>
            <p>PARTIDES GUANYADES: ${data.games_won}</p>
            <p>PARTIDA AMB MÉS PUNTS: ${bestGameDateStr} - ${data.best_game_points} punts</p>
        `;
    })
    .catch(error => {
        console.error(error);
        alert("No se pudieron cargar las estadísticas del usuario");
    });
}



function verificarLetra(letra) {
    if (letrasUsadas.includes(letra)) return; 
    letrasUsadas.push(letra);

    let acierto = false;

    for (let i = 0; i < palabraSecreta.length; i++) {
        if (palabraSecreta[i] === letra) {
            palabraMostrar[i] = letra;
            acierto = true;
        }
    }

    if (acierto) {
        puntos++;
        mostrarPalabra();
        verificarVictoria();
    } else {
        intentos--;
       
        const imagen = document.querySelector('#intentosRestantes img');
        if (imagen) {
            imagen.src = `/img/img_${intentos}.jpg`;
        }

        document.getElementById(`boton-${letra}`).style.color = 'red';
    }
    

    if (intentos === 0) {
        finalizarJuego(false);
    }

}

function verificarVictoria() {
    if (palabraMostrar.join('') === palabraSecreta) {
        finalizarJuego(true);
    }
}

function finalizarJuego(ganado) {
    if (!game_id) {  
        console.error("Error: game_id no está definido");
        return;
    }

    const botonComenzar = document.getElementById("comenzarJuego");
    if (!botonComenzar) {
        console.error("Error: No se encontró el botón 'comenzarJuego'");
        return;
    }

    const resultado = ganado ? "ganado" : "perdido";
    // La puntuación es el número de intentos restantes si gana, o 0 si pierde.
    const puntosPartida = ganado ? intentos : 0;

    palabraOculta.style.backgroundColor = ganado ? 'green' : 'red';
    if (!ganado) {
        palabraOculta.textContent = palabraSecreta;
    }

    botonComenzar.disabled = false;

    fetch(`http://127.0.0.1:8000/game/${game_id}/finish`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ game_id: game_id, resultado: resultado, puntos: puntosPartida })
    })
    .then(response => response.json())
    .then(data => {
        console.log("Resultado registrado:", data);
        // Una vez finalizada la partida, recargamos las estadísticas del usuario logeado
        const userId = localStorage.getItem("userId");
        if (userId) {
            loadUserStats(userId);
        }
    })
    .catch(error => console.error("Error:", error));
}
