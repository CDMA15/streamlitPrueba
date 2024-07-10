import streamlit as st
import requests

login_url = "https://wservices.boa.bo/ApiGateway/BoaApiGateway/"
hashing_url = "https://wservices.boa.bo/AuthenticationServices/MS_DataEncrypt/"

def login():

    # Inicializar el estado de autenticación si no está presente
    if "authentication_status" not in st.session_state:
        st.session_state["authentication_status"] = None

    if st.session_state["authentication_status"] is None:
        with st.form("login_form"):
            username = st.text_input("Usuario")
            password = st.text_input("Contraseña", type="password")
            submitted = st.form_submit_button("Iniciar sesión")

            if submitted:
                encryptPass = {
                    "value" : password,
                    "key" : ""
                }
                try:
                    # Aquí puedes agregar tu lógica de autenticación
                    response= requests.post(hashing_url+"encrypt/EncryptData", json=encryptPass)
                    if response.status_code ==200:
                        data = response.json()
                        if not data["hasError"]:
                            hashed=data["result"]
                    
                    login_data = {
                        "ip": "10.0.0.1",
                        "macAddress": "",
                        "systemCode": "SMS",
                        "platformLogin": "dotnet",
                        "userName": username,
                        "password": hashed
                    }
                    response2=requests.post(login_url+"auth/Login", json=login_data)
                    if response2.status_code == 200:
                        data = response2.json()
                        if not data["hasError"]:
                            token1 = data["result"]["token"]
                            usuarioID = data["result"]["userEmployeeId"]
                            st.session_state["userID"] = usuarioID
                            decrypt= {
                                "value":token1,
                                "key":""
                            }
                            response3 = requests.post(hashing_url+"encrypt/DecryptAes",json=decrypt)
                            if response3.status_code == 200:
                                data = response3.json()
                                if not data["hasError"]:
                                    token_final = data["result"]
                                    st.session_state["user_token"] = token_final
                            st.session_state["authentication_status"] = True
                            if st.session_state["authentication_status"]:
                                set_page("main")
                                st.rerun()
                    else:
                        st.error("Usuario o contraseña incorrectos")
                except requests.exceptions.RequestException as e:
                    st.error(f"Error al conectar con la API: {e}")
            else:
                    st.error("Usuario o contraseña incorrectos")

def main():
    with st.chat_message("assistant"):
        st.markdown("¿Desea subir una imagen de prueba para el reporte?")

    # Botones para la respuesta del usuario
    if st.button('Sí'):
        st.session_state.upload_approved = True
        # Mensaje del asistente
        with st.chat_message("assistant"):
            st.markdown('Adjunte una imagen como prueba del reporte')
    if st.button('No'):
        st.session_state.upload_approved = False
        with st.chat_message("assistant"):
            st.markdown("Está bien, gracias.")

    if 'upload_approved' in st.session_state and st.session_state.upload_approved:
        # Capturar imagen como respuesta del usuario
        uploaded_image = st.file_uploader("Cargar imagen", type=["jpg", "jpeg", "png"])

        # Mostrar la imagen cargada como mensaje de respuesta
        if uploaded_image is not None:
            with st.chat_message("user"):
                st.image(uploaded_image, caption="Imagen cargada")
            userID = st.session_state.get("userID")
            bytes_data = uploaded_image.getvalue()
            files = {
                "file": (uploaded_image.name, bytes_data, uploaded_image.type)
            }
            image_post = {
                "formSMSId": 20868,
                "idEmployee": userID
            }
            user_token = st.session_state.get("user_token")
            headers = {
                "Authorization": f"Bearer {user_token}",
                "accept": "*/*"
            }
            response4=requests.post(login_url+"attachment/Upload", params=image_post,files=files,headers=headers)
            if response4.status_code == 200:
                st.success('Saved')
            else:
                st.error(f"Error: {response4.status_code}")
                st.error(response4.text)

def set_page(page):
    st.experimental_set_query_params(page=page)
def get_page():
    query_params = st.experimental_get_query_params()
    return query_params.get("page", [None])[0]

def main_page():
    main()

def login_page():
    st.title("Inicio de Sesión")
    login()

if __name__ == "__main__":
    page = get_page()
    if page == "main" and st.session_state.get("authentication_status"):
        contador = 0
        st.session_state["first"] = None
        if st.session_state["first"] is None:
            st.title("SeMS")
            st.warning("Envía 'HOLA' para iniciar el reporte.\nRecuerda que todas las respuestas deben estar en MAYÚSCULAS")
            st.session_state["first"] = True
        main_page()
    else:
        login_page()