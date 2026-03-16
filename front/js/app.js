const usuario = new Usuario("admin","1234",true);

usuario.verificarSesion();

const btnLogin = document.getElementById("btnLogin");
const saludoUsuario = document.getElementById("saludoUsuario");

function actualizarUI(){

if(usuario.logueado){

btnLogin.textContent="Logout";
saludoUsuario.textContent=`Hola ${usuario.username}`;

}else{

btnLogin.textContent="Login";
saludoUsuario.textContent="";

}

}

actualizarUI();

btnLogin.addEventListener("click",()=>{

if(usuario.logueado){

usuario.logout();
actualizarUI();

}else{

document
.getElementById("modalLogin")
.classList.remove("hidden");

}

});

document
.getElementById("loginSubmit")
.addEventListener("click",()=>{

const user =
document.getElementById("username").value;

const pass =
document.getElementById("password").value;

if(usuario.login(user,pass)){

actualizarUI();

document
.getElementById("modalLogin")
.classList.add("hidden");

}else{

alert("Credenciales incorrectas");

}

});

document
.getElementById("closeModal")
.addEventListener("click",()=>{

document
.getElementById("modalLogin")
.classList.add("hidden");

});

document
.getElementById("formBusqueda")
.addEventListener("submit",(e)=>{

e.preventDefault();

const ciudad =
document.getElementById("ciudad").value;

const zona =
document.getElementById("zona").value;

const precioMax =
document.getElementById("precioMax").value;

const activarPrecio =
document.getElementById("activarPrecio").checked;

const soloDisponibles =
document.getElementById("soloDisponibles").checked;

let precio=null;

if(activarPrecio && precioMax!==""){

precio=parseInt(precioMax);

}

const filtros={
ciudad,
zona,
precio,
soloDisponibles
};

localStorage.setItem(
"filtroBusqueda",
JSON.stringify(filtros)
);

window.location.href="parqueadero.html";

});