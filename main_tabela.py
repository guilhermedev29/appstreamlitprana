import streamlit as st
import pandas as pd
import sqlite3

def alterar_estilo():
    with open("style.css", "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

alterar_estilo()

# Conexão com o banco de dados SQLite
conn = sqlite3.connect('dados.db')
c = conn.cursor()

# Verifique se a tabela "itens" já existe
c.execute('''CREATE TABLE IF NOT EXISTS itens
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
             data TEXT, dia TEXT, mes TEXT, ano TEXT, tipo_movimento TEXT, valor_total TEXT,
             valor_fracionado TEXT, forma_pagamento TEXT, cliente TEXT, cliente_novo TEXT,
             atendimentos TEXT, terapeutas TEXT, detalhe_gastos TEXT, observacoes_predefinidas TEXT, observacoes_escritas TEXT, alimentado_por TEXT, chave_seguranca TEXT)''')

def renderizar_ultima_observacao_por_cliente(cliente_pesquisa):
    # Construa a consulta SQL baseada no nome do cliente pesquisado
    if cliente_pesquisa:
        query = f"SELECT data, observacoes_predefinidas FROM itens WHERE cliente LIKE '%{cliente_pesquisa}%' ORDER BY ROWID DESC LIMIT 1"
    else:
        st.warning("Por favor, insira um nome de cliente para pesquisar.")
        return

    # Execute a consulta SQL
    c.execute(query)
    data = c.fetchone()

    # Se houver dados retornados, exiba a última data e observação do cliente
    if data:
        st.header(f"Último Procedimento do Cliente {cliente_pesquisa}")
        st.write(f"Data: {data[0]}")
        st.write(f"Observação: {data[1]}")
    else:
        st.write(f"Nenhum procedimento encontrado para o cliente {cliente_pesquisa}.")

def main_tabela():
    st.title("Tabela de Controle")

    # Crie duas colunas para os inputs
    col5, col1, col2, col3, col4, col6 = st.columns(6)

    # Adicione os inputs em cada coluna
    with col5:
        chave_seguranca = st.text_input("C.Segurança", type="password")
    with col1:
        data = st.date_input("Data")

    with col2:
        tipo_movimento = st.selectbox("T.Movimento", ["", "Entrada", "Saída", "Garantia de Satisfação"])
        valor_total = st.text_input("V Total $")
        valor_fracionado = st.text_input("V Fracionado $")
        forma_pagamento = st.selectbox("F. de Pagamento", ["", "Transferência", "Cartão", "À Vista"])

    with col3:
        cliente = st.text_input("Cliente")
        cliente_novo = st.selectbox("Cliente Novo", ["", "Sim", "Não"])
        atendimentos = st.selectbox("T.Atendimentos", ["", "Massagem", "Pacote", "Evento", "Produtos", "P. A.", "P. A. Massagem", "Atendimento Evento", "Vale Presente", "V. P. Massagem"])

        # Atualizar a lista de terapeutas disponíveis na interface
        terapeutas_disponiveis = obter_terapeutas()
        terapeutas_disponiveis.insert(0, "")
        terapeuta = st.selectbox("Terapeuta", terapeutas_disponiveis)

    with col4:
        detalhe_gastos_options = [
            "", "Alimentação", "Transporte", "Salario", "Imposto", "Outros Gastos",
            "Diária Terapeuta", "Conta de Água", "Conta de Luz", "Produtos",
            "Recarga Celular", "Conta de Internet", "G. Administrativos", "Aluguel",
            "Não escrever"
        ]

        detalhe_gastos = st.selectbox("D.Gasto", detalhe_gastos_options)
        observacoes_predefinidas_options = [
            "PAC 1/3", "PAC 2/3", "PAC 3/3", "PAC 1/5 PM28270124MM1",
            "PAC 2/5 PM28270124MM2", "PAC 3/5 PM08070124MM3", "PAC 4/5 PM08070124MM4",
            "PAC 5/5 PM08070124MM5", "PAC 1/10", "PAC 2/10", "PAC 3/10", "PAC 4/10",
            "PAC 5/10", "PAC 6/10", "PAC 7/10", "PAC 8/10", "PAC 9/10", "PAC 10/10",
            "Quizena"
        ]

        observacoes_predefinidas = st.selectbox("Pacotes", observacoes_predefinidas_options)
        observacoes_escritas = st.text_area("Observações Escritas", height=100)  # Campo de texto multilinha para observações

    with col6:
        username = obter_usuario_por_chave(chave_seguranca)  # Obtem o nome de usuário com base na chave de segurança
        st.text_input("Alimentado por", value=username, disabled=True)  # Campo preenchido automaticamente

    if not verificar_chave_seguranca(chave_seguranca):
        st.error("Chave de Segurança Inválida, adicione a chave para aparecer mais informações.")
        return

    if st.button("Adicionar Item"):
        st.warning("Você tem certeza que deseja adicionar os itens a tabela?")
        # Mostrar mensagem de confirmação
        st.session_state.confirmation = True

    if st.session_state.get('confirmation', False):
        if st.button("Confirmar Adição"):
            # Converter a data para string no formato desejado
            data_value = data.strftime('%Y-%m-%d')

            # Coletar os dados necessários
            tipo_movimento_value = tipo_movimento
            valor_total_value = valor_total
            valor_fracionado_value = valor_fracionado
            forma_pagamento_value = forma_pagamento
            cliente_value = cliente
            cliente_novo_value = cliente_novo
            atendimentos_value = atendimentos
            terapeuta_value = terapeuta
            detalhe_gastos_value = detalhe_gastos
            observacoes_predefinidas_value = observacoes_predefinidas
            observacoes_escritas_value = observacoes_escritas
            alimentado_por_value = username
            chave_seguranca_value = chave_seguranca

            # Chamar a função adicionar_item
            adicionar_item(data_value, tipo_movimento_value, valor_total_value, valor_fracionado_value, forma_pagamento_value,
                        cliente_value, cliente_novo_value, atendimentos_value, terapeuta_value, detalhe_gastos_value,
                        observacoes_predefinidas_value, observacoes_escritas_value, alimentado_por_value, chave_seguranca_value)

            st.success("Item adicionado com sucesso.")
            st.session_state.confirmation = False  # Resetar o estado de confirmação
            st.experimental_rerun()

    st.header("Tabela")
    # Renderizar a tabela aqui
    renderizar_tabela(chave_seguranca)
    st.write("")

    # Adicione um componente para pesquisar o último procedimento de um cliente
    cliente_pesquisa = st.text_input("Pesquisar Último Procedimento por Cliente")
    if st.button("Pesquisar"):
        renderizar_ultima_observacao_por_cliente(cliente_pesquisa)

def obter_terapeutas():
    # Consulta ao banco de dados para obter os terapeutas disponíveis
    c.execute("SELECT nome FROM terapeutas")
    terapeutas = c.fetchall()
    return [terapeuta[0] for terapeuta in terapeutas]

def adicionar_item(data, tipo_movimento, valor_total, valor_fracionado, forma_pagamento,
                   cliente, cliente_novo, atendimentos, terapeuta, detalhe_gastos, observacoes_predefinidas, observacoes_escritas, alimentado_por, chave_seguranca):
    # Verifica se a chave de segurança é válida
    if not verificar_chave_seguranca(chave_seguranca):
        st.error("Chave de Segurança Inválida")
        return

    # Verifica se o cliente é novo e seu nome já está na base de dados
    if cliente_novo == "Sim":
        c.execute("SELECT * FROM itens WHERE cliente = ?", (cliente,))
        existing_client = c.fetchone()
        if existing_client:
            st.warning(f"O cliente '{cliente}' já existe na base de dados. Verifique se é realmente um cliente novo.")
            return

    # Inserção dos dados no banco de dados
    c.execute('''INSERT INTO itens (data, dia, mes, ano, tipo_movimento, valor_total, valor_fracionado, forma_pagamento, cliente, cliente_novo, atendimentos, terapeutas, detalhe_gastos, observacoes_predefinidas, observacoes_escritas, alimentado_por, chave_seguranca)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
              (data, data.split('-')[2], data.split('-')[1], data.split('-')[0], tipo_movimento, valor_total, valor_fracionado, forma_pagamento, cliente, cliente_novo, atendimentos, terapeuta, detalhe_gastos, observacoes_predefinidas, observacoes_escritas, alimentado_por, chave_seguranca))
    conn.commit()

def renderizar_tabela(chave_seguranca):
    # Selecionar apenas o último registro adicionado pelo usuário correspondente à chave de segurança
    c.execute('''SELECT data, dia, mes, ano, tipo_movimento, valor_total, valor_fracionado, forma_pagamento, cliente, cliente_novo, atendimentos, terapeutas, detalhe_gastos, observacoes_predefinidas, observacoes_escritas, alimentado_por, chave_seguranca FROM itens WHERE chave_seguranca = ? ORDER BY ROWID DESC LIMIT 1''', (chave_seguranca,))
    data = c.fetchall()
    if data:
        df = pd.DataFrame(data, columns=["Data", "Dia", "Mês", "Ano", "Tipo de Movimento", "V Total $", "V Fracionado $", "F. de Pagamento", "Cliente", "C. Novo", "T. de Atendimentos", "Terapeuta", "Detalhe de Gastos", "Observações Pré-definidas", "Observações Escritas", "Alimentado por", "Chave de Segurança"])

        # Adicionando uma coluna de numeração única
        df.insert(0, 'ID', range(1, 1 + len(df)))

        # Exibir a tabela
        st.dataframe(df)
    else:
        st.write("Nenhum item encontrado para esta chave de segurança.")

def verificar_chave_seguranca(chave_seguranca):
    c.execute("SELECT * FROM users WHERE authentication_key = ?", (chave_seguranca,))
    result = c.fetchone()
    if result:
        return True  # A chave de segurança foi encontrada no banco de dados
    else:
        return False  # A chave de segurança não foi encontrada no banco de dados

def obter_usuario_por_chave(chave_seguranca):
    c.execute("SELECT username FROM users WHERE authentication_key = ?", (chave_seguranca,))
    result = c.fetchone()
    if result:
        return result[0]  # Retorna o nome de usuário se encontrado
    else:
        return ""  # Retorna uma string vazia se a chave de segurança não estiver associada a nenhum usuário

if __name__ == "__main__":
    if 'confirmation' not in st.session_state:
        st.session_state.confirmation = False
    main_tabela()
