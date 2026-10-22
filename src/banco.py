import os
import mysql.connector

def conectar_banco():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "127.0.0.1"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASS", "SUA_SENHA"),
        database="EmailBD",
    )

def salvar_email(conexao, remetente, destinatario, assunto, conteudo, data_hr, filtragem):
    sql = """
        INSERT INTO tb_email 
        (remetente, destinatario, assunto, conteudo, data_hr, status_processamento, filtragem)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    valores = (remetente, destinatario, assunto, conteudo, data_hr, "OK", filtragem)

    with conexao.cursor() as cursor:
        cursor.execute(sql, valores)
        conexao.commit()