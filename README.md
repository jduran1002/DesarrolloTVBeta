# 🎥 Galería Multimedia - Plataforma Administrativa

Aplicación web construida con **Flask** para gestionar y visualizar imágenes y videos mediante una interfaz segura, con autenticación mediante **LDAP**, almacenamiento local y funcionalidades administrativas.

---

## 🚀 Características

- 🔐 **Inicio de sesión con autenticación LDAP**
- 👥 **Control de acceso para usuarios autorizados**
- 🖼️ **Subida y gestión de imágenes**
- 🎞️ **Subida y visualización de videos**
- 🧩 **Ordenamiento personalizado de imágenes**
- 🧹 **Funciones para limpiar galería y lista de reproducción**
- 📦 **API REST para listar archivos en JSON**
- ⚙️ **Rutas protegidas mediante sesiones**

---

## 🛠️ Requisitos

Instala las dependencias del proyecto con:

```bash
pip install -r requirements.txt
```

### Contenido recomendado para `requirements.txt`:

- `Flask`
- `ldap3`
- `Werkzeug`
- `openpyxl`
- `python-dotenv` (opcional, para manejo seguro de claves)

---

## ▶️ Ejecución

Inicia el servidor local con:

```bash
python app.py
```

El servidor quedará disponible en:

```
http://0.0.0.0:5000/
```

---

## 🔐 Autenticación

Se utiliza **LDAP** para autenticar usuarios con el siguiente servidor:

- **Host:** `ldaps://201.0.100.249`
- **Dominio:** `@pdc.cobranzasbeta.com.co`
- Solo usuarios autorizados en la lista `USUARIOS_PERMITIDOS` podrán iniciar sesión.

---

## 📄 Rutas Principales

| Ruta               | Método | Descripción                                  |
| ------------------ | ------ | -------------------------------------------- |
| `/`                | GET    | Redirige a la página de inicio de sesión     |
| `/sign-in.html`    | GET    | Página de login                              |
| `/dashboard.html`  | GET    | Panel principal (requiere login)             |
| `/upload`          | POST   | Subida de videos                             |
| `/upload_image`    | POST   | Subida de imágenes                           |
| `/list_videos`     | GET    | Devuelve lista de videos en formato JSON     |
| `/list_images`     | GET    | Devuelve lista de imágenes en formato JSON   |
| `/clear_gallery`   | POST   | Elimina todas las imágenes y su ordenamiento |
| `/clear_playlist`  | POST   | Elimina todos los videos                     |
| `/reorder_gallery` | POST   | Reordena las imágenes (orden personalizado)  |
| `/logout`          | GET    | Cierra la sesión actual                      |

---

## 📁 Estructura del Proyecto

```
Desarrollo-TV-Beta/
├── app.py                      # Código principal de la app Flask
├── pages/                      # Plantillas HTML
│   ├── sign-in.html
│   ├── dashboard.html
│   └── imagenes.html
├── assets/                     # Archivos estáticos
├── uploads/
│   ├── Imagenes/               # Carpeta para imágenes cargadas
│   │   └── order.json          # Archivo con el orden de imágenes
│   └── Videos/                 # Carpeta para videos cargados
├── requirements.txt
├── README.md
```

---

## ✅ Permisos de Usuario

Solo los siguientes usuarios pueden acceder:

```python
USUARIOS_PERMITIDOS = [
    'pgordillo', 'cpedraza', 'jochoa', 'ccastro',
    'yvega', 'sposada', 'lfajardo', 'ndiaz',
    'otorres', 'adiaz', 'nchavez', 'lmendoza',
    'jduran'
]
```

---

## 💡 Recomendaciones

- **Seguridad:** Mover `secret_key` y credenciales LDAP a un archivo `.env`.
- **Backups:** Realizar copias periódicas de las carpetas `uploads/Imagenes` y `uploads/Videos`.
- **Actualizaciones:** Implementar una interfaz para edición y eliminación individual de archivos.

---

## 🧑‍💻 Autor

**Equipo de Desarrollo - Cobranzas Beta**
📧 [jdduran@cobranzasbeta.com.co]
**Juan David Durán Lerma**

---

## 📅 Mantenimiento

Este proyecto se encuentra en producción y en constante mejora. Para nuevas funciones, contacta al equipo de desarrollo.

```

```
