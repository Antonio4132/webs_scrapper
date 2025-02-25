import os
import pandas as pd
import requests
import streamlit as st

# Define la URL del CSV en GitHub
csv_url = 'https://raw.githubusercontent.com/Antonio4132/webs_scrapper/main/productos.csv'

# Función para cargar el CSV desde GitHub
def cargar_csv():
    response = requests.get(csv_url)
    if response.status_code == 200:
        # Guardar el archivo en el servidor temporalmente
        with open('productos.csv', 'wb') as f:
            f.write(response.content)
        return pd.read_csv('productos.csv')
    else:
        return None

# Función principal de la app Streamlit
def app():
    st.title('Productos en Stock')

    # Botón para actualizar el CSV
    if st.button('Actualizar Datos'):
        st.write("Actualizando datos...")
        df_final = cargar_csv()
        if df_final is not None:
            # Filtrar productos en stock
            productos_en_stock_actuales = df_final[df_final['Disponibilidad'] == 'https://schema.org/InStock']
            productos_en_stock_guardados = pd.read_csv('productos.csv')[pd.read_csv('productos.csv')['Disponibilidad'] == 'https://schema.org/InStock']

            # Productos nuevos
            productos_nuevos_en_stock = productos_en_stock_actuales[~productos_en_stock_actuales['URL'].isin(productos_en_stock_guardados['URL'])]

            # 10 productos más baratos
            productos_en_stock_actuales['Precio'] = pd.to_numeric(productos_en_stock_actuales['Precio'], errors='coerce')
            productos_mas_baratos_en_stock = productos_en_stock_actuales.nsmallest(10, 'Precio')

            # Productos que han bajado de precio
            productos_comparados_en_stock = pd.merge(productos_en_stock_actuales, productos_en_stock_guardados, on='URL', suffixes=('_nuevo', '_antiguo'))
            productos_bajaron_precio_en_stock = productos_comparados_en_stock[productos_comparados_en_stock['Precio_nuevo'] < productos_comparados_en_stock['Precio_antiguo']]

            # Productos que han dejado de estar en stock
            productos_dejaron_de_estar_en_stock = productos_en_stock_guardados[~productos_en_stock_guardados['URL'].isin(productos_en_stock_actuales['URL'])]

            # Productos que han vuelto a estar en stock
            productos_volvieron_a_estar_en_stock = productos_en_stock_actuales[~productos_en_stock_actuales['URL'].isin(productos_en_stock_guardados['URL'])]

            # Mostrar tablas con Streamlit
            st.subheader('Productos Nuevos')
            st.write(productos_nuevos_en_stock)

            st.subheader('10 Productos Más Baratos')
            st.write(productos_mas_baratos_en_stock)

            st.subheader('Productos que han Bajado de Precio')
            st.write(productos_bajaron_precio_en_stock)

            st.subheader('Productos que Han Dejado de Estar en Stock')
            st.write(productos_dejaron_de_estar_en_stock)

            st.subheader('Productos que Han Volvuelto a Estar en Stock')
            st.write(productos_volvieron_a_estar_en_stock)

        else:
            st.write("Error al cargar los productos desde GitHub.")
    else:
        st.write("Haz clic en 'Actualizar Datos' para cargar los productos desde GitHub.")

if __name__ == "__main__":
    app()
