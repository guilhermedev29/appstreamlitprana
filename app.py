
import streamlit as st
import pandas as pd
import sqlite3
import subprocess
import random
import string


def alterar_estilo():
    with open("style.css", "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

alterar_estilo()

conn = sqlite3.connect('dados.db')
c = conn.cursor()

# Criando a tabela de usuários, se ela não existir
c.execute('''CREATE TABLE IF NOT EXISTS users
             (username TEXT PRIMARY KEY, password TEXT, authentication_key TEXT)''')

c.execute('''CREATE TABLE IF NOT EXISTS itens
             (data TEXT, dia TEXT, mes TEXT, ano TEXT, tipo_movimento TEXT, valor_total TEXT,
             valor_fracionado TEXT, forma_pagamento TEXT, cliente TEXT, cliente_novo TEXT,
             atendimentos TEXT, terapeuta TEXT, detalhe_gastos TEXT, observacoes TEXT, alimentado_por TEXT, username TEXT)''')

def main():
    logged_in = False
    
    page = st.sidebar.radio("Escolha uma opção:", ["Login", "Cadastro"])
    
    if page == "Login":
        logged_in = login()
        if logged_in:
            if st.session_state['username'] == 'admin' or st.session_state['username'] == 'admin2':
                redirecionar_para_pagina_admin()
            else:
                redirecionar_para_pagina_tabela()
    else:
        cadastrar()

def login():
    st.image("testar.jpg", use_column_width=True)
    st.title("Login")
    username = st.text_input("Usuário")
    password = st.text_input("Senha", type="password")
    
    if st.button("Login"):
        if verificar_credenciais(username, password):
            st.success("Login realizado com sucesso!")
            st.session_state['username'] = username
            return True
        else:
            st.error("Usuário ou senha incorretos")
    return False

def verificar_credenciais(username, password):
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    return c.fetchone() is not None

def cadastrar():
    st.title("Cadastro")
    novo_username = st.text_input("Novo Usuário")
    novo_password = st.text_input("Nova Senha", type="password")
    
    if st.button("Cadastrar"):
        authentication_key = gerar_authentication_key(novo_username)
        adicionar_usuario(novo_username, novo_password, authentication_key)
        st.success("Cadastro realizado com sucesso!")
        st.info(f"Sua chave de autenticação é: {authentication_key}. Guarde-a em um local seguro.")


def adicionar_usuario(username, password, authentication_key):
    c.execute("INSERT INTO users (username, password, authentication_key) VALUES (?, ?, ?)", (username, password, authentication_key))
    conn.commit()

def gerar_authentication_key(username):
    # Pegar as três primeiras letras do nome do usuário
    prefixo = username[:3].upper()
    # Gerar dois números aleatórios
    numeros_aleatorios = ''.join(random.choices(string.digits, k=2))
    # Concatenar o prefixo com os números aleatórios
    authentication_key = prefixo + numeros_aleatorios
    return authentication_key


def redirecionar_para_pagina_tabela():
    subprocess.run(["streamlit", "run", "main_tabela.py"])

def redirecionar_para_pagina_admin():
    subprocess.run(["streamlit", "run", "painel_admin.py"])

if __name__ == "__main__":
    main()