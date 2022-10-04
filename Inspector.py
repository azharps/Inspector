import streamlit_option_menu
from streamlit import config
from streamlit_option_menu import option_menu
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
import xlsxwriter
from io import BytesIO
import time
import threading
import os
import numpy as np
from openpyxl import load_workbook
import streamlit_authenticator as stauth
import yaml
from yaml import SafeLoader
from streamlit_authenticator import *
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
import time
import warnings
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.wait import WebDriverWait

warnings.filterwarnings('ignore')

st.set_page_config("TITLE TREATMENT INSPECTOR", "📊", initial_sidebar_state="expanded", layout="wide", )

hide_menu_style = """
        <style>
        #MainMenu {visibility: hidden;}
        .css-2ykyy6 {
                    display: none;
                }
        </style>
        """
st.markdown(hide_menu_style, unsafe_allow_html=True)
hide_top_side = """
        <style>
               .css-18e3th9 {
                    padding-top: 0.5rem;
                    padding-bottom: 3.5rem;
                    padding-left: 5rem;
                    padding-right: 5rem;
                }
               .css-1d391kg {
                    padding-top: 0.5rem;
                    padding-right: 5rem;
                    padding-bottom: 3.5rem;
                    padding-left: 5rem;
                }
                .stButton>button {
                    color: #FFFFF;
                    border-radius: 100%;
                    height: 3.5em;
                    width: 3.5em;
                }
        </style>
        """
st.markdown(hide_top_side, unsafe_allow_html=True)

if not st.session_state:
    st.session_state.user_name = None
    st.session_state.add_marketplace = ""
    st.session_state.add_PT = None
    st.session_state.add_IC = None
    st.session_state.select_ASIN = None
    st.session_state.select_Index = 0
    st.session_state.select_GL = None
    st.session_state.counter = False
    st.session_state.selected_theme = 0
    st.session_state.primaryColor = "#f63366"
    st.session_state.backgroundColor = "#FFFFFF"
    st.session_state.secondaryBackgroundColor = "#f0f2f6"
    st.session_state.textColor = "#262730"
    st.session_state.is_dark_theme = False
    st.session_state.first_time = True

def get_html(URL,ASIN):
    # navigate webpage
    chrome_options = Options()
    chrome_options.add_argument("user-agent=UA")

    # set the browser Headless.
    chrome_options.add_argument("--headless")

    # open web browser
    driver = webdriver.Chrome('.\chromedriver.exe', options=chrome_options)
    driver.get(URL)

    html = driver.page_source
    driver.quit()
    html_path = "Data/HTML/" + str(ASIN) + ".html"
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)
        f.close()

def login():
    with open('Data/config.YAML') as file:
        sconfig = yaml.load(file, Loader=SafeLoader)

    authenticator = Authenticate(
        sconfig['credentials'],
        sconfig['cookie']['name'],
        sconfig['cookie']['key'],
        sconfig['cookie']['expiry_days'],
        sconfig['preauthorized']
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

def select_theme(set_theme):
    if set_theme == "Light":
        config.set_option("theme.primaryColor", "#f63366")
        config.set_option("theme.backgroundColor", "#FFFFFF")
        config.set_option(
            "theme.secondaryBackgroundColor", "#f0f2f6")
        config.set_option("theme.textColor", "#262730")
    elif set_theme == "Blue":
        config.set_option("theme.primaryColor", "#d33682")
        config.set_option("theme.backgroundColor", "#002b36")
        config.set_option(
            "theme.secondaryBackgroundColor", "#586e75")
        config.set_option("theme.textColor", "#fafafa")
    elif set_theme == "Green":
        config.set_option("theme.primaryColor", "#E694FF")
        config.set_option("theme.backgroundColor", "#00172B")
        config.set_option(
            "theme.secondaryBackgroundColor", "#0083B8")
        config.set_option("theme.textColor", "#C6CDD4")
    elif set_theme == "Solarized":
        config.set_option("theme.primaryColor", "#d33682")
        config.set_option("theme.backgroundColor", "#002b36")
        config.set_option(
            "theme.secondaryBackgroundColor", "#586e75")
        config.set_option("theme.textColor", "#fafafa")

def streamlit_menu():
    with st.sidebar:
        selected = option_menu(
            menu_title="Menu",  # required
            options=["Dashboard", "Add/Modify TRP", "Instructions"],  # required
            icons=["house", "book", "envelope"],  # optional
            menu_icon="cast",  # optional
            default_index=0,  # optional
            orientation="vertical",
        )
    return selected

@st.experimental_memo(persist="disk")
def read_html(ASIN):
    path = "Data/HTML/" + str(ASIN) + ".html"
    while os.path.exists(path):
        HtmlFile = open(path, 'r', encoding='utf-8')
        source_code = HtmlFile.read()
        return source_code

@st.experimental_memo
def load_datafile():
    if os.path.exists("Files/Allocation.xlsx"):
        loaded_datafile = pd.read_excel("Files/Allocation.xlsx")
        loaded_datafile = loaded_datafile.replace(np.nan, '', regex=True)
        return loaded_datafile
    else:
        return pd.DataFrame()

def load_savedfile():
    filename = "Data/Save_File/" + str(st.session_state.add_marketplace) + "_" + str(
        st.session_state.add_PT) + "_" + str(st.session_state.user_name) + ".csv"
    saved_datafile = pd.read_csv(filename)
    saved_datafile = saved_datafile.replace(np.nan, '', regex=True)
    return saved_datafile

class UI:
    def __init__(self):
        self.THEMES = None
        self.theme = None
        self.modified_dataframe = None
        self.saved_data = None
        self.add_GL = None
        self.filename = None
        self.select_ASIN = None
        self.workable_file = None
        self.add_IC = None
        self.add_PT = None
        self.add_marketplace = None
        self.pass_word = None
        self.user_name = None
        self.Ate = pd.read_excel("Files/Datafile.xlsx", sheet_name="attributes_to_be_extracted")
        self.TRP = pd.read_excel("Files/Datafile.xlsx", sheet_name="TRP")
        self.Dept = pd.read_excel("Files/Datafile.xlsx", sheet_name="Dept")
        self.MP_Lang = pd.read_excel("Files/Datafile.xlsx", sheet_name="MP_Lang")
        self.filename = "Data/Save_File/" + str(st.session_state.add_marketplace) + "_" + str(
            st.session_state.add_PT) + "_" + str(st.session_state.user_name) + ".csv"

    def save_file(self, workable_file):
        if st.session_state.user_name is not None and str(st.session_state.add_PT) in self.workable_file[
            'product_type'].unique() and str(st.session_state.add_marketplace) in self.workable_file[
            'MP'].unique():
            self.workable_file.reset_index(drop=True, inplace=True)
            self.filename = "Data/Save_File/" + str(st.session_state.add_marketplace) + "_" + str(
                st.session_state.add_PT) + "_" + str(st.session_state.user_name) + ".csv"
            if 'seller_data' not in self.workable_file.columns:
                self.workable_file['seller_data'] = ""
                self.workable_file.to_csv(self.filename, index=False)
            else:
                self.workable_file.to_csv(self.filename, index=False)

    def options_top_menu(self):
        self.workable_file = load_datafile()
        if self.workable_file.empty == 0:
            with st.expander("Options", expanded=True):
                with st.container():
                    colt0, colt1, colt2, colt3, colt4 = st.columns([1, 1, 1, 1, 1])
                    with colt0:
                        self.select_User = st.selectbox(
                            "User ID",
                            list(self.workable_file['User ID'].unique()), key=972)
                        st.session_state.user_name = self.select_User

                    with colt1:
                        self.add_Date = st.selectbox(
                            "Date",
                            list(self.workable_file['Date'].unique()), key=973)
                    with colt2:
                        self.add_marketplace = st.selectbox(
                            "Marketplace",
                            list(self.workable_file['MP'].unique()), key=2)
                        st.session_state.add_marketplace = self.add_marketplace
                    with colt3:
                        self.add_PT = st.selectbox(
                            "Select PT",
                            (list(self.workable_file['product_type'].unique())))
                        st.session_state.add_PT = self.add_PT
                    with colt4:
                        self.add_IC = st.selectbox(
                            "Item Classification",
                            (list(set(self.TRP['item_classification'].loc[self.TRP['PT'] == self.add_PT]))))
                        st.session_state.add_IC = self.add_IC

    def top_menu(self):
        self.filename = "Data/Save_File/" + str(st.session_state.add_marketplace) + "_" + str(
            st.session_state.add_PT) + "_" + str(st.session_state.user_name) + ".csv"
        if os.path.exists(self.filename):
            self.workable_file = load_savedfile()
        else:
            self.workable_file = load_datafile()
            self.workable_file = pd.DataFrame(
                self.workable_file.loc[self.workable_file['User ID'] == str(st.session_state.user_name)])
            self.workable_file.reset_index(drop=True, inplace=True)
            self.save_file(self.workable_file)

        if st.session_state.user_name is not None and str(st.session_state.add_PT) in self.workable_file[
            'product_type'].unique() and str(st.session_state.add_marketplace) in self.workable_file['MP'].unique():
            with st.expander("Options", expanded=False):
                with st.container():
                    col1, col2, col5, col3, col4, col_web, col_dwld = st.columns([1, 1, 1, 1, 1, 1, 1])
                    with col1:
                        self.control = st.checkbox("Control", key=101)
                        self.trp1 = st.checkbox("TRP1", key=99)

                    with col2:
                        self.trp2 = st.checkbox("TRP2", key=98)
                        self.trp3 = st.checkbox("TRP3", key=97)
                    with col3:
                        self.filename = "Data/Save_File/" + str(st.session_state.add_marketplace) + "_" + str(
                            st.session_state.add_PT) + "_" + str(st.session_state.user_name) + ".csv"
                        if st.button("Load"):
                            if os.path.exists(self.filename):
                                self.workable_file = load_savedfile()
                            else:
                                self.save_file(self.workable_file)
                    with col5:
                        self.trp4 = st.checkbox("TRP4", key=96)
                        self.trp5 = st.checkbox("TRP5", key=95)
                    with col_web:
                        if st.button("Offline"):
                            self.save_html(set="All")

                    with col_dwld:
                        fil_nam = str(
                            str(st.session_state.add_marketplace) + "_" + str(st.session_state.add_PT) + "_" + str(
                                st.session_state.user_name) + ".xlsx")

                        if self.workable_file is not None and os.path.exists(self.filename):
                            final_data = pd.DataFrame(pd.read_csv(self.filename, encoding="utf8"))
                            final_data = final_data.replace(np.nan, '', regex=True)
                            output = BytesIO()
                            writer = pd.ExcelWriter(output, engine='xlsxwriter')
                            final_data.to_excel(writer, index=False, sheet_name='Sheet1')

                            writer.save()
                            processed_data = output.getvalue()
                            st.download_button(label='📥  Download',
                                               data=processed_data,
                                               file_name=fil_nam)

    def modify_data(self, sel_asin, column_name, updated_data, modified_dataframe):
        for index1, row1 in modified_dataframe.iterrows():
            if modified_dataframe.loc[index1, 'ASIN'] == sel_asin:
                modified_dataframe.at[index1, column_name] = updated_data
                modified_dataframe.to_csv(self.filename, index=False)

    def title_menu(self):
        with st.container():
            col0, col11, col12, col_prev, col_save, col_next, col1 = st.columns([1, 0.5, 2, 0.7, 0.7, 0.7, 2])
            if st.session_state.user_name is not None and str(st.session_state.add_PT) in self.workable_file[
                'product_type'].unique() and str(st.session_state.add_marketplace) in self.workable_file['MP'].unique():
                with col0:
                    st.metric("User", st.session_state.user_name)

                with col11:
                    st.metric("MP", st.session_state.add_marketplace)
                with col12:
                    st.metric("PT", st.session_state.add_PT)
                if int(st.session_state.select_Index) != 0:
                    with col_prev:
                        if st.button("Prev", key=123):
                            st.session_state.select_Index = int(st.session_state.select_Index) - 1
                with col_save:
                    if st.button("Save", key=77):
                        st.write("Save")
                        self.modify_data("", "", "", "")
                with col_next:
                    if st.button("Next", key=124):
                        st.session_state.select_Index = int(st.session_state.select_Index) + 1

                with col1:
                    st.session_state.select_ASIN = self.workable_file['ASIN'][int(st.session_state.select_Index)]
                    self.save_html(set=None)
                    st.header(st.session_state.select_ASIN)

        with st.container():
            if st.session_state.user_name is not None and str(st.session_state.add_PT) in self.workable_file[
                'product_type'].unique() and str(st.session_state.add_marketplace) in self.workable_file['MP'].unique():
                self.filename2 = "Data/Save_File/" + str(st.session_state.add_marketplace) + "_" + str(
                    st.session_state.add_PT) + "_" + str(st.session_state.user_name) + ".xlsx"
                col_title, col2 = st.columns([30, 4])
                self.saved_data = load_savedfile()
                self.saved_data.reset_index(drop=True, inplace=True)
                if self.saved_data is not None and os.path.exists(self.filename):
                    with col_title:
                        st.subheader(str(
                            self.saved_data['item_name'].loc[
                                self.saved_data['ASIN'] == st.session_state.select_ASIN].values[0]))
                    with col2:
                        # st.metric("Index ", len(self.workable_file['ASIN']))
                        st.metric("Index",
                                  str(self.workable_file.loc[
                                          self.workable_file['ASIN'] == st.session_state.select_ASIN].index[
                                          0] + 1) + "/" + str(len(self.workable_file['ASIN'])))

    def bottom_menu(self):
        check_list = ["for", ","]
        if self.workable_file is not None:
            with st.container():
                self.back_col1, bacl_col2 = st.columns([1, 1])
                if st.session_state.user_name is not None and str(st.session_state.add_PT) in self.workable_file[
                    'product_type'].unique() and str(st.session_state.add_marketplace) in self.workable_file[
                    'MP'].unique():
                    if os.path.exists(self.filename):
                        self.saved_data = load_savedfile()
                    else:
                        self.saved_data = self.workable_file

                    if self.saved_data is not None and os.path.exists(self.filename):
                        self.data1 = self.TRP.loc[self.TRP['MP'] == st.session_state.add_marketplace]
                        self.data2 = self.data1.loc[self.data1['PT'] == st.session_state.add_PT]
                        self.data3 = self.data2.loc[self.data2['item_classification'] == st.session_state.add_IC]
                        self.trp1_format = str(self.data3['TRP1'].values[0]).replace('[', '').replace(']', '').split(
                            '+')
                        self.final_trp = ""
                        for words1 in self.trp1_format:
                            words1 = words1.strip()
                            if words1 not in check_list:
                                self.final_trp = self.final_trp + str(
                                    self.saved_data[words1].loc[
                                        self.saved_data['ASIN'] == st.session_state.select_ASIN].values[
                                        0]) + " "
                            else:
                                self.final_trp = self.final_trp + str(words1) + " "

                        self.final_trp = self.final_trp.replace(" , ", ", ")
                        st.subheader("TRP 1: " + self.final_trp)
                        self.modify_data(st.session_state.select_ASIN, "TRP 1", self.final_trp, self.saved_data)

    def body_menu(self):
        if st.session_state.user_name is not None and self.workable_file is not None:
            if os.path.exists(self.filename):
                self.saved_data = load_savedfile()
            else:
                self.saved_data = self.workable_file
            self.n = 30
            with st.container():
                col_left, col_r1, col_r2 = st.columns([2.4, 1, 1])
                with col_left:
                    self.link = str(
                        self.MP_Lang['merchant_name'].loc[
                            self.MP_Lang['marketplace'] == str(st.session_state.add_marketplace)].values[
                            0]) + str(st.session_state.select_ASIN)
                    self.path = "Data/HTML/" + str(st.session_state.select_ASIN) + ".html"
                    if not os.path.exists(self.path):
                        t2 = threading.Thread(target=get_html(self.link, st.session_state.select_ASIN))
                        t2.start()
                        t2.join()

                    source_code = read_html(st.session_state.select_ASIN)

                    components.html(source_code, scrolling=True, height=400)

                    self.from_mp = self.Ate.loc[(self.Ate['MP'] == st.session_state.add_marketplace)]
                    self.from_PT = pd.DataFrame(self.from_mp.loc[(self.from_mp['PT'] == st.session_state.add_PT)])
                for col in self.from_PT.columns:
                    for index, row in self.from_PT.iterrows():
                        if row[col] == "Y" and (str(col) != "item_name"):

                            self.n = self.n + 1
                            self.item_classification = str(self.saved_data['item_classification'].loc[
                                                               self.saved_data[
                                                                   'ASIN'] == st.session_state.select_ASIN].values[
                                                               0])
                            default_data = str(
                                self.saved_data[col].loc[
                                    self.saved_data['ASIN'] == st.session_state.select_ASIN].values[0])
                            if self.n % 2 != 0:
                                default_data = str(
                                    self.saved_data[col].loc[
                                        self.saved_data['ASIN'] == st.session_state.select_ASIN].values[0])
                                with col_r1:
                                    mod_data1 = st.text_input(col, default_data, key=self.n * 7)
                                    if mod_data1 != default_data:
                                        self.modify_data(st.session_state.select_ASIN, col, mod_data1, self.saved_data)


                            else:
                                default_data = str(
                                    self.saved_data[col].loc[
                                        self.saved_data['ASIN'] == st.session_state.select_ASIN].values[0])
                                with col_r2:
                                    mod_data2 = st.text_input(col, default_data, key=self.n * 8)
                                    if mod_data2 != default_data:
                                        self.modify_data(st.session_state.select_ASIN, col, mod_data2, self.saved_data)

    def save_html(self, set=None):
        if st.session_state.select_ASIN is not None and set == "All":
            asin_list = list(self.workable_file['ASIN'])
            for i in range(len(asin_list)):
                self.link = str(
                    self.MP_Lang['merchant_name'].loc[
                        self.MP_Lang['marketplace'] == str(st.session_state.add_marketplace)].values[
                        0]) + str(asin_list[i])
                ix2 = threading.Thread(target=get_html, args=(self.link, st.session_state.select_ASIN,))
                ix2.daemon = True
                ix2.start()
                ix2.join()
        if st.session_state.select_ASIN is not None and set is None:
            self.path = "Data/HTML/" + str(st.session_state.select_ASIN) + ".html"
            self.link = str(
                self.MP_Lang['merchant_name'].loc[
                    self.MP_Lang['marketplace'] == str(st.session_state.add_marketplace)].values[
                    0]) + str(st.session_state.select_ASIN)

            if not os.path.exists(self.path):
                ix1 = threading.Thread(target=get_html, args=(self.link, st.session_state.select_ASIN,))
                ix1.daemon = True
                ix1.start()
                ix1.join()
            else:
                pass

if __name__ == "__main__":
    obj = UI()
    with st.sidebar:
        if st.button("Theme"):
            options = ["Light", "Blue", "Green", "Solarized"]
            select_theme(options[st.session_state.selected_theme])
            st.session_state.selected_theme += 1
            if st.session_state.selected_theme == 3:
                st.session_state.selected_theme = 0

    selected = streamlit_menu()
    if selected == "Dashboard":
        st.session_state.user_name = login()
        filename = "Data/Save_File/" + str(st.session_state.add_marketplace) + "_" + str(
            st.session_state.add_PT) + "_" + str(st.session_state.user_name) + ".csv"
        if st.session_state.user_name is not None:
            if os.path.exists("Files/Allocation.xlsx") or os.path.exists(filename):
                obj.options_top_menu()
                obj.top_menu()
                x2 = threading.Thread(target=obj.title_menu(), args=())
                obj.body_menu()
                x4 = threading.Thread(target=obj.bottom_menu(), args=())
                x2.daemon = True
                x4.daemon = True
                x2.start()
                x4.start()
                x2.join()
                x4.join()
    if selected == "Add/Modify TRP":
        st.title(f"Enter Data to {selected}")
        col1, col2, col3, col4, col5 = st.columns([0.5, 1, 1, 1, 0.5])
        Ate = pd.read_excel("Files/Datafile.xlsx", sheet_name="attributes_to_be_extracted")
        TRP = pd.read_excel("Files/Datafile.xlsx", sheet_name="TRP")
        Dept = pd.read_excel("Files/Datafile.xlsx", sheet_name="Dept")
        MP_Lang = pd.read_excel("Files/Datafile.xlsx", sheet_name="MP_Lang")
        TRP_List = ['Control', 'TRP1', 'TRP2', 'TRP3', 'TRP4', 'TRP5']
        with col1:
            new_MP = st.text_input("MP", "US", key=4567)
        with col2:
            new_GL = st.selectbox("GL", ("Hardlines", "Softlines", "Consumables"), key=4669)
        with col3:
            new_PT = st.text_input("PT", "SHIRT", key=4572)
        with col4:
            new_IC = st.selectbox("Item Classification", ("base_product", "variation_parent"), key=4569)
        with col5:
            new_TRP = st.selectbox("TRP Type", list(TRP_List), key=4369)
        new_TRP_Input = st.text_input(new_TRP, "[brand] + [department] + [item_type_name]")
        updated_TRP = pd.DataFrame()
        if st.button("Add"):
            # TRP.reset_index(inplace=True)
            if new_MP in list(TRP['MP'].unique()) and new_GL in list(TRP['GL'].unique()) and new_PT in list(
                    TRP['PT'].unique()) and new_IC in list(TRP['item_classification'].unique()):
                updated_TRP = TRP
                data1 = TRP.loc[TRP['MP'] == new_MP]
                data2 = data1.loc[data1['GL'] == new_GL]
                data3 = data2.loc[data2['PT'] == new_PT]
                data4 = data3.loc[data3['item_classification'] == new_IC]
                data4[new_TRP] = new_TRP_Input
                index_num = int(data4[data4[new_TRP] == new_TRP_Input].index.values[0])
                updated_TRP.loc[index_num, new_TRP] = new_TRP_Input
                FilePath = "Files/Datafile.xlsx"
                writer = pd.ExcelWriter(FilePath, engine='xlsxwriter')
                Ate.to_excel(writer, sheet_name="attributes_to_be_extracted", index=False)
                updated_TRP.to_excel(writer, sheet_name="TRP", index=False)
                Dept.to_excel(writer, sheet_name="Dept", index=False)
                MP_Lang.to_excel(writer, sheet_name="MP_Lang", index=False)
                writer.save()
                writer.close()
            else:
                updated_TRP = pd.read_excel("Files/Datafile.xlsx", sheet_name="TRP")
                updated_TRP = updated_TRP.append(
                    {'MP': new_MP, 'GL': new_GL, 'PT': new_PT, 'item_classification': new_IC, new_TRP: new_TRP_Input},
                    ignore_index=True)
                FilePath = "Files/Datafile.xlsx"
                # os.remove(FilePath)
                writer = pd.ExcelWriter(FilePath, engine='xlsxwriter')
                Ate.to_excel(writer, sheet_name="attributes_to_be_extracted", index=False)
                updated_TRP.to_excel(writer, sheet_name="TRP", index=False)
                Dept.to_excel(writer, sheet_name="Dept", index=False)
                MP_Lang.to_excel(writer, sheet_name="MP_Lang", index=False)
                writer.save()
                writer.close()

        with st.expander("Existing TRP Data", expanded=True):
            chkTRP = pd.read_excel("Files/Datafile.xlsx", sheet_name="TRP")
            colk1, colk2, colk3, colk4 = st.columns([1, 1, 1, 1])
            with colk1:
                MP_chk = st.selectbox("MP", list(TRP['MP'].unique()))
                if MP_chk in list(TRP['MP'].unique()):
                    data1 = TRP.loc[TRP['MP'] == MP_chk]
                    with colk2:
                        GL_chk = st.selectbox("GL", list(data1['GL'].unique()))
                        if GL_chk in list(TRP['GL'].unique()):
                            data2 = data1.loc[data1['GL'] == GL_chk]
                            with colk3:
                                PT_chk = st.selectbox("PT", list(TRP['PT'].unique()))
                                if PT_chk in list(TRP['PT'].unique()):
                                    data3 = data2.loc[data2['PT'] == PT_chk]
                                    with colk4:
                                        IC_chk = st.selectbox("item_classification",
                                                              list(TRP['item_classification'].unique()))
                                        if IC_chk in list(TRP['item_classification'].unique()):
                                            data4 = data3.loc[data3['item_classification'] == IC_chk]
            with st.container():
                st.write(data4, use_container_width=True)
    if selected == "Instructions":
        st.title(f"{selected}")
        cold1,cold2 = st.columns([1,1])
        with cold1:
            st.title("For Dashboard :")
            st.header("Login using: admin and Password: 12345")
            st.header("Upload Allocation file using sidebar menu")
            st.header("Download worked file as .xlsx file using download button")
        with cold2:
            st.title("For Add/Modify TRP :")
            st.head08oer("Search for existing TRP menu provided")
            st.header("Mention the MP and PT in the Text box")
            st.header("Select the GL, Item Classification and TRP Type from dropdown")
            st.header("Sample TRP : [brand] + [department] + [item_type_name] + . . . . .")

