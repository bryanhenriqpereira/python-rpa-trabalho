import os
import time
import mysql.connector
import pyautogui
import pyperclip
import keyboard # requer o 'pip install keyboard'

# =========================================================
# CONFIGURAÇÕES
# =========================================================
pyautogui.PAUSE = 0.5

# Dicionário mapeando categorias para suas respectivas palavras-chave
CATEGORIAS_KEYWORDS = {
    "Trabalho": ["trabalho", "empresa", "emprego", "reunião", "contrato", "chefe"],
    "Estudos": ["escola", "prova", "atividade", "professor", "aluno"],
    "Entretenimento": ["jogo", "videogame", "filme", "série", "cinema"],
    "Tecnologia": ["python", "programação", "tecnologia", "software", "computador", "javascript"],
}


def limpar_terminal():
    os.system("cls" if os.name == "nt" else "clear")


def conectar_banco():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
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


def classificar_email(texto):
    texto_minusculo = texto.lower()

    for categoria, palavras in CATEGORIAS_KEYWORDS.items():
        if any(palavra in texto_minusculo for palavra in palavras):
            return categoria

    return "Outros"


# =========================================================
# FUNÇÕES DE INTERAÇÃO COM O EXCEL
# =========================================================
def abrir_excel(conexao, remetente, destinatario, assunto, conteudo, data_hr, categoria, indice):
    pyautogui.press("win")
    time.sleep(1)
    pyautogui.write("excel")
    pyautogui.press("enter")
    time.sleep(3)

    pyautogui.hotkey("win", "up")
    time.sleep(1)

    pyautogui.hotkey("ctrl", "l")
    pyautogui.write("https://excel.com")
    pyautogui.press("enter")

    print("Aguardando carregamento do Excel ...")
    time.sleep(7)

    print(f"Procurando por arquivos de e-mail salvos...")
    time.sleep(4)
    
    # Salvando no banco integrado com o fluxo do Excel
    salvar_email(conexao, remetente, destinatario, assunto, conteudo, data_hr, categoria)
    print("Email salvo no Excel via BD")
    print(f"Email.exl nº {indice + 1} SALVO")


# =========================================================
# FUNÇÕES DE INTERAÇÃO COM O GMAIL
# =========================================================
def abrir_gmail():
    pyautogui.press("win")
    time.sleep(1)
    pyautogui.write("chrome")
    pyautogui.press("enter")
    time.sleep(3)

    pyautogui.hotkey("win", "up")
    time.sleep(1)

    pyautogui.hotkey("ctrl", "l")
    pyautogui.write("https://gmail.com")
    pyautogui.press("enter")

    print("Aguardando carregamento da Caixa de Entrada...")
    time.sleep(7)

    X_PRIMEIRO_EMAIL = 480
    Y_PRIMEIRO_EMAIL = 500

    print("Abrindo o primeiro e-mail...")
    pyautogui.click(x=X_PRIMEIRO_EMAIL, y=Y_PRIMEIRO_EMAIL)
    time.sleep(4)


def ler_email():
    pyautogui.click(x=500, y=500)
    time.sleep(0.5)

    pyautogui.hotkey("ctrl", "a")
    pyautogui.hotkey("ctrl", "c")
    time.sleep(0.5)

    return pyperclip.paste()


def ir_para_proximo_email():
    print("Avançando para o próximo e-mail ...")
    keyboard.send('down')
    time.sleep(3)


# =========================================================
# FLUXO PRINCIPAL DE PROCESSAMENTO
# =========================================================
def processar():
    limpar_terminal()
    print("=" * 60)
    print("            RPA - PROCESSADOR DE E-MAILS")
    print("=" * 60)

    try:
        quantidade_emails = int(input("\nDEFINA  A  QUANTIDADE  DE  E-MAILS  A  PROCESSAR: "))
    except ValueError:
        print("Entrada inválida! Digite apenas números inteiros.")
        return

    print("\nConectando ao banco...")
    try:
        conexao = conectar_banco()
        print("Banco conectado com sucesso!")
    except mysql.connector.Error as erro:
        print(f"\nErro ao conectar ao MySQL: {erro}")
        return

    # Variáveis padrão para os exemplos
    remetente = "A extrair"
    destinatario = "A extrair"
    assunto = "A extrair"
    data_hr = None
    texto_email = ""
    categoria = "Outros"

    try:
        print("\nAbrindo Gmail...")
        abrir_gmail()
        print("Gmail aberto.\nIniciando processamento...\n")

        for i in range(quantidade_emails):
            print("-" * 60)
            print(f"Processando e-mail {i + 1}/{quantidade_emails}")

            try:
                texto_email = ler_email()

                if not texto_email or not texto_email.strip():
                    print("E-mail vazio. Ignorando.")
                    continue

                categoria = classificar_email(texto_email)
                print(f"Categoria: {categoria}")

                # Salvar e-mail no banco
                salvar_email(
                    conexao,
                    remetente,
                    destinatario,
                    assunto,
                    texto_email,
                    data_hr,
                    categoria,
                )
                print("E-mail salvo no banco!")
                print(f"Email nº {i + 1} SALVO") 

                # Próximo e-mail
                ir_para_proximo_email()

            except Exception as erro:
                print(f"Erro ao processar e-mail individual: {erro}")

        # Executa a parte do Excel ao terminar o ciclo dos e-mails (ainda com a conexão aberta)
        print("\nAbrindo rotina do Excel...")
        abrir_excel(conexao, remetente, destinatario, assunto, texto_email, data_hr, categoria, 0)

    finally:
        # Verificação segura para fechar a conexão no final de tudo
        if 'conexao' in locals() and conexao.is_connected():
            conexao.close()
            print("\n" + "=" * 60)
            print("PROCESSAMENTO FINALIZADO E CONEXÃO FECHADA!")
            print("=" * 60)


# =========================================================
# EXECUÇÃO
# =========================================================
if __name__ == "__main__":
    processar()