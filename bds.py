import sqlite3

# Conexão com o banco de dados SQLite
conn = sqlite3.connect('dados.db')
c = conn.cursor()

def mostrar_colunas_da_tabela_itens():
    try:
        # Consultar informações sobre as colunas da tabela itens
        c.execute("PRAGMA table_info(itens)")
        colunas = c.fetchall()
        
        # Imprimir o nome de cada coluna
        for coluna in colunas:
            print(coluna[1])  # O nome da coluna está na segunda posição da tupla
        
    except sqlite3.Error as e:
        print("Ocorreu um erro ao mostrar as colunas da tabela 'itens':", e)

def main():
    print("Mostrando todas as colunas da tabela 'itens', incluindo a chave primária 'id'...")
    mostrar_colunas_da_tabela_itens()

if __name__ == "__main__":
    main()
