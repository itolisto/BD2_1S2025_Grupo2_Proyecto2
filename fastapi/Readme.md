# Cómo iniciar un entorno virtual (`venv`) e instalar dependencias en Python para usar FastAPI


Posicionate en la carpeta FastAPI en `/backend/fastapi`

## 1. Crear un entorno virtual
Ejecuta el siguiente comando en tu terminal para crear un entorno virtual en la carpeta actual:

```bash
python -m venv venv
```

Esto creará una carpeta llamada `venv` que contendrá el entorno virtual.

---

## 2. Activar el entorno virtual
Dependiendo de tu sistema operativo, activa el entorno virtual:

- **Windows:**
  ```bash
  venv\Scripts\activate
  ```

- **macOS/Linux:**
  ```bash
  source venv/bin/activate
  ```

Después de activarlo, verás el nombre del entorno virtual (`venv`) en tu terminal.

---

## 3. Instalar dependencias desde `requirements.txt`
Ejecuta:

```bash
pip install -r requirements.txt

fastapi dev main.py
```

Esto instalará todas las dependencias listadas en el archivo.

---

## 4. Desactivar el entorno virtual
Cuando termines de trabajar, puedes desactivar el entorno virtual con:

```bash
deactivate
```


