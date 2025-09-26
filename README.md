# Sorteo San Valentín - CTS Turismo

Sistema completo para gestión de sorteo de San Valentín desarrollado con Django + Vue.js. Permite registro de participantes, verificación de email, panel administrativo para selección de ganadores y notificaciones automáticas.

## Características

- **Registro de participantes** con validación de emails duplicados
- **Verificación por email** con enlaces seguros
- **Creación de contraseña** post-verificación  
- **Panel administrativo** para gestión de participantes y sorteo
- **Selección aleatoria** de ganadores
- **Notificaciones por email** asíncronas (Celery + Redis)
- **Interfaz responsive** con Vue.js 3

## Tecnologías Utilizadas

### Backend
- **Python 3.11**
- **Django 5.2.6** - Framework web
- **Django REST Framework 3.16.1** - API REST
- **Celery 5.5.3** - Tareas asíncronas
- **Redis** - Broker para Celery
- **SQLite** - Base de datos (desarrollo)
- **SimpleJWT** - Autenticación JWT

### Frontend  
- **Vue.js 3.5.21** - Framework frontend
- **Vue Router 4.5.1** - Enrutamiento SPA
- **Axios 1.12.2** - Cliente HTTP
- **Vite** - Bundler y dev server

## Requisitos Previos

- Python 3.8+
- Node.js 16+
- Redis (local o en la nube)
- Git

## Instalación y Configuración

### 1. Clonar el Repositorio

```bash
git clone
cd prueba-cts
```

### 2. Configuración del Backend

#### Instalar dependencias
```bash
cd backend
pip install -r requirements.txt
```

#### Variables de entorno
```bash
# Copiar el archivo de ejemplo y editarlo con tus credenciales
cp .env.example .env
```

Editar `.env` con tus credenciales reales:
```env
# Redis Configuration (reemplazar con instancia de tu DB)
REDIS_URL=redis://default:tu_password@tu-redis-host:puerto

# Email Configuration (para desarrollo)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=tu-email@gmail.com
EMAIL_HOST_PASSWORD=tu-app-password
```

#### Migraciones de base de datos
```bash
python manage.py makemigrations
python manage.py migrate
```

#### Crear superusuario para admin
```bash
python manage.py createsuperuser
# Username: admin
# Password: admincts (o la que prefieras)
# Este será el admin que ingresará al panel administrativo y podrá sortear
```

### 3. Configuración del Frontend

```bash
cd frontend
npm install
```

### 4. Iniciar los Servicios

#### Terminal 1: Django Backend
```bash
cd backend
python manage.py runserver
```

#### Terminal 2: Celery Worker
```bash
cd backend
celery -A backend worker --loglevel=info --pool=solo
```
> **Nota**: En Windows usar `--pool=solo` para evitar errores de permisos

#### Terminal 3: Frontend Vue.js
```bash
cd frontend
npm run dev
```

## URLs de Acceso

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000/api
- **Admin Django**: http://localhost:8000/admin

## Endpoints de la API

### Endpoints Públicos

#### Estadísticas del Concurso
```http
GET /api/stats/
```
**Response**:
```json
{
  "total_registered": 45,
  "verified": 32,
  "participating": 30,
  "winner_selected": false
}
```

#### Registro de Participante
```http
POST /api/register/
Content-Type: application/json

{
  "full_name": "Diego Navarrete",
  "email": "diegonavarrete@email.com",
  "phone": "+56912345678"
}
```
**Response**:
```json
{
  "message": "¡Gracias por registrarte! Revisa tu correo para verificar tu cuenta.",
  "participant_id": 123,
  "verification_token": "abc123-def456-ghi789"
}
```

#### Verificación de Email
```http
POST /api/verify-email/
Content-Type: application/json

{
  "token": "abc123-def456-ghi789"
}
```

#### Creación de Contraseña
```http
POST /api/create-password/
Content-Type: application/json

{
  "token": "abc123-def456-ghi789",
  "password": "pass1234",
  "password_confirm": "pass1234"
}
```

### Endpoints Administrativos (Requieren Autenticación)

#### Login de Administrador
```http
POST /api/admin/login/
Content-Type: application/json

{
  "username": "admin",
  "password": "admincts"
}
```
**Response**:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "message": "Login exitoso"
}
```

#### Listar Participantes
```http
GET /api/admin/participants/
Authorization: Bearer <token>

# Filtros opcionales:
GET /api/admin/participants/?search=diego&status=verified
```

#### Seleccionar Ganador
```http
POST /api/admin/select-winner/
Authorization: Bearer <token>
Content-Type: application/json

{
  "count": 1
}
```

#### Obtener Ganadores
```http
GET /api/admin/winners/
Authorization: Bearer <token>
```

#### Notificar Ganadores
```http
POST /api/admin/notify-winners/
Authorization: Bearer <token>
```

## Decisiones Técnicas

### Arquitectura
- **Separación backend/frontend**: Permite escalabilidad independiente y posible desarrollo de apps móviles
- **API REST**: Estándar de la industria, fácil integración y testing
- **Celery + Redis**: Emails asíncronos para mejor UX y rendimiento

### Base de Datos
- **SQLite para desarrollo**: Simplicidad en setup inicial
- **Modelos relacionales**: Participant/Winner con integridad referencial
- **UUIDs para tokens**: Mayor seguridad que IDs secuenciales

### Seguridad
- **JWT Authentication**: Stateless, escalable para microservicios
- **Validación de tokens**: Expiración automática y verificación
- **CORS configurado**: Solo orígenes permitidos
- **Contraseñas hasheadas**: Django's PBKDF2 por defecto

### Frontend
- **Vue 3 Composition API**: Mejor organización del código
- **SPA con Vue Router**: Navegación fluida sin recargas
- **CSS en componente específico**: Si bien para futuras mejoras se puede elegir componentes reutilizables con Tailwind, en este caso preferí que fueran modificables solo dentro de cada uno.
- **Axios interceptors**: Manejo centralizado de errores

### Emails
- **Templates HTML + Plain text**: Compatibilidad con todos los clientes
- **Console backend para desarrollo**: Evita configuración SMTP compleja
- **Celery para producción**: Envío asíncrono, no bloquea requests

## Configuración de Emails

### Desarrollo (Console Backend)
Los emails se muestran en la consola del backend. No requiere configuración SMTP.

### Producción
Actualizar en `settings.py`:
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'emailreal@gmail.com'
EMAIL_HOST_PASSWORD = 'apppassword-real'
```

## Testing

### Test Manual de la API
```bash
cd backend
python test_api.py
```

### Flujo Completo de Usuario
1. Ir a http://localhost:5173
2. Registrarse con email válido
3. Verificar token en consola del backend
4. Acceder a link de verificación
5. Crear contraseña
6. Admin: Login en /admin/login
7. Ver participantes y realizar sorteo

## 🎨 Capturas de Pantalla

### Flujo del Usuario
![Página Principal](screenshots/screenshot-home.png)
*Página principal con información del sorteo*

![Registro](screenshots/registro.png)
*Formulario de registro de participantes*

![Registro Exitoso](screenshots/siguientes-pasos.png)
*Modal de confirmación tras registro exitoso*

![Respuesta de Celery](screenshots/celery-response.png)
*Respuesta de Celery en la terminal*

![Verificación Email](screenshots/verificacion-email.png)
*Pantalla para verificar email y crear contraseña*

### Panel Administrativo
![Login Admin](screenshots/login-adm.png)
*Pantalla de login para administradores*

![Panel administrativo](screenshots/panel-administrativo.png)
*Gestión de participantes registrados*

![Lista Participantes](screenshots/participantes-adm.png)
*Gestión de participantes registrados. Se pueden ver detalles o reenviar correo de registro.*

![Detalles](screenshots/detalles-participantes.png)
*Detalles de cada participante* 

![Sorteo](screenshots/sorteo.png)
*Pantalla de selección de ganador*

![Ganador Seleccionado](screenshots/ganador.png)
*Resultado del sorteo con ganador*

![Celery: Correo Ganador](screenshots/ganador-celery.png)
*Envia correo al ganador del sorteo*

![Sorteo cerrado](screenshots/sorteo-cerrado.png)
*Una vez haya un ganador, el concurso se cierra.*

## 🔧 Mejoras Futuras

- [ ] **Tests automatizados** (pytest, Vue Test Utils)
- [ ] **Paginación** en listado de participantes
- [ ] **Logs estructurados** (ELK Stack)
- [ ] **Rate limiting** para endpoints públicos
- [ ] **Docker Compose** para desarrollo
- [ ] **CI/CD Pipeline** (GitHub Actions)
- [ ] **Notificaciones push** para administradors
- [ ] **Dashboard con métricas** en tiempo real
- [ ] **Backup automático** de base de datos
- [ ] **Multi-idioma** (i18n)

## 📄 Licencia

Este proyecto fue desarrollado como prueba técnica.
