
# analisador.py
import tkinter as tk
from tkinter import scrolledtext
import re, os
from sintatico import AnalisadorSintatico

ARQUIVO_CODIGO = "index.mine"

def capturar_tokens(codigo):
    tabela_de_token = [
        ('COMENTARIO',   r'//[^\n]*'),
        ('VARIAVEL',     r'\bbau\b'),
        ('QUADRO',       r'\bquadro\b'),
        ('ATRIBUICAO',   r'='),
        ('IF',           r'\bfunil\b'),
        ('ELSE',         r'\bejetor\b'),
        ('LOOP_WHILE',   r'\bredstone\b'),
        ('LOOP_FOR',     r'\btrilho\b'),
        ('FUNCAO',       r'\bcraftar\b'),
        ('RETORNO',      r'\bfornalha\b'),
        ('OP_ARIT',      r'[+\-*/]'),
        ('OP_REL',       r'==|!=|>=|<=|>|<'),
        ('OP_LOGICO',    r'\b(e|ou|nao)\b'),
        ('DELIM',        r'[(){};,]'),
        ('NUM',          r'\d+(\.\d+)?'),
        ('ID',           r'[A-Za-z_][A-Za-z0-9_]*'),
        ('STRING',       r'"[^"\n]*"'),
        ('CHAR',         r"'[^'\n]'"),
        ('SKIP',         r'[ \t]+'),
        ('PULARLINHA',   r'\n+'),
        ('MISMATCH',     r'.'),
    ]
    tok_regex = '|'.join(f'(?P<{n}>{p})' for n,p in tabela_de_token)
    tokens = []
    for mo in re.finditer(tok_regex, codigo):
        kind, val = mo.lastgroup, mo.group()
        if kind in ('SKIP','COMENTARIO','PULARLINHA','MISMATCH'):
            continue
        tokens.append((kind, val))
    tokens.append(('EOF',''))
    return tokens

def salvar_codigo(codigo):
    with open(ARQUIVO_CODIGO, 'w', encoding='utf-8') as f:
        f.write(codigo)

def carregar_codigo():
    if os.path.exists(ARQUIVO_CODIGO):
        return open(ARQUIVO_CODIGO,'r',encoding='utf-8').read()
    return ""

def criar_interface():
    janela = tk.Tk()
    janela.title("MineScript – Analisador & Executor")
    janela.state('zoomed')
    bg, fg, hl = "#1e1e1e","#ffffff","#2d2d2d"
    janela.configure(bg=bg)
    frame = tk.Frame(janela,bg=bg); frame.pack(fill=tk.BOTH,expand=True)
    tk.Label(frame,text="Código MineScript:",bg=bg,fg=fg).pack(anchor='nw',padx=10,pady=(10,0))
    entrada = scrolledtext.ScrolledText(frame,font=("Consolas",12),height=15,undo=True,bg=hl,fg=fg,insertbackground=fg)
    entrada.pack(fill=tk.BOTH,expand=True,padx=10,pady=5); entrada.insert(tk.END, carregar_codigo())
    tk.Label(frame,text="Terminal:",bg=bg,fg=fg).pack(anchor='nw',padx=10,pady=(10,0))
    terminal = scrolledtext.ScrolledText(frame,font=("Consolas",12),height=10,bg=hl,fg='yellow',insertbackground='red')
    terminal.pack(fill=tk.BOTH,expand=True,padx=10,pady=5); terminal.tag_config("erro",foreground="red"); terminal.tag_config("token",foreground="skyblue")
    btn = tk.Button(frame,text="Executar",command=lambda: executar(entrada,terminal)); btn.pack(pady=10)
    def executar(entrada,terminal):
        codigo = entrada.get("1.0",tk.END); salvar_codigo(codigo); terminal.delete("1.0",tk.END)
        tokens = capturar_tokens(codigo)
        terminal.insert(tk.END,"—— Análise Léxica ——\n")
        for k,v in tokens[:-1]: terminal.insert(tk.END,f"Token:<{k}, {v}>\n","token")
        terminal.insert(tk.END,"\n—— Análise Sintática & Execução ——\n")
        analisador = AnalisadorSintatico(tokens, terminal)
        analisador.analisar()
        if not analisador.has_error: terminal.insert(tk.END,"Programa executado com sucesso.\n")
    janela.mainloop()

if __name__ == "__main__": 
    criar_interface()
