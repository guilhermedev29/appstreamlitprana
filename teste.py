import sqlite3
import pandas as pd

def print_all_items():
    # Conexão com o banco de dados SQLite
    conn = sqlite3.connect('dados.db')
    c = conn.cursor()

    # Selecionar todos os itens da tabela
    c.execute("SELECT * FROM itens")
    items = c.fetchall()

    # Imprimir os nomes das colunas
    columns = [description[0] for description in c.description]
    print("Número de colunas nas colunas:", len(columns))
    print("Colunas:", columns)

    # Imprimir o número de colunas nos dados
    num_columns_in_data = len(items[0]) if items else 0
    print("Número de colunas nos dados:", num_columns_in_data)

    # Verificar se há dados
    if items:
        # Criar DataFrame com os dados e as colunas corretas
        df = pd.DataFrame(items, columns=columns)
        print(df)
    else:
        print("Nenhum item encontrado na tabela 'itens'.")

    # Fechar a conexão com o banco de dados
    conn.close()

# Chamar a função para imprimir todos os itens
print_all_items()
a