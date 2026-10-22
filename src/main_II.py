import os
import time
import mysql.connector
import pyautogui
import pyperclip
                                                    # Segunda versao do codigo original ( main II )
# =========================================================
# CONFIGURAÇÕES
# =========================================================
pyautogui.PAUSE = 0.5
QUANTIDADE_EMAILS = int(input("- QUANTIDADE  DE  E-MAIL's: "))

# Dicionário mapeando categorias para suas respectivas palavras-chave
CATEGORIAS_KEYWORDS = {
    "Trabalho": ["trabalho", "empresa", "emprego", "reunião"],
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
        if any(palavra in texto_minusculo for palavra in palavras):
            return categoria

    return "Outros"


# =========================================================
# NOVAS FUNÇÕES DE INTERAÇÃO COM O GMAIL
# =========================================================


def abrir_gmail():
    # Abre o navegador
    pyautogui.press("win")
    time.sleep(1)
    pyautogui.write("chrome")
    pyautogui.press("enter")
    time.sleep(3)

    # Maximiza a janela para padronizar o tamanho da tela
    pyautogui.hotkey("win", "up")
    time.sleep(1)

    # Digita o link do Gmail
    pyautogui.hotkey("ctrl", "l")
    pyautogui.write("https://gmail.com")
    pyautogui.press("enter")

    # Aguarda 7 segundos para garantir que a caixa de entrada carregou totalmente
    print("Aguardando carregamento da Caixa de Entrada...")
    time.sleep(7)

    # Coordenada aproximada do PRIMEIRO e-mail da lista na tela maximizada.
    X_PRIMEIRO_EMAIL = 400
    Y_PRIMEIRO_EMAIL = 300

    print("Abrindo o primeiro e-mail...")
    pyautogui.click(x=X_PRIMEIRO_EMAIL, y=Y_PRIMEIRO_EMAIL)
    time.sleep(3)  # Aguarda o e-mail abrir


def ler_email():
    # Clica no meio da tela para garantir o foco no conteúdo do e-mail
    pyautogui.click(x=500, y=500)
    time.sleep(0.5)

    # Seleciona tudo e copia
    pyautogui.hotkey("ctrl", "a")
    pyautogui.hotkey("ctrl", "c")
    time.sleep(0.5)

    texto = pyperclip.paste()
    return texto


def ir_para_proximo_email():
    print("Avançando para o próximo e-mail...")

    # Método 1: Usando o atalho de teclado nativo do Gmail (Tecla 'j')
    # Nota: Requer "Atalhos de teclado" ATIVADOS nas configurações do Gmail.
    pyautogui.press("j")

    # Método 2 (Alternativo por clique se o de cima não funcionar):
    # X_BOTAO_PROXIMO = 1250
    # Y_BOTAO_PROXIMO = 255
    # pyautogui.click(x=X_BOTAO_PROXIMO, y=Y_BOTAO_PROXIMO)

    time.sleep(3)


# =========================================================
# FLUXO PRINCIPAL DE PROCESSAMENTO
# =========================================================


def processar():
    limpar_terminal()
    print("=" * 60)
    print("          RPA - PROCESSADOR DE E-MAILS")
    print("=" * 60)

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

        for i in range(QUANTIDADE_EMAILS):
            print("-" * 60)
            print(f"Processando e-mail {i + 1}/{QUANTIDADE_EMAILS}")

            try:
                texto_email = ler_email()

                if not texto_email or not texto_email.strip():
                    print("E-mail vazio. Ignorando.")
                    continue

                categoria = classificar_email(texto_email)
                print(f"Categoria: {categoria}")

                # Dados temporários que serão extraídos futuramente
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

                # Avança para o próximo e-mail usando a nova função
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
if __name__ == "__main__":
    processar()