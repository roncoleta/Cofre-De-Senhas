import speech_recognition as sr
import pyttsx3
from cryptography.fernet import Fernet
import sqlite3

# Inicializar o mecanismo de voz
engine = pyttsx3.init()

# Função para falar
def falar(texto):
    engine.say(texto)
    engine.runAndWait()

# Função para capturar comando de voz
def ouvir_comando():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Diga algo...")
        audio = recognizer.listen(source)
        try:
            comando = recognizer.recognize_google(audio, language="pt-BR")
            print("Você disse:", comando)
            return comando.lower()
        except sr.UnknownValueError:
            falar("Desculpe, não consegui entender. Tente novamente.")
            return None
        except sr.RequestError:
            falar("Erro na API de reconhecimento de voz.")
            return None

# Gera uma chave de criptografia
def gerar_chave():
    chave = Fernet.generate_key()
    with open("chave.key", "wb") as chave_file:
        chave_file.write(chave)

# Carrega a chave de criptografia
def carregar_chave():
    with open("chave.key", "rb") as chave_file:
        return chave_file.read()

# Inicializa a chave
try:
    chave = carregar_chave()
except FileNotFoundError:
    gerar_chave()
    chave = carregar_chave()

fernet = Fernet(chave)

# Banco de dados
conn = sqlite3.connect("cofre_senhas.db")
cursor = conn.cursor()

# Criação da tabela
cursor.execute("""
CREATE TABLE IF NOT EXISTS senhas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plataforma TEXT NOT NULL,
    usuario TEXT NOT NULL,
    senha BLOB NOT NULL
)
""")
conn.commit()

# Função para adicionar uma senha
def adicionar_senha(plataforma, usuario, senha):
    senha_criptografada = fernet.encrypt(senha.encode())
    cursor.execute("INSERT INTO senhas (plataforma, usuario, senha) VALUES (?, ?, ?)", (plataforma, usuario, senha_criptografada))
    conn.commit()
    falar("Senha adicionada com sucesso.")

# Função para listar senhas
def listar_senhas():
    cursor.execute("SELECT plataforma, usuario FROM senhas")
    registros = cursor.fetchall()
    if registros:
        for plataforma, usuario in registros:
            falar(f"Plataforma: {plataforma}, Usuário: {usuario}")
    else:
        falar("Nenhuma senha encontrada.")

# Função para acessar uma senha
def acessar_senha(plataforma):
    cursor.execute("SELECT usuario, senha FROM senhas WHERE plataforma = ?", (plataforma,))
    registro = cursor.fetchone()
    if registro:
        usuario, senha_criptografada = registro
        senha = fernet.decrypt(senha_criptografada).decode()
        falar(f"Usuário: {usuario}, Senha: {senha}")
    else:
        falar("Nenhuma senha encontrada para essa plataforma.")

# Função principal
def main():
    falar("Bem-vindo ao cofre de senhas com reconhecimento de voz.")
    while True:
        falar("Diga uma opção: adicionar senha, listar senhas, acessar senha ou sair.")
        comando = ouvir_comando()
        
        if comando is None:
            continue
        elif "adicionar senha" in comando:
            falar("Diga o nome da plataforma.")
            plataforma = ouvir_comando()
            falar("Diga o nome de usuário.")
            usuario = ouvir_comando()
            falar("Diga a senha.")
            senha = ouvir_comando()
            if plataforma and usuario and senha:
                adicionar_senha(plataforma, usuario, senha)
        elif "listar senhas" in comando:
            listar_senhas()
        elif "acessar senha" in comando:
            falar("Diga o nome da plataforma.")
            plataforma = ouvir_comando()
            if plataforma:
                acessar_senha(plataforma)
        elif "sair" in comando:
            falar("Encerrando o cofre de senhas.")
            break
        else:
            falar("Comando não reconhecido. Tente novamente.")

# Executar o programa principal
if __name__ == "__main__":
    main() 