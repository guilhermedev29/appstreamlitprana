import streamlit as st
import pandas as pd
import sqlite3
import uuid
from dateutil.relativedelta import relativedelta
import datetime as dt
from datetime import datetime
import matplotlib.pyplot as plt
from collections import defaultdict  
# Conexão com o banco de dados SQLite
conn = sqlite3.connect('dados.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS itens
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
             data TEXT, dia TEXT, mes TEXT, ano TEXT, tipo_movimento TEXT, valor_total TEXT,
             valor_fracionado TEXT, forma_pagamento TEXT, cliente TEXT, cliente_novo TEXT,
             atendimentos TEXT, terapeutas TEXT, detalhe_gastos TEXT, observacoes TEXT, observacoes_escritas TEXT, alimentado_por TEXT, username TEXT)''')
def alterar_estilo():
    with open("style.css", "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

alterar_estilo()
def main_admin():
    st.title("Página de Administração")

    # Caixa de seleção para escolher a maneira de filtrar
    st.markdown("## Escolher a maneira de filtrar")
    filtro_por_cliente = st.checkbox("Filtrar por cliente")
    filtro_por_data = st.checkbox("Filtrar por data")
    filtro_por_tipo_movimento = st.checkbox("Filtrar por tipo de movimento")
    filtro_por_terapeuta = st.checkbox("Filtrar por terapeuta")
    filtro_por_tipo_atendimento = st.checkbox("Filtrar por tipo de atendimento")
    filtro_por_detalhe_gasto = st.checkbox("Filtrar por detalhe de gasto")  # Adicionado filtro por detalhe de gasto

    # Botões para exportar a tabela
    st.markdown("## Exportar Tabela")
    export_format = st.selectbox("Selecione o formato de exportação:", ["Excel", "CSV", "PDF"])
    if st.button("Exportar"):
        if export_format == "Excel":
            exportar_para_excel()
        elif export_format == "CSV":
            exportar_para_csv()
        elif export_format == "PDF":
            exportar_para_pdf()

    # Adicione filtros à tabela conforme selecionado pelo usuário
    st.markdown("## Filtros")
    filtro_ano = filtro_mes = filtro_dia = None
    if filtro_por_data:
        st.markdown("### Filtrar por data")
        filtro_ano = st.selectbox("Ano:", ["", 2022, 2023, 2024])  # Atualize com os anos necessários
        filtro_mes = st.selectbox("Mês:", ["", "January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"])

        if filtro_mes:
            mes_numero = datetime.strptime(filtro_mes, "%B").month
            filtro_dia = st.number_input("Dia:", min_value=0, max_value=31, step=1)
            if filtro_dia > 0:
                data_filtro = datetime(filtro_ano, mes_numero, filtro_dia)
            else:
                data_filtro = datetime(filtro_ano, mes_numero, 1)
        else:
            mes_numero = None
            data_filtro = None

    if filtro_por_tipo_movimento:
        filtro_tipo_movimento = st.selectbox("Filtrar por tipo de movimento:", ["", "Entrada", "Saída", "Garantia de Satisfação"])
    else:
        filtro_tipo_movimento = ""

    if filtro_por_cliente:
        filtro_cliente = st.text_input("Filtrar por cliente:")
    else:
        filtro_cliente = ""

    if filtro_por_terapeuta:
        terapeutas = obter_terapeutas()  # Obter lista de terapeutas do banco de dados
        filtro_terapeuta = st.selectbox("Filtrar por terapeuta:", [""] + terapeutas)  # Adicionar uma opção vazia e as terapeutas disponíveis
    else:
        filtro_terapeuta = ""

    if filtro_por_tipo_atendimento:
        tipos_atendimento = obter_tipos_atendimento()  # Obter lista de tipos de atendimento do banco de dados
        filtro_tipo_atendimento = st.selectbox("Filtrar por tipo de atendimento:", [""] + tipos_atendimento)  # Adicionar uma opção vazia e os tipos de atendimento disponíveis
    else:
        filtro_tipo_atendimento = ""

    if filtro_por_detalhe_gasto:
        detalhes_gastos = obter_detalhes_gastos()  # Obter lista de detalhes de gastos do banco de dados
        filtro_detalhe_gasto = st.selectbox("Filtrar por detalhe de gasto:", [""] + detalhes_gastos)  # Adicionar uma opção vazia e os detalhes de gastos disponíveis
    else:
        filtro_detalhe_gasto = ""

    # Renderizar a tabela com base nos filtros
    renderizar_tabela(filtro_ano, filtro_mes, filtro_dia, filtro_tipo_movimento, filtro_cliente, filtro_terapeuta, filtro_tipo_atendimento, filtro_detalhe_gasto)

    # Calcular e exibir o faturamento de cada terapeuta
    calcular_faturamento_terapeutas()



def calcular_faturamento_terapeutas():
    # Consulta ao banco de dados para obter o faturamento de cada terapeuta
    c.execute("SELECT terapeutas, SUM(valor_total) AS total_faturado FROM itens GROUP BY terapeutas")
    data = c.fetchall()
    df_faturamento = pd.DataFrame(data, columns=["Terapeuta", "Total Faturado"])

    # Exibir a tabela com o faturamento de cada terapeuta
    st.subheader("Faturamento por Terapeuta")
    st.dataframe(df_faturamento)

def renderizar_tabela(filtro_ano=None, filtro_mes=None, filtro_dia=None, filtro_tipo_movimento=None, filtro_cliente=None, filtro_terapeuta=None, filtro_tipo_atendimento=None, filtro_detalhe_gasto=None):
    conn = sqlite3.connect('dados.db')
    c = conn.cursor()
    
    # Construir a query SQL base
    query = "SELECT data, dia, mes, ano, tipo_movimento, valor_total, valor_fracionado, forma_pagamento, cliente, cliente_novo, atendimentos, terapeutas, detalhe_gastos, observacoes_predefinidas, observacoes_escritas, alimentado_por, chave_seguranca FROM itens WHERE 1=1"

    # Adicionar cláusulas WHERE conforme filtros fornecidos
    if filtro_ano:
        query += f" AND ano = {filtro_ano}"
    if filtro_mes:
        # Converter o nome do mês para o número do mês
        numero_mes = datetime.strptime(filtro_mes, "%B").month
        query += f" AND mes = {numero_mes}"
    if filtro_dia:
        query += f" AND dia = {filtro_dia}"
    if filtro_tipo_movimento:
        query += f" AND tipo_movimento = '{filtro_tipo_movimento}'"
    if filtro_cliente:
        query += f" AND cliente LIKE '%{filtro_cliente}%'"
    if filtro_terapeuta:
        query += f" AND terapeutas LIKE '%{filtro_terapeuta}%'"
    if filtro_tipo_atendimento:
        query += f" AND atendimentos LIKE '%{filtro_tipo_atendimento}%'"
    if filtro_detalhe_gasto:
        query += f" AND detalhe_gastos LIKE '%{filtro_detalhe_gasto}%'"

    # Executar a query no banco de dados
    c.execute(query)
    data = c.fetchall()
    conn.close()



    


    
    # Verificar se há dados a serem exibidos
    if data:
        # Definir as colunas para o DataFrame
        columns = ["Data", "Dia", "Mês", "Ano", "Tipo de Movimento", "V Total $", "V Fracionado $", "F. de Pagamento", "Cliente", "C. Novo", "T. de Atendimentos", "Terapeuta", "Detalhe de Gastos", "Observações Pré-definidas", "Observações Escritas", "Alimentado por", "Chave de Segurança"]
        
        # Criar o DataFrame
        df = pd.DataFrame(data, columns=columns)
        
        # Adicionar uma nova coluna 'ID' de numeração única
        df.insert(0, 'ID', range(1, 1 + len(df)))

        # Exibir a tabela
        st.dataframe(df)
    else:
        st.write("Nenhum item encontrado para os filtros fornecidos.")







def exportar_para_excel():
    # Implemente a exportação para Excel aqui
    pass

# Função para exportar a tabela para CSV
def exportar_para_csv():
    # Implemente a exportação para CSV aqui
    pass

# Função para exportar a tabela para PDF
def exportar_para_pdf():
    # Implemente a exportação para PDF aqui
    pass

def main_tabela():
    st.title("Tabela de Controle")

    # Crie duas colunas para os inputs
    col5,col1, col2, col3, col4, col6 = st.columns(6)

    # Adicione os inputs em cada coluna
    with col5:
        chave_seguranca = st.text_input("C.Segurança", type="password")
    with col1:
        data = st.date_input("Data")

    with col2:
        tipo_movimento = st.selectbox ("T.Movimento", ["", "Entrada", "Saída", "Garantia de Satisfação"])
        valor_total = st.text_input("V Total $")
        valor_fracionado = st.text_input("V Fracionado $")
        forma_pagamento = st.selectbox("F. de Pagamento", ["", "Transferência", "Cartão", "À Vista"])

    with col3:
        cliente = st.text_input("Cliente")
        cliente_novo = st.selectbox("Cliente Novo", ["", "Sim", "Não"])
        atendimentos = st.selectbox("T.Atendimentos", ["", "Massagem", "Pacote", "Evento", "Produtos", "P. A.", "P. A. Massagem", "Atendimento Evento", "Vale Presente", "V. P. Massagem"])

        # Atualizar a lista de terapeutas disponíveis na interface
        terapeutas_disponiveis = obter_terapeutas()
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
            "","PAC 0/3", "PAC 1/3", "PAC 2/3", "PAC 3/3", "PAC 0/5 PM28270124MM0", "PAC 1/5", 
            "PAC 2/5", "PAC 3/5", "PAC 4/5","PAC 5/5", "PAC 0/10", "PAC 1/10", "PAC 2/10", "PAC 3/10", "PAC 4/10", 
            "PAC 5/10", "PAC 6/10", "PAC 7/10", "PAC 8/10", "PAC 9/10", "PAC 10/10"
        ]

        observacoes_predefinidas = st.selectbox("Pacotes", observacoes_predefinidas_options)
        observacoes_escritas = st.text_area("Observações Escritas", height=100)  # Campo de texto multilinha para observações

    with col6:
        username = obter_usuario_por_chave(chave_seguranca)  # Obtem o nome de usuário com base na chave de segurança
        st.text_input("Alimentado por", value=username, disabled=True)  # Campo preenchido automaticamente

    if not verificar_chave_seguranca(chave_seguranca):
        st.error("Chave de Segurança Inválida, adicione a chave para aparecer mais informações.")
        return

    if not verificar_chave_seguranca(chave_seguranca):
        st.error("Chave de Segurança Inválida, adicione a chave para aparecer mais informações.")
        return

    if st.button("Adicionar Item"):
        adicionar_item(data, tipo_movimento, valor_total, valor_fracionado, forma_pagamento,
                                cliente, cliente_novo, atendimentos, terapeuta, detalhe_gastos, observacoes_predefinidas, observacoes_escritas, username, chave_seguranca)

    st.header("Tabela")

    renderizar_tabela()



def verificar_chave_seguranca(chave_seguranca):
    return True  

def obter_usuario_por_chave(chave_seguranca):
    c.execute("SELECT username FROM users WHERE authentication_key = ?", (chave_seguranca,))
    result = c.fetchone()
    if result:
        return result[0]  # Retorna o nome de usuário se encontrado
    else:
        return ""  # Retorna uma string vazia se a chave de segurança não estiver associada a nenhum usuário



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

    dia = str(data.day)
    mes = str(data.month)
    ano = str(data.year)

    # Se o tipo de atendimento não for um dos seguintes, então valor_fracionado será igual a valor_total
    if atendimentos.strip() not in ["Pacote", "P. A. Massagem", "V. P. Massagem"]:
        valor_fracionado_calculado = valor_total
    else:
        valor_fracionado_calculado = valor_fracionado.strip() if valor_fracionado.strip() else ""

    # Inserção dos dados no banco de dados
    c.execute('''INSERT INTO itens (data, dia, mes, ano, tipo_movimento, valor_total, valor_fracionado, forma_pagamento, cliente, cliente_novo, atendimentos, terapeutas, detalhe_gastos, observacoes_predefinidas, observacoes_escritas, alimentado_por, chave_seguranca)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                (data, dia, mes, ano, tipo_movimento, valor_total, valor_fracionado_calculado, forma_pagamento, cliente, cliente_novo, atendimentos, terapeuta, detalhe_gastos, observacoes_predefinidas, observacoes_escritas, alimentado_por, chave_seguranca))
    conn.commit()

def consultar_dados_do_banco_de_dados(mes, ano):
    # Conexão com o banco de dados
    conn = sqlite3.connect('dados.db')
    c = conn.cursor()

    # Consulta ao banco de dados para obter as informações necessárias
    query = """
        SELECT 
            terapeutas, 
            SUM(CAST(CASE WHEN (tipo_movimento = 'Entrada' OR tipo_movimento = 'Garantia de Satisfação') AND atendimentos IN ('Massagem', 'Pacote', 'P. A. Massagem', 'Atendimento Evento', 'V. P. Massagem') AND valor_fracionado != 'V Fracionado' THEN REPLACE(valor_fracionado, 'R$ ', '') ELSE 0 END AS REAL)) AS comissao,
            COUNT(CASE WHEN (tipo_movimento = 'Entrada' OR tipo_movimento = 'Garantia de Satisfação') AND atendimentos IN ('Massagem', 'Pacote', 'P. A. Massagem', 'Atendimento Evento', 'V. P. Massagem') THEN 1 END) AS quantidade_atendimentos
        FROM 
            itens
        WHERE
            strftime('%m', data) = ? AND strftime('%Y', data) = ? -- Filtro pelo mês e ano
        GROUP BY 
            terapeutas
    """
    
    # Executando a consulta
    c.execute(query, (mes, ano))
    
    # Obtendo os resultados
    resultados = c.fetchall()
    
    # Fechando a conexão com o banco de dados
    conn.close()
    
    return resultados



def calcular_comissao_e_atendimentos():
    # Exibir a seleção do mês e do ano
    mes = st.selectbox("Selecione o mês", [str(i).zfill(2) for i in range(1, 13)], index=2)  # Inicia com o mês 03 como padrão
    ano = st.text_input("Digite o ano", value="2024")

    # Verificar se o ano tem 4 dígitos
    if len(ano) != 4 or not ano.isdigit():
        st.error("Por favor, digite um ano válido com 4 dígitos.")
        return

    # Consultar os dados do banco de dados
    data = consultar_dados_do_banco_de_dados(mes, ano)

    # Criar DataFrame com os dados
    df = pd.DataFrame(data, columns=["Terapeuta", "Comissão", "Quantidade de Atendimentos"])

    # Exibir a tabela com as informações de comissão e atendimentos dos terapeutas
    st.title(f"Comissões e Atendimentos dos Terapeutas - {mes}/{ano}")
    st.dataframe(df)















def main():
    page = st.sidebar.selectbox("Selecione uma opção:", ["Tabela", "Administração", "Administração de Terapeutas", "Comissão e Atendimentos", "Gráficos", "Detalhes de Entrada / Saída", "Editar Item","Contagem Cliente Novo"])

    if page == "Tabela":
        main_tabela()
    elif page == "Administração":
        main_admin()
    elif page == "Administração de Terapeutas":
        main_admin_terapeutas()
    elif page == "Comissão e Atendimentos":
        calcular_comissao_e_atendimentos()
    elif page == "Gráficos":
        mostrar_graficos()
    elif page == "Detalhes de Entrada / Saída":
        main_detalhes_entrada()
    elif page == "Editar Item":  # Adicione esta linha
        editar_item()  # Adicione esta linha também
    elif page == "Contagem Cliente Novo":
        contagemclientenovo()
def obter_item_por_id(id_to_edit):
    conn = sqlite3.connect('dados.db')
    c = conn.cursor()
    c.execute("SELECT * FROM itens WHERE id=?", (id_to_edit,))
    item = c.fetchone()
    conn.close()
    return item


def editar_item():
    st.title("Editar Item")

    # Inputs para selecionar o item a ser editado
    id_to_edit = st.text_input("Digite o ID do item que deseja editar:")

    # Verificar se o ID foi fornecido
    if id_to_edit:
        # Dividir a tela em duas colunas
        col_tabela, col_inputs = st.columns([2, 3])

        # Mostrar a tabela na primeira coluna
        with col_tabela:
            renderizar_tabela()

        # Inputs para editar as informações do item na segunda coluna
        with col_inputs:
            st.write("Editar Informações:")
            
            # Obter o item com base no ID fornecido
            item = obter_item_por_id(id_to_edit)

            if item:
                # Inicializar todas as variáveis com os valores existentes do item
                data = item[1]
                dia, mes, ano = data.split('-')
                tipo_movimento = item[2]
                valor_total = item[3]
                valor_fracionado = item[4]
                forma_pagamento = item[5]
                cliente = item[6]
                cliente_novo = item[7]
                atendimentos = item[8]
                terapeuta = item[9]
                detalhe_gastos = item[10]
                observacoes_predefinidas = item[11]
                observacoes_escritas = item[12]
                alimentado_por = item[13]

                # Opção para selecionar os campos a serem editados
                campos_editar = st.multiselect("Selecione os campos que deseja editar:", 
                                                ["Data", "Tipo de Movimento", "Valor Total", 
                                                "Valor Fracionado", "Forma de Pagamento", "Cliente", 
                                                "Cliente Novo", "Tipo de Atendimento", "Terapeuta", 
                                                "Detalhe de Gastos", "Pacotes", "Observações Escritas", 
                                                "Alimentado Por"])

                # Inputs para editar os campos selecionados
            detalhe_gastos_options = [
                "", "Alimentação", "Transporte", "Salario", "Imposto", "Outros Gastos",
                "Diária Terapeuta", "Conta de Água", "Conta de Luz", "Produtos", 
                "Recarga Celular", "Conta de Internet", "G. Administrativos", "Aluguel", 
                "Não escrever"
]

            if campos_editar:
                campos_atualizados = {}  # Dicionário para armazenar os campos atualizados
                nova_observacao = None
                for campo in campos_editar:
                    if campo == "Data":
                        nova_data = st.date_input("Data")
                        dia = nova_data.day
                        mes = nova_data.month
                        ano = nova_data.year

                        # Atualiza os campos no dicionário `campos_atualizados`
                        campos_atualizados["data"] = nova_data.strftime("%Y-%m-%d")  # Armazena a nova data completa
                        campos_atualizados["dia"] = int(dia)  # Converte para inteiro para remover zero à esquerda
                        campos_atualizados["mes"] = int(mes)  # Converte para inteiro para remover zero à esquerda
                        campos_atualizados["ano"] = ano
                    elif campo == "Tipo de Movimento":
                        index_tipo_movimento = ["Entrada", "Saída", "Garantia de Satisfação"].index(tipo_movimento) if tipo_movimento in ["Entrada", "Saída", "Garantia de Satisfação"] else 0
                        tipo_movimento = st.selectbox("Novo Tipo de Movimento:", ["", "Entrada", "Saída", "Garantia de Satisfação"], index=index_tipo_movimento)
                        campos_atualizados["tipo_movimento"] = tipo_movimento
                    elif campo == "Valor Total":
                        valor_total = st.text_input("Novo Valor Total:", value=valor_total)
                        campos_atualizados["valor_total"] = valor_total
                    elif campo == "Valor Fracionado":
                        valor_fracionado = st.text_input("Novo Valor Fracionado:", value=valor_fracionado)
                        campos_atualizados["valor_fracionado"] = valor_fracionado
                    elif campo == "Forma de Pagamento":
                        index_forma_pagamento = ["", "Transferência", "Cartão", "À Vista"].index(forma_pagamento) if forma_pagamento in ["", "Transferência", "Cartão", "À Vista"] else 0
                        forma_pagamento = st.selectbox("Nova Forma de Pagamento:", ["", "Transferência", "Cartão", "À Vista"], index=index_forma_pagamento)
                        campos_atualizados["forma_pagamento"] = forma_pagamento
                    elif campo == "Cliente":
                        cliente = st.text_input("Novo Cliente:", value=cliente)
                        campos_atualizados["cliente"] = cliente
                    elif campo == "Cliente Novo":
                        index_cliente_novo = ["", "Sim", "Não"].index(cliente_novo) if cliente_novo in ["", "Sim", "Não"] else 0
                        cliente_novo = st.selectbox("Novo Cliente Novo:", ["", "Sim", "Não"], index=index_cliente_novo)
                        campos_atualizados["cliente_novo"] = cliente_novo
                    elif campo == "Tipo de Atendimento":
                        index_atendimentos = ["", "Massagem", "Pacote", "Evento", "Produtos", "P. A.", "P. A. Massagem", "Atendimento Evento", "Vale Presente", "V. P. Massagem"].index(atendimentos) if atendimentos in ["", "Massagem", "Pacote", "Evento", "Produtos", "P. A.", "P. A. Massagem", "Atendimento Evento", "Vale Presente", "V. P. Massagem"] else 0
                        atendimentos = st.selectbox("Novo Tipo de Atendimento:", ["", "Massagem", "Pacote", "Evento", "Produtos", "P. A.", "P. A. Massagem", "Atendimento Evento", "Vale Presente", "V. P. Massagem"], index=index_atendimentos)
                        campos_atualizados["atendimentos"] = atendimentos
                    elif campo == "Terapeuta":
                        conn = sqlite3.connect('dados.db')  # Substitua 'seu_banco_de_dados.db' pelo nome do seu banco de dados
                        c = conn.cursor()

                        # Consulta ao banco de dados para obter os terapeutas disponíveis
                        c.execute("SELECT DISTINCT terapeutas FROM itens")
                        terapeutas_disponiveis = [row[0] for row in c.fetchall()]

                        # Fechar conexão com o banco de dados
                        conn.close()

                        # Selecionar um terapeuta
                        terapeuta_selecionado = st.selectbox("Selecione um Terapeuta:", terapeutas_disponiveis)
                        campos_atualizados["terapeutas"] = terapeuta_selecionado 
                    elif campo == "Detalhe de Gastos":
                            index_detalhe_gastos = detalhe_gastos_options.index(detalhe_gastos) if detalhe_gastos in detalhe_gastos_options else 0
                            detalhe_gastos = st.selectbox("Novo Detalhe de Gastos:", detalhe_gastos_options, index=index_detalhe_gastos)
                            campos_atualizados["detalhe_gastos"] = detalhe_gastos
                    elif campo == "Pacotes":
                        opcoes_observacoes = ["","PAC 0/3", "PAC 1/3", "PAC 2/3", "PAC 3/3", "PAC 0/5", "PAC 1/5", 
                        "PAC 2/5", "PAC 3/5", "PAC 4/5","PAC 5/5", "PAC 0/10", "PAC 1/10", "PAC 2/10","PAC 3/10", "PAC 4/10", 
                        "PAC 5/10", "PAC 6/10", "PAC 7/10", "PAC 8/10", "PAC 9/10", "PAC 10/10"]
                        nova_observacao = st.selectbox("Nova Observação:", opcoes_observacoes)
                        campos_atualizados["observacoes_predefinidas"] = nova_observacao
                    elif campo == "Observações Escritas":
                        observacoes_escritas = st.text_input("Novas Observações Escritas:", value=observacoes_escritas)
                        campos_atualizados["observacoes_escritas"] = observacoes_escritas
                    elif campo == "Alimentado Por":
                        alimentado_por = st.text_input("Novo Alimentado Por:", value=alimentado_por)
                        campos_atualizados["alimentado_por"] = alimentado_por

                    chave_seguranca_id = str(uuid.uuid4())
                    chave_seguranca = st.text_input("Chave de Segurança", key=chave_seguranca_id, type="password")

                    if st.button("Salvar Alterações"):
                        # Verificar se a chave de segurança é válida
                        if verificar_chave_seguranca(chave_seguranca):
                            # Atualizar apenas os campos selecionados no banco de dados
                            edit_item_by_id(id_to_edit, campos_atualizados, chave_seguranca)

                            st.success(f"Item com ID {id_to_edit} editado com sucesso!")
                        else:
                            st.error("Chave de Segurança Inválida")


def edit_item_by_id(id_to_edit, campos_atualizados, chave_seguranca):
    # Conectar ao banco de dados
    conn = sqlite3.connect('dados.db')  # Substitua 'seu_banco_de_dados.db' pelo nome do seu banco de dados
    c = conn.cursor()

    # Atualizar a query de acordo com os campos atualizados
    update_query = "UPDATE itens SET "
    values = []

    for campo, valor in campos_atualizados.items():
        update_query += f"{campo} = ?, "
        values.append(valor)

    # Adicione a chave de segurança à consulta
    update_query += "chave_seguranca = ? WHERE id = ?"
    values.append(chave_seguranca)
    values.append(id_to_edit)

    # Executar a consulta
    c.execute(update_query, tuple(values))

    # Commit e fechar conexão
    conn.commit()
    conn.close()


def contagemclientenovo():
    st.title("Contagem de Clientes Novos por Mês")

    # Conecta ao banco de dados
    conn = sqlite3.connect('dados.db')
    cursor = conn.cursor()

    try:
        # Consulta SQL para obter todos os anos disponíveis na base de dados
        cursor.execute("SELECT DISTINCT strftime('%Y', data) FROM itens")
        anos_disponiveis = [x[0] for x in cursor.fetchall()]

        # Seleção do ano através de dropdown
        key_ano = "selectbox_ano"  # Chave única para o widget de seleção de ano
        ano_selecionado = st.selectbox("Selecione o ano:", sorted(anos_disponiveis), index=0, key=key_ano)

        # Consulta SQL para obter todos os meses disponíveis na base de dados para o ano selecionado
        cursor.execute(f"SELECT DISTINCT strftime('%m', data) FROM itens WHERE strftime('%Y', data) = '{ano_selecionado}'")
        meses_disponiveis = [x[0] for x in cursor.fetchall()]

        # Seleção do mês através de dropdown
        key_mes = "selectbox_mes"  # Chave única para o widget de seleção de mês
        mes_selecionado = st.selectbox("Selecione o mês:", sorted(meses_disponiveis), index=0, key=key_mes)

        mes_ano_selecionado = f"{ano_selecionado}-{mes_selecionado}"

        # Consulta SQL para obter dados de clientes novos adicionados no mês e ano selecionados
        cursor.execute(f"SELECT COUNT(*) FROM itens WHERE cliente_novo = 'Sim' AND strftime('%Y-%m', data) = '{mes_ano_selecionado}'")

        # Obtem o total de clientes novos adicionados no mês selecionado
        total_clientes_novos = cursor.fetchone()[0]

        # Exibe o total de clientes novos adicionados no mês e ano selecionados
        st.write(f"Total de clientes novos adicionados no mês {mes_ano_selecionado}: {total_clientes_novos}")

    except sqlite3.Error as e:
        st.error(f"Erro ao acessar o banco de dados: {e}")

    finally:
        # Fecha a conexão com o banco de dados
        conn.close()









  


def atualizar_item(numero_linha, tipo_movimento, valor_total, valor_fracionado, forma_pagamento):
    # Atualizar os dados no banco de dados usando a instrução SQL UPDATE
    c.execute("UPDATE itens SET tipo_movimento = ?, valor_total = ?, valor_fracionado = ?, forma_pagamento = ? WHERE ID = ?", (tipo_movimento, valor_total, valor_fracionado, forma_pagamento, numero_linha))
    conn.commit()



def mostrar_graficos():
    st.title("Comparação de Valores por Mês")

    # Conectar ao banco de dados
    conn = sqlite3.connect('dados.db')
    c = conn.cursor()

    # Consultar o banco de dados para obter os meses únicos e anos únicos
    c.execute("SELECT DISTINCT strftime('%m', data), strftime('%Y', data) FROM itens ORDER BY strftime('%Y', data), strftime('%m', data)")
    resultados = c.fetchall()

    # Criar listas de meses e anos únicos
    meses_numeros = [resultado[0] for resultado in resultados]
    anos = [resultado[1] for resultado in resultados]

    # Mapear números de mês para nomes de mês
    nome_meses = {
        '01': 'January', '02': 'February', '03': 'March', '04': 'April',
        '05': 'May', '06': 'June', '07': 'July', '08': 'August',
        '09': 'September', '10': 'October', '11': 'November', '12': 'December'
    }

    meses = [nome_meses[numero] for numero in meses_numeros]

    # Selecionar os meses e anos para comparação
    mes_selecionado_nomes = st.multiselect("Selecione os meses para comparar:", meses)  # Usar meses únicos recuperados
    anos_selecionados = st.multiselect("Selecione os anos para comparar:", anos)  # Usar anos únicos recuperados

    # Selecionar o tipo de movimento para comparar
    tipo_movimento = st.selectbox("Selecione o Tipo de Movimento para Comparar", ['Entrada', 'Saída', 'Garantia de Satisfação'])

    # Inicializar listas para armazenar os valores totais por mês e ano selecionados
    valores_totais = []
    valores_fracionados = []

    # Iterar sobre os meses e anos selecionados
    for ano in anos_selecionados:
        for mes_nome in mes_selecionado_nomes:
            mes_numero = list(nome_meses.keys())[list(nome_meses.values()).index(mes_nome)]

            # Calcular o intervalo de datas para o mês e ano selecionados
            inicio_mes = datetime(int(ano), int(mes_numero), 1)
            fim_mes = inicio_mes + relativedelta(day=31)

            # Consultar o banco de dados para obter os valores totais para o mês e ano selecionados
            c.execute("SELECT SUM(CASE WHEN tipo_movimento = ? AND valor_fracionado != 'V Fracionado $' THEN valor_total ELSE 0 END) FROM itens WHERE data >= ? AND data <= ?", (tipo_movimento, inicio_mes, fim_mes))
            valor_total = c.fetchone()[0] or 0

            # Consultar o banco de dados para obter os valores fracionados para o mês e ano selecionados
            c.execute("SELECT SUM(CASE WHEN (tipo_movimento = 'Entrada' OR tipo_movimento = 'Garantia de Satisfação') AND atendimentos IN ('Massagem', 'Pacote', 'P. A. Massagem', 'Atendimento Evento', 'V. P. Massagem') AND valor_fracionado != 'V Fracionado' THEN REPLACE(valor_fracionado, 'R$ ', '') ELSE 0 END) FROM itens WHERE data >= ? AND data <= ?", (inicio_mes, fim_mes))
            valor_fracionado = c.fetchone()[0] or 0

            # Armazenar os valores totais e fracionados na lista correspondente
            valores_totais.append({
                'Mês': f"{mes_nome} {ano}",
                'Valor Total': valor_total
            })
            valores_fracionados.append({
                'Mês': f"{mes_nome} {ano}",
                'Valor Fracionado': valor_fracionado
            })

    # Exibir gráficos
    if valores_totais:
        # Criar DataFrames com os dados
        df_valores_totais = pd.DataFrame(valores_totais)
        df_valores_fracionados = pd.DataFrame(valores_fracionados)

        # Criar gráficos lado a lado
        fig, axs = plt.subplots(1, 2, figsize=(12, 6))

        # Plotar gráfico de barras para comparar os valores totais
        axs[0].bar(df_valores_totais['Mês'], df_valores_totais['Valor Total'], color='blue')
        axs[0].set_title('Valor Total por Mês')
        axs[0].set_xlabel('Mês')
        axs[0].set_ylabel('Valor Total')

        # Plotar gráfico de barras para comparar os valores fracionados
        axs[1].bar(df_valores_fracionados['Mês'], df_valores_fracionados['Valor Fracionado'], color='orange')
        axs[1].set_title('Valor Total dos Valores Fracionados por Mês')
        axs[1].set_xlabel('Mês')
        axs[1].set_ylabel('Valor Total dos Valores Fracionados')

        # Ajustar layout
        plt.tight_layout()

        # Exibir os gráficos
        st.pyplot(fig)
    else:
        st.write("Nenhum dado disponível para os filtros selecionados.")

    # Fechar conexão com o banco de dados
    conn.close()

def calcular_valor_servico_por_tipo(c, tipo_movimento, mes=None, ano=None):
    # Construir a parte da consulta SQL para o tipo de movimento especificado
    query = "SELECT SUM(valor_total) FROM itens WHERE tipo_movimento = 'Entrada' AND atendimentos = ?"

    # Adicionar a condição do filtro por mês, se fornecido
    if mes is not None:
        query += " AND mes = ?"

    # Adicionar a condição do filtro por ano, se fornecido
    if ano is not None:
        query += " AND ano = ?"

    # Executar a consulta SQL
    if mes is not None and ano is not None:
        c.execute(query, (tipo_movimento, mes, ano))
    elif mes is not None:
        c.execute(query, (tipo_movimento, mes))
    elif ano is not None:
        c.execute(query, (tipo_movimento, ano))
    else:
        c.execute(query, (tipo_movimento,))

    # Recuperar o resultado da consulta
    result = c.fetchone()

    # Verificar se há resultados e retornar o valor total
    if result is not None:
        valor_total = result[0]
        return valor_total
    else:
        return None

def calcular_detalhes_gasto(c, detalhe_gasto, mes=None, ano=None):
    # Construir a parte da consulta SQL para o detalhe de gasto especificado
    query = "SELECT SUM(valor_total) FROM itens WHERE tipo_movimento = 'Saída' AND detalhe_gastos = ?"

    # Adicionar a condição do filtro por mês, se fornecido
    if mes is not None:
        query += " AND mes = ?"

    # Adicionar a condição do filtro por ano, se fornecido
    if ano is not None:
        query += " AND ano = ?"

    # Imprimir a consulta SQL para depuração
    print("Consulta SQL:", query)

    # Executar a consulta SQL
    if mes is not None and ano is not None:
        c.execute(query, (detalhe_gasto, mes, ano))
    elif mes is not None:
        c.execute(query, (detalhe_gasto, mes))
    elif ano is not None:
        c.execute(query, (detalhe_gasto, ano))
    else:
        c.execute(query, (detalhe_gasto,))

    # Recuperar o resultado da consulta
    result = c.fetchone()

    # Verificar se há resultados e retornar o valor total
    if result is not None:
        valor_total = result[0]
        return valor_total
    else:
        return None


def main_detalhes_entrada():
    st.title("Detalhes de Entrada")

    tipos_movimento = ["Massagem", "Pacote", "Produtos", "Vale Presente"]
    selected_movimento = st.selectbox("Selecione o Tipo de Movimento:", tipos_movimento)

    # Adicionando campo de seleção de mês e ano
    ano_entrada = st.number_input("Selecione o Ano para Entrada:", value=2024)
    mes_entrada = st.selectbox("Selecione o Mês para Entrada:", range(1, 13))

    if selected_movimento:
        # Conectar ao banco de dados (supondo que você já tenha essa função)
        conn = sqlite3.connect('dados.db')

        c = conn.cursor()

        # Calcular o valor total do serviço para o tipo de movimento selecionado, mês e ano selecionados
        valor_total = calcular_valor_servico_por_tipo(c, selected_movimento, mes_entrada, ano_entrada)
        st.write(f"Valor Total para {selected_movimento} em {mes_entrada}/{ano_entrada}: R$ {valor_total if valor_total is not None else 0}")

        # Fechar a conexão com o banco de dados
        conn.close()

        # Agora, vamos para a parte de detalhes de saída
        st.title("Detalhes de Saída")

        detalhes_gastos = ["Alimentação", "Transporte", "Salario", "Imposto", "Outros Gastos",
                        "Diária Terapeuta", "Conta de Água", "Conta de Luz", "Produtos", 
                        "Recarga Celular", "Conta de Internet", "G. Administrativos", "Aluguel", 
                        "Não escrever"]
        selected_gasto = st.selectbox("Selecione o Detalhe de Gasto:", detalhes_gastos)

        # Adicionando campo de seleção de mês e ano
        ano_saida = st.number_input("Selecione o Ano para Saída:", value=2024)
        mes_saida = st.selectbox("Selecione o Mês para Saída:", range(1, 13))

        if selected_gasto:
            # Conectar ao banco de dados (supondo que você já tenha essa função)
            conn = sqlite3.connect('dados.db')

            c = conn.cursor()

            # Calcular o valor total do detalhe de gasto para a saída no mês e ano selecionados
            total_gasto = calcular_detalhes_gasto(c, selected_gasto, mes_saida, ano_saida)  # Passando o cursor 'c' corretamente
            st.write(f"Total gasto em {selected_gasto} em {mes_saida}/{ano_saida}: R$ {total_gasto if total_gasto is not None else 0}")

            # Fechar a conexão com o banco de dados
            conn.close()

def renderizar_detalhes_entrada(tipo_movimento):
    print("Tipo de movimento selecionado:", tipo_movimento)
    st.header(f"Detalhes de Entrada para {tipo_movimento}")

    # Consulta ao banco de dados para obter os detalhes de entrada para o tipo de movimento especificado
    query = f"SELECT SUM(valor_total) FROM itens WHERE tipo_movimento = ?"
    c.execute(query, (tipo_movimento,))
    result = c.fetchone()
    print("Resultado da consulta:", result)

    # Calcular o valor total do serviço específico
    valor_servico = calcular_valor_servico_por_tipo(tipo_movimento)
    st.write(f"Valor Total para {tipo_movimento}: R$ {valor_servico}")

def adicionar_terapeuta(nome_terapeuta):
    # Insira a lógica para adicionar terapeuta ao banco de dados
    c.execute("INSERT INTO terapeutas (nome) VALUES (?)", (nome_terapeuta,))
    conn.commit()

def remover_terapeuta(nome_terapeuta):
    # Insira a lógica para remover terapeuta do banco de dados
    c.execute("DELETE FROM terapeutas WHERE nome=?", (nome_terapeuta,))
    conn.commit()

def main_admin_terapeutas():
    st.title("Administração de Terapeutas")

    # Seção para adicionar terapeutas
    st.markdown("## Adicionar Terapeutas")
    novo_terapeuta = st.text_input("Nome do Novo Terapeuta:")
    if st.button("Adicionar Terapeuta"):
        if novo_terapeuta:
            adicionar_terapeuta(novo_terapeuta)
            st.success(f"Terapeuta '{novo_terapeuta}' adicionado com sucesso!")
        else:
            st.warning("Por favor, insira o nome do terapeuta.")

    # Seção para remover terapeutas
    st.markdown("## Remover Terapeutas")
    terapeutas = obter_terapeutas()
    terapeuta_para_remover = st.selectbox("Selecione o Terapeuta para Remover:", terapeutas)
    if st.button("Remover Terapeuta"):
        if terapeuta_para_remover:
            remover_terapeuta(terapeuta_para_remover)
            st.success(f"Terapeuta '{terapeuta_para_remover}' removido com sucesso!")
        else:
            st.warning("Por favor, selecione um terapeuta para remover.")

    # Atualizar a lista de terapeutas disponíveis na interface

def obter_terapeutas():
    # Função para obter a lista de terapeutas existentes
    c.execute("SELECT nome FROM terapeutas")
    terapeutas = c.fetchall()
    return [terapeuta[0] for terapeuta in terapeutas]
def obter_detalhes_gastos():
    conn = sqlite3.connect('dados.db')
    c = conn.cursor()

    # Consulta SQL para obter detalhes de gastos únicos
    c.execute("SELECT DISTINCT detalhe_gastos FROM itens")
    detalhes_gastos = c.fetchall()

    # Fechar conexão com o banco de dados
    conn.close()

    # Retornar uma lista dos detalhes de gastos únicos
    return [detalhe[0] for detalhe in detalhes_gastos]

def obter_tipos_atendimento():
    # Conectar ao banco de dados
    conn = sqlite3.connect('dados.db')
    c = conn.cursor()

    # Consulta SQL para selecionar tipos de atendimento distintos
    query = "SELECT DISTINCT atendimentos FROM itens"

    # Executar a consulta SQL
    c.execute(query)

    # Recuperar os resultados da consulta
    tipos_atendimento = [row[0] for row in c.fetchall()]

    # Fechar a conexão com o banco de dados
    conn.close()

    return tipos_atendimento
    


if __name__ == "__main__":
    main()
