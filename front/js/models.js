class Usuario{

constructor(username,password,activo){

this.username = username;
this.password = password;
this.activo = activo;
this.logueado = false;

}

login(user,pass){

if(this.username === user && this.password === pass){

this.logueado = true;

localStorage.setItem("usuarioLogueado","true");
localStorage.setItem("usuarioNombre",user);

return true;

}

return false;

}

logout(){

this.logueado = false;

localStorage.removeItem("usuarioLogueado");
localStorage.removeItem("usuarioNombre");

}

verificarSesion(){

this.logueado =
localStorage.getItem("usuarioLogueado") === "true";

}

}


class Parqueadero{

constructor(nombre,direccion,ciudad,zona,precio,cupos,cubierto,distancia){

this.nombre = nombre;
this.direccion = direccion;
this.ciudad = ciudad;
this.zona = zona;
this.precio = precio;
this.cupos = cupos;
this.cubierto = cubierto;
this.distancia = distancia;

}

}


class Reserva{

constructor(usuario,parqueadero,fecha){

this.usuario = usuario;
this.parqueadero = parqueadero;
this.fecha = fecha;

}

}