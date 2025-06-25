from flask import Flask, request, jsonify, render_template, redirect, url_for, flash, send_from_directory, session
import os
import ssl
from ldap3 import Server, Connection, ALL, Tls
from werkzeug.utils import secure_filename
from datetime import timedelta
import json
from functools import wraps

# Configurar la aplicación Flask
app = Flask(__name__, 
            template_folder='pages', 
            static_folder='assets', 
            static_url_path='/assets')

app.secret_key = 'tu_clave_secreta'  # Cambia esto por una clave segura
app.permanent_session_lifetime = timedelta(minutes=40)  # Tiempo de vida de la sesión

# Configuraciones
UPLOAD_FOLDER = r'C:\xampp\htdocs\Desarrollo TV Beta\uploads\Videos'
IMAGE_FOLDER = r'C:\xampp\htdocs\Desarrollo TV Beta\uploads\Imagenes'
ORDER_FILE = os.path.join(IMAGE_FOLDER, 'order.json')
USERS_FILE = os.path.join(os.path.dirname(__file__), 'users.json')
ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'avi', 'mov', 'wmv'}
ALLOWED_IMAGE_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}

# Usuarios permitidos (con persistencia en archivo)
if os.path.exists(USERS_FILE):
    with open(USERS_FILE, encoding="utf-8") as f:
        USUARIOS_PERMITIDOS = json.load(f)
else:
    USUARIOS_PERMITIDOS = [
        'pgordillo', 'cpedraza', 'jochoa', 'ccastro',
        'yvega', 'sposada', 'lfajardo', 'ndiaz',
        'otorres', 'adiaz', 'nchavez', 'lmendoza',
        'jduran'
    ]

def save_usuarios_permitidos():
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(USUARIOS_PERMITIDOS, f, ensure_ascii=False, indent=2)

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(IMAGE_FOLDER, exist_ok=True)

tls_configuration = Tls(validate=ssl.CERT_NONE)
server = Server('ldaps://201.0.100.249', use_ssl=True, tls=tls_configuration, get_info=ALL)

def autenticar_usuario(username, password):
    user_dn = f"{username.lower()}@pdc.cobranzasbeta.com.co"
    try:
        conn = Connection(server, user=user_dn, password=password, auto_bind=True)
        if conn.bind() and username.lower() in [user.lower() for user in USUARIOS_PERMITIDOS]:
            print("Autenticación exitosa")
            return True
        else:
            print("Error de autenticación")
            return False
    except Exception as e:
        print(f"Error al autenticar: {e}")
        return False

# NUEVO: Validar usuario en LDAP (sin password, sólo existencia)
def usuario_existe_en_dominio(username):
    search_user = "jduran@pdc.cobranzasbeta.com.co"  # Usuario de consulta AD, debe tener permisos de búsqueda
    search_pass = "Beta.2025*+"  # Cambia esto a la contraseña real del usuario de búsqueda
    try:
        conn = Connection(
            server,
            user=search_user,
            password=search_pass,
            auto_bind=True
        )
        search_base = 'DC=pdc,DC=cobranzasbeta,DC=com,DC=co'
        search_filter = f'(&(objectClass=user)(sAMAccountName={username}))'
        conn.search(search_base, search_filter, attributes=["cn"])
        return len(conn.entries) > 0
    except Exception as e:
        print(f"Error buscando usuario en AD: {e}")
        return False

def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def list_videos_from_folder(folder):
    videos = []
    for filename in os.listdir(folder):
        if allowed_file(filename, ALLOWED_VIDEO_EXTENSIONS):
            video_url = f'/uploads/{filename}'
            size = os.path.getsize(os.path.join(folder, filename))
            videos.append({"name": filename, "size": size, "url": video_url})
    return videos

def get_image_order():
    if os.path.exists(ORDER_FILE):
        with open(ORDER_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except Exception:
                return []
    return []

def save_image_order(order):
    with open(ORDER_FILE, "w", encoding="utf-8") as f:
        json.dump(order, f)

def list_images_from_folder(folder):
    images = []
    filenames = [f for f in os.listdir(folder) if allowed_file(f, ALLOWED_IMAGE_EXTENSIONS)]
    order = get_image_order()
    # Si hay orden guardado, usarlo
    if order:
        ordered_filenames = [f for f in order if f in filenames]
        remaining = [f for f in filenames if f not in order]
        filenames = ordered_filenames + remaining
    for filename in filenames:
        image_url = f'/images/{filename}'
        size = os.path.getsize(os.path.join(folder, filename))
        images.append({"name": filename, "size": size, "url": image_url})
    return images

# Decorador para proteger rutas
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            flash('Debes iniciar sesión primero.', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def home():
    return redirect(url_for('index'))

@app.route('/sign-in.html')
def index():
    return render_template('sign-in.html')

@app.route('/usuarios.html')
@login_required
def usuarios():
    return render_template('usuarios.html')

@app.route('/dashboard.html')
@login_required
def dashboard():
    videos = list_videos_from_folder(UPLOAD_FOLDER)
    images = list_images_from_folder(IMAGE_FOLDER)
    return render_template('dashboard.html', videos=videos, images=images)

@app.route('/imagenes.html', methods=['GET'])
@login_required
def imagenes():
    images = list_images_from_folder(IMAGE_FOLDER)
    return render_template('imagenes.html', images=images)

@app.route('/video.html', methods=['GET'])
def video():
    videos = list_videos_from_folder(UPLOAD_FOLDER)
    return render_template('video.html', videos=videos)

@app.route('/imagen.html', methods=['GET'])
def imagen_auto():
    images = list_images_from_folder(IMAGE_FOLDER)
    return render_template('imagen.html', images=images)

@app.route('/pages/sign-in.html', methods=['GET'])
def sign_in():
    return render_template('sign-in.html')


@app.route('/pages/dashboard.html', methods=['GET'])
@login_required
def dashboard_page():
    return render_template('dashboard.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    if username is None or password is None:
        flash('Por favor, complete todos los campos.', 'error')
        return redirect(url_for('index'))
    if autenticar_usuario(username, password):
        session['username'] = username
        session.permanent = True
        return redirect(url_for('dashboard'))
    else:
        flash('Acceso denegado. Credenciales incorrectas o usuario no permitido.', 'error')
        return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('Has cerrado sesión.', 'success')
    return redirect(url_for('index'))

@app.before_request
def before_request():
    if 'username' in session:
        session.modified = True

@app.route('/uploads/<path:filename>')
def serve_video(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/images/<path:filename>')
def serve_image(filename):
    if allowed_file(filename, ALLOWED_IMAGE_EXTENSIONS):
        return send_from_directory(IMAGE_FOLDER, filename)
    else:
        return jsonify({"error": "Archivo no encontrado o tipo de archivo inválido"}), 404

@app.route('/list_videos', methods=['GET'])
def list_videos():
    videos = list_videos_from_folder(UPLOAD_FOLDER)
    return jsonify(videos)

@app.route('/list_images', methods=['GET'])
def list_images():
    images = list_images_from_folder(IMAGE_FOLDER)
    return jsonify(images)

@app.route('/upload_image', methods=['POST'])
@login_required
def upload_image():
    file = request.files.get('imageFile')
    if not file or file.filename == '':
        msg = 'No se seleccionó ningún archivo.'
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'error': msg}), 400
        flash(msg, 'error')
        return redirect(url_for('dashboard'))
    if allowed_file(file.filename, ALLOWED_IMAGE_EXTENSIONS):
        filename = secure_filename(file.filename)
        target_file = os.path.join(IMAGE_FOLDER, filename)
        file.save(target_file)
        # Al subir la imagen, si hay un archivo de orden, la añadimos al final
        order = get_image_order()
        if filename not in order:
            order.append(filename)
            save_image_order(order)
        msg = f'Imagen {filename} subida con éxito'
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': True, 'filename': filename}), 200
        flash(msg, 'success')
        return redirect(url_for('dashboard'))
    msg = 'Solo se permiten archivos JPG, JPEG, PNG y GIF.'
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'success': False, 'error': msg}), 400
    flash(msg, 'error')
    return redirect(url_for('dashboard'))

@app.route('/clear_gallery', methods=['POST'])
@login_required
def clear_gallery():
    error = None
    for filename in os.listdir(IMAGE_FOLDER):
        if allowed_file(filename, ALLOWED_IMAGE_EXTENSIONS):
            try:
                file_path = os.path.join(IMAGE_FOLDER, filename)
                os.remove(file_path)
            except Exception as e:
                error = str(e)
    # Borra también el archivo de orden
    if os.path.exists(ORDER_FILE):
        try:
            os.remove(ORDER_FILE)
        except Exception as e:
            error = str(e)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if error:
            return jsonify({'success': False, 'error': error}), 500
        return jsonify({'success': True, 'message': 'Galería de imágenes limpiada con éxito.'}), 200
    if error:
        flash(f'Error al limpiar la galería: {error}', 'error')
    else:
        flash('Galería de imágenes limpiada con éxito.', 'success')
    return redirect(url_for('dashboard'))

@app.route('/clear_playlist', methods=['POST'])
@login_required
def clear_playlist():
    error = None
    for filename in os.listdir(UPLOAD_FOLDER):
        if allowed_file(filename, ALLOWED_VIDEO_EXTENSIONS):
            try:
                file_path = os.path.join(UPLOAD_FOLDER, filename)
                os.remove(file_path)
            except Exception as e:
                error = str(e)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if error:
            return jsonify({'success': False, 'error': error}), 500
        return jsonify({'success': True, 'message': 'Lista de reproducción limpiada con éxito.'}), 200
    if error:
        flash(f'Error al limpiar la lista: {error}', 'error')
    else:
        flash('Lista de reproducción limpiada con éxito.', 'success')
    return redirect(url_for('dashboard'))

@app.route('/upload', methods=['POST'])
@login_required
def upload_file():
    file = request.files.get('videoFile')
    if not file or file.filename == '':
        msg = 'No se seleccionó ningún archivo.'
        flash(msg, 'error')
        return redirect(url_for('dashboard'))
    if allowed_file(file.filename, ALLOWED_VIDEO_EXTENSIONS):
        filename = secure_filename(file.filename)
        target_file = os.path.join(UPLOAD_FOLDER, filename)
        file.save(target_file)
        flash(f'Video {filename} subido con éxito', 'success')
        return redirect(url_for('dashboard'))
    msg = 'Solo se permiten archivos MP4, AVI, MOV y WMV.'
    flash(msg, 'error')
    return redirect(url_for('dashboard'))

@app.route('/reorder_gallery', methods=['POST'])
@login_required
def reorder_gallery():
    # Espera un JSON: { "order": ["img1.jpg", "img2.jpg", ...] }
    data = request.get_json()
    order = data.get('order', [])
    # Filtrar solo los archivos que existen realmente
    filenames = [f for f in os.listdir(IMAGE_FOLDER) if allowed_file(f, ALLOWED_IMAGE_EXTENSIONS)]
    order = [f for f in order if f in filenames]
    # Guarda el orden
    try:
        save_image_order(order)
        return jsonify({'success': True}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# --- API de usuarios permitidos ---

@app.route('/list_users', methods=['GET'])
@login_required
def list_users():
    return jsonify(USUARIOS_PERMITIDOS)

@app.route('/add_user', methods=['POST'])
@login_required
def add_user():
    data = request.get_json()
    username = data.get('username', '').strip().lower()
    if not username:
        return jsonify({'success': False, 'error': 'Usuario inválido.'}), 400

    # 1. ¿Ya está registrado?
    if username in [u.lower() for u in USUARIOS_PERMITIDOS]:
        return jsonify({'success': False, 'error': 'Usuario ya existe.'}), 400

    # 2. ¿Existe en el dominio?
    if not usuario_existe_en_dominio(username):
        return jsonify({'success': False, 'error': 'Usuario no existe en el dominio.'}), 400

    # 3. Lo agregas
    USUARIOS_PERMITIDOS.append(username)
    save_usuarios_permitidos()
    return jsonify({'success': True, 'message': f'Usuario {username} agregado.'})

@app.route('/remove_user', methods=['POST'])
@login_required
def remove_user():
    data = request.get_json()
    username = data.get('username', '').strip().lower()
    for u in USUARIOS_PERMITIDOS:
        if u.lower() == username:
            USUARIOS_PERMITIDOS.remove(u)
            save_usuarios_permitidos()
            return jsonify({'success': True, 'message': f'Usuario {username} eliminado.'})
    return jsonify({'success': False, 'error': 'Usuario no encontrado.'}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)