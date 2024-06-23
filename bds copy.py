import sqlite3

# Conexão com o banco de dados SQLite
conn = sqlite3.connect('dados.db')
c = conn.cursor()

def mostrar_valores_fracionados():
    try:
        # Consultar todos os valores da coluna 'valor_fracionado' na tabela 'itens'
        c.execute("SELECT valor_fracionado FROM itens")
        valores_fracionados = c.fetchall()
        
        # Imprimir os valores fracionados
        print("Valores Fracionados:")
        for valor_fracionado in valores_fracionados:
            print(valor_fracionado[0])  # O valor está na primeira posição da tupla
        
    except sqlite3.Error as e:
        print("Ocorreu um erro ao mostrar os valores fracionados da tabela 'itens':", e)

def main():
    print("Mostrando todos os valores da coluna 'valor_fracionado' da tabela 'itens'...")
    mostrar_valores_fracionados()

if __name__ == "__main__":
    main()
