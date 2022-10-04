import os.path

import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml import SafeLoader
import pandas as pd
from streamlit_authenticator import *

hashed_passwords = stauth.Hasher(['12345']).generate()
def login():
    with open('Data/config.YAML') as file:
        config = yaml.load(file, Loader=SafeLoader)

    authenticator = Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days'],
        config['preauthorized']
    )
    with st.sidebar:
        uploaded_file = st.file_uploader("Upload Allocation File")
        if uploaded_file is not None:
            data = pd.read_excel(uploaded_file)
            FilePath = "Files/Allocation.xlsx"
            writer = pd.ExcelWriter(FilePath, engine='xlsxwriter')
            data.to_excel(writer, sheet_name="Wroksheet", index=False)
            writer.save()
            writer.close()

    name, authentication_status, username = authenticator.login('Login', 'main')
    #
    # with open('Data/config.yaml') as file:
    #     config = yaml.load(file, Loader=SafeLoader)

    if authentication_status:
        with st.sidebar:
            authenticator.logout('Logout', 'main')
            st.write(f'Welcome *{name}*')
            return username
    elif authentication_status == False:
        st.error('Username/password is incorrect')
    elif authentication_status == None:
        st.warning('Please enter your username and password')

    with open('Data/config.YAML', 'w') as file:
        yaml.dump(config, file, default_flow_style=False)

