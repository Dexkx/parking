const usuarioLogueado = localStorage.getItem("usuarioLogueado");
const usuarioNombre = localStorage.getItem("usuarioNombre");

const welcome =
document.getElementById("welcomeMessage");

if(usuarioLogueado==="true"){

welcome.innerText=`Hola ${usuarioNombre}`;

}else{

welcome.innerText="Usuario invitado";

}

let reservas =
JSON.parse(localStorage.getItem("reservas")) || [];

const contador =
document.getElementById("contadorReservas");

if(usuarioNombre){

const reservasUsuario =
reservas.filter(r=>r.usuario===usuarioNombre);

contador.innerText=`Reservas: ${reservasUsuario.length}`;

}

const filtros =
JSON.parse(localStorage.getItem("filtroBusqueda")) || {};

let parqueaderosFiltrados =
parqueaderos.filter(p=>{

if(filtros.ciudad && p.ciudad!==filtros.ciudad)
return false;

if(filtros.zona && p.zona!==filtros.zona)
return false;

if(filtros.precio && p.precio>filtros.precio)
return false;

if(filtros.soloDisponibles && p.cupos===0)
return false;

return true;

});

const container =
document.getElementById("parqueaderosContainer");

function renderParqueaderos(){

container.innerHTML="";

parqueaderosFiltrados.forEach(p=>{

const card=document.createElement("div");

card.classList.add("card");

card.innerHTML=`

<h3>${p.nombre}</h3>
<p>${p.direccion}</p>
<p>Zona: ${p.zona}</p>
<p>$${p.precio}</p>
<p>Cupos: ${p.cupos}</p>
<p>${p.distancia}</p>

<button class="btnReservar">
Reservar
</button>

`;

const btn=
card.querySelector(".btnReservar");

btn.addEventListener("click",()=>reservar(p));

container.appendChild(card);

});

}

renderParqueaderos();

function reservar(parqueadero){

if(usuarioLogueado!=="true"){

alert("Debes iniciar sesión para reservar");
window.location.href="index.html";
return;

}

if(parqueadero.cupos===0){

alert("Parqueadero lleno");
return;

}

parqueadero.cupos--;

const nuevaReserva=
new Reserva(usuarioNombre,parqueadero,new Date());

reservas.push(nuevaReserva);

localStorage.setItem(
"reservas",
JSON.stringify(reservas)
);

alert("Reserva realizada");

renderParqueaderos();

}

function logout(){

localStorage.removeItem("usuarioLogueado");
localStorage.removeItem("usuarioNombre");

window.location.href="index.html";

}