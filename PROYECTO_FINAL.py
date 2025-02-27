import os
import streamlit as st
import pandas as pd
import firebase_admin
from firebase_admin import credentials, firestore

# Verificar si Firebase ya está inicializado para evitar errores
if not firebase_admin._apps:
    try:
        cred = credentials.Certificate("moviescreds.json")  # Asegúrate de que el archivo existe
        firebase_admin.initialize_app(cred, {"projectId": "movies-94cb0"})  # Reemplázalo con tu ID de proyecto
    except Exception as e:
        st.error(f"Error al inicializar Firebase: {e}")

# Verifica que la inicialización fue exitosa antes de usar Firestore
if firebase_admin._apps:
    db = firestore.client()
else:
    st.error("No se pudo inicializar Firebase. Verifica las credenciales.")

@st.cache_data
def load_data(collection_name):
    try:
        docs = db.collection(collection_name).stream()
        data = [{**doc.to_dict(), 'id': doc.id} for doc in docs]
        return pd.DataFrame(data)
    except Exception as e:
        st.error(f"Error al cargar datos: {e}")
        return pd.DataFrame()

# Cargar los datos de la colección 'netflix'
df = load_data("netflix")

st.title("Dashboard de Filmes")

# Mostrar todos los filmes
show_films = st.sidebar.checkbox("Mostrar todos los filmes", value=True)
if show_films:
    st.header("Lista de Filmes")
    st.dataframe(df)
else:
    st.info("Selecciona el checkbox para mostrar la lista de filmes.")

# Buscar por nombre
search_name = st.sidebar.text_input("Buscar por nombre:")
if st.sidebar.button("Buscar Nombre"):
    if search_name:
        filtered_df = df[df['name'].str.contains(search_name, case=False, na=False)]
        st.write(f"Se encontraron {len(filtered_df)} filmes.")
        st.dataframe(filtered_df)
    else:
        st.info("Escribe un nombre para buscar.")

# Manejo de la columna 'director'
if 'director' in df.columns:
    directors = df['director'].dropna().unique().tolist()
else:
    st.warning("'director' no está en las columnas de los datos cargados.")
    directors = []

# Filtrar por director
selected_director = st.sidebar.selectbox("Selecciona un director", directors)
if st.sidebar.button("Filtrar por Director"):
    if selected_director:
        filtered_by_director = df[df['director'] == selected_director]
        st.write(f"Se encontraron {len(filtered_by_director)} filmes dirigidos por {selected_director}.")
        st.dataframe(filtered_by_director)
    else:
        st.info("Selecciona un director para filtrar.")

# Insertar un nuevo filme
with st.sidebar.form("insert_film_form"):
    st.header("Insertar un nuevo filme")
    new_name = st.text_input("Nombre:")
    new_genre = st.text_input("Género:")
    new_director = st.text_input("Director:")
    new_company = st.text_input("Compañía:")
    
    submit_button = st.form_submit_button("Insertar Filme")
    if submit_button:
        if new_name and new_genre and new_director and new_company:
            existing_films = df[df['name'].str.contains(new_name, case=False, na=False)]
            if not existing_films.empty:
                st.warning(f"El filme '{new_name}' ya existe en la base de datos.")
            else:
                new_film = {'name': new_name, 'genre': new_genre, 'director': new_director, 'company': new_company}
                db.collection('netflix').add(new_film)
                st.success(f"¡El filme '{new_name}' ha sido insertado exitosamente!")
                df = load_data("netflix")  # Recargar datos
        else:
            st.error("Por favor completa todos los campos del formulario.")
