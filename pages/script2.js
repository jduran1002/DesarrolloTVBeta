document.addEventListener("DOMContentLoaded", function () {
  const fileInput = document.getElementById("fileInput");
  const fullscreenButton = document.getElementById("fullscreen");
  const clearPlaylistButton = document.getElementById("clearPlaylistButton");
  const errorMessage = document.getElementById("errorMessage");
  const playlistContainer = document.getElementById("playlist");
  const imageViewer = document.getElementById("imageViewer");

  let currentImageIndex = 0;
  let randomInterval;

  // Función para mostrar errores
  function showError(message) {
    errorMessage.textContent = message;
    errorMessage.style.color = "red";
    setTimeout(() => {
      errorMessage.textContent = "";
    }, 5000);
  }

  // Cargar imagen desde el equipo
  fileInput.addEventListener("change", function () {
    const file = this.files[0];
    if (file) {
      const fileURL = URL.createObjectURL(file);
      addToImagePlaylist(file.name, fileURL);
      imageViewer.src = fileURL;
      imageViewer.style.display = "block"; // Mostrar imagen
      startSlideshow(); // Iniciar slideshow si se agrega la primera imagen
    }
  });

  // Función para agregar imágenes a la lista de reproducción
  function addToImagePlaylist(name, src) {
    const playlistItem = document.createElement("div");
    playlistItem.className = "playlist-item";
    playlistItem.setAttribute("data-src", src);
    playlistItem.textContent = name; // Mostrar el nombre en la lista

    const img = document.createElement("img");
    img.src = src; // Imagen en miniatura
    img.alt = name;
    img.className = "img-thumbnail";

    playlistItem.appendChild(img);
    playlistContainer.appendChild(playlistItem); // Agregar el elemento a la lista

    // Evento para hacer clic en la imagen y mostrarla en el visor
    playlistItem.addEventListener("click", function () {
      currentImageIndex = Array.from(playlistContainer.children).indexOf(
        playlistItem
      );
      imageViewer.src = src; // Cambia la imagen en el visor
      clearInterval(randomInterval); // Detener el slideshow
      startSlideshow(); // Reiniciar el slideshow desde la imagen seleccionada
    });
  }

  // Función para iniciar el slideshow
  function startSlideshow() {
    const playlistItems = Array.from(playlistContainer.children);
    if (playlistItems.length > 0) {
      clearInterval(randomInterval); // Limpiar intervalos anteriores
      imageViewer.src =
        playlistItems[currentImageIndex].getAttribute("data-src"); // Mostrar la imagen actual
      randomInterval = setInterval(function () {
        currentImageIndex = (currentImageIndex + 1) % playlistItems.length; // Incrementar índice
        const nextItem = playlistItems[currentImageIndex];
        const imageURL = nextItem.getAttribute("data-src");
        imageViewer.src = imageURL; // Cambiar a la siguiente imagen
      }, 10000); // Cambia cada 10 segundos
    } else {
      showError("La lista de reproducción está vacía.");
    }
  }

  // Función para manejar la navegación con teclas
  document.addEventListener("keydown", function (event) {
    const playlistItems = Array.from(playlistContainer.children);
    if (event.key === "ArrowRight") {
      // Siguiente imagen
      currentImageIndex = (currentImageIndex + 1) % playlistItems.length;
      imageViewer.src =
        playlistItems[currentImageIndex].getAttribute("data-src");
    } else if (event.key === "ArrowLeft") {
      // Imagen anterior
      currentImageIndex =
        (currentImageIndex - 1 + playlistItems.length) % playlistItems.length;
      imageViewer.src =
        playlistItems[currentImageIndex].getAttribute("data-src");
    }
  });

  // Función para activar pantalla completa
  fullscreenButton.addEventListener("click", function () {
    if (imageViewer.requestFullscreen) {
      imageViewer.requestFullscreen();
    } else if (imageViewer.webkitRequestFullscreen) {
      // Safari
      imageViewer.webkitRequestFullscreen();
    } else if (imageViewer.msRequestFullscreen) {
      // IE/Edge
      imageViewer.msRequestFullscreen();
    }
  });

  document.addEventListener("fullscreenchange", function () {
    if (!document.fullscreenElement) {
      clearInterval(randomInterval); // Detener el slideshow si se sale de pantalla completa
    } else {
      startSlideshow(); // Reiniciar el slideshow si se vuelve a pantalla completa
    }
  });

  // Función para limpiar la lista de reproducción
  clearPlaylistButton.addEventListener("click", function () {
    playlistContainer.innerHTML = ""; // Limpia la lista en la interfaz
    imageViewer.src = ""; // Limpia el visor de imágenes
    currentImageIndex = 0; // Reiniciar el índice
    clearInterval(randomInterval); // Detener el slideshow
  });

  // Manejar zoom en la imagen
  imageViewer.addEventListener("click", function () {
    if (this.style.transform === "scale(1.5)") {
      this.style.transform = "scale(1)"; // Restablecer a tamaño normal
    } else {
      this.style.transform = "scale(1.5)"; // Aumentar tamaño
    }
  });
});
