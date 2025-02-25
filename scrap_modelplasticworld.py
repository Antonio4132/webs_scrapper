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
df_final.to_csv("productos.csv", index=False)

# Mostrar los primeros registros
print(df_final.head())
