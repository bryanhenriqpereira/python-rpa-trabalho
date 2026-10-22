import os
import time
import mysql.connector
import pyautogui
import pyperclip

                                                # Terceira versao do codigo original ( main III )
# =========================================================
# CONFIGURAÇÕES
# =========================================================
pyautogui.PAUSE = 0.5

# Dicionário mapeando categorias para suas respectivas palavras-chave
CATEGORIAS_KEYWORDS = {
    "Trabalho": ["trabalho", "empresa", "emprego", "reunião","contrato"],
    "Estudos": ["escola", "prova", "atividade", "professor", "aluno"],
    "Entretenimento": ["jogo", "videogame", "filme", "série", "cinema"],
    "Tecnologia": ["python", "programação", "tecnologia", "software", "computador"],
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
        if any(palavra in texto_minusculo  in palavras for palavra in palavras):
            return categoria    # não inserir 'for_word' na linha acima

    return "Outros"


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
    

# =========================================================
# FLUXO PRINCIPAL DE PROCESSAMENTO
# =========================================================


def processar():
    limpar_terminal()
    print("=" * 60)
    print("          RPA - PROCESSADOR DE E-MAILS")
    print("=" * 60)

    # REAJUSTE AQUI: O input agora acontece no momento visual correto do robô
    try:
        quantidade_emails = int(input("\n- DEFINA  A  QUANTIDADE  DE  E-MAILS  A  PROCESSAR: "))
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

                remetente = "A extrair"
                destinatario = "A extrair"
                assunto = "A extrair"
                data_hr = None

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

                ir_para_proximo_email()

            except Exception as erro:
                print(f"Erro ao processar e-mail individual: {erro}")

    finally:
        conexao.close()
        print("\n" + "=" * 60)
        print("PROCESSAMENTO FINALIZADO E CONEXÃO FECHADA!")
        print("=" * 60)


# =========================================================
# EXECUÇÃO
# =========================================================
if __name__ == "_main_":
    processar()