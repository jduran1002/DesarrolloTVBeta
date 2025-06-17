import os

def listar_estructura(ruta, nivel=0):
    estructura = ""
    espacios = "│   " * nivel
    for item in os.listdir(ruta):
        ruta_item = os.path.join(ruta, item)
        estructura += f"{espacios}├── {item}\n"
        if os.path.isdir(ruta_item):
            estructura += listar_estructura(ruta_item, nivel + 1)
    return estructura

def guardar_estructura(ruta_proyecto):
    estructura = listar_estructura(ruta_proyecto)
    with open(os.path.join(ruta_proyecto, "estructura.txt"), "w", encoding='utf-8') as f:
        f.write(estructura)

if __name__ == "__main__":
    ruta_proyecto = os.path.dirname(os.path.abspath(__file__))
    guardar_estructura(ruta_proyecto)
    print("Estructura guardada en 'estructura.txt'")
