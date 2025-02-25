# Importar librerías necesarias
import requests
from bs4 import BeautifulSoup
import pandas as pd

# URL base de la categoría
base_url = "https://modelplasticworld.com/es/78-135?page="

# Lista para almacenar los datos de todos los productos
data = []

# Bucle para recorrer todas las páginas
pagina = 1
while True:
    # Construir la URL de la página actual
    url = f"{base_url}{pagina}"
    print(f"Extrayendo productos de: {url}")
    
    # Obtener el contenido de la página
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Error al acceder a la página {pagina}. Deteniendo el proceso.")
        break  # Si hay un error, detener el bucle

    # Analizar el HTML con BeautifulSoup
    soup = BeautifulSoup(response.text, "html.parser")
    
    # Encontrar los productos que NO estén en "tvcms-prod-popup"
    productos = [
        prod for prod in soup.find_all("div", class_="tvproduct-name product-title")
        if not prod.find_parent(class_="tvcms-prod-popup")
    ]
    
    # Si no se encuentran productos, se asume que no hay más páginas y se detiene el bucle
    if not productos:
        print("No se encontraron más productos. Finalizando extracción.")
        break

    # Extraer información de cada producto
    for producto in productos:
        nombre = producto.find("h6").text.strip()
        url_producto = producto.find("a")["href"]
        data.append([nombre, url_producto])
    
    # Pasar a la siguiente página
    pagina += 1

# Crear DataFrame con los datos recopilados
df = pd.DataFrame(data, columns=["Nombre", "URL"])
df = df.drop_duplicates()

import pandas as pd
import requests
from bs4 import BeautifulSoup
import json

def extraer_datos_producto(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")

        # Extraer todos los scripts con JSON-LD
        script_tags = soup.find_all("script", type="application/ld+json")
        productos = []

        for script in script_tags:
            try:
                data = json.loads(script.string)

                # Filtrar solo objetos de tipo Product
                if isinstance(data, dict) and data.get("@type") == "Product":
                    producto = {
                        "Nombre": data.get("name", ""),
                        "Descripción": data.get("description", ""),
                        "Categoría": data.get("category", ""),
                        "Marca": data.get("brand", {}).get("name", ""),
                        "Precio": data.get("offers", {}).get("price", ""),
                        "Moneda": data.get("offers", {}).get("priceCurrency", ""),
                        "URL": data.get("offers", {}).get("url", ""),
                        "Disponibilidad": data.get("offers", {}).get("availability", ""),
                        "Fecha Precio Válido": data.get("offers", {}).get("priceValidUntil", "")
                    }
                    productos.append(producto)
            except json.JSONDecodeError:
                continue

        return productos[0] if productos else {"Error": "No se encontraron datos de producto"}

    return {"Error": "No se pudo acceder a la página"}

# Extraer datos para cada URL y añadirlos al df original
df_extraidos = pd.DataFrame([extraer_datos_producto(url) for url in df["URL"]])


df_extraidos = df_extraidos.drop(columns=['Nombre'])
df_final = df.merge(df_extraidos, on="URL",how="inner")
# Guardar en un CSV

# Mostrar los primeros registros
print(df_final.head())

import os
import shutil
import pandas as pd
from git import Repo

# Define el nombre de tu archivo CSV y el repositorio de GitHub
csv_file = 'productos.csv'
repo_url = 'https://github.com/Antonio4132/webs_scrapper.git'  # URL de tu repositorio
token = os.getenv('GITHUB_TOKEN')  # Reemplaza esto con tu token de GitHub
repo_dir = '/content/mi_repo'  # Ruta donde clonarás el repositorio

# Cargar el CSV de productos
df_final = pd.read_csv(csv_file)

# Aquí podrías agregar o modificar el dataframe si lo deseas

# Guarda el CSV actualizado en el entorno de Colab
df_final.to_csv(csv_file, index=False)

# Clonar el repositorio en Colab (si no existe ya)
if not os.path.exists(repo_dir):
    print(f"Clonando el repositorio en {repo_dir}...")
    Repo.clone_from(repo_url, repo_dir)

# Verificar si el archivo ya está en el repositorio
csv_dest = os.path.join(repo_dir, csv_file)
if os.path.abspath(csv_file) != os.path.abspath(csv_dest):
    # Copiar el archivo CSV al directorio del repositorio clonado solo si no es el mismo
    shutil.copy(csv_file, csv_dest)
else:
    print("El archivo CSV ya está en el directorio del repositorio.")

# Acceder al repositorio clonado
repo = Repo(repo_dir)

# Verificar que el directorio contiene un repositorio de git
if repo.bare:
    print("El repositorio está vacío o no es válido.")
else:
    # Añadir el archivo CSV actualizado al índice de Git
    index = repo.index
    index.add([csv_file])  # Ahora se encuentra en el directorio correcto

    # Realiza el commit con un mensaje
    commit_message = 'Actualización automática del archivo productos.csv'
    index.commit(commit_message)

    # Pushea los cambios al repositorio en GitHub usando HTTPS y el token
    origin = repo.remotes.origin
    origin.set_url(f'https://{token}@github.com/Antonio4132/webs_scrapper.git')  # Usando token para autenticación
    origin.push()

    print("Archivo CSV actualizado y enviado a GitHub.")
