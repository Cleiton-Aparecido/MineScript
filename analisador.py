import tkinter as tk
from tkinter import scrolledtext
import re
import os

ARQUIVO_CODIGO = "index.mine"

def analisador_lexico(codigo, terminal):
    tabela_de_token = [
        ('COMENTARIO',   r'//[^\n]*'),
        ('VARIAVEL',     r'\bbau\b'),
        ('ATRIBUICAO',   r'='),
        ('IF',           r'\bfunil\b'),
        ('ELSE',         r'\bejetor\b'),
        ('LOOP_WHILE',   r'\bredstone\b'),
        ('LOOP_FOR',     r'\btrilho\b'),
        ('FUNCAO',       r'\bcraftar\b'),
        ('RETORNO',      r'\bfornalha\b'),
        ('OP_ARIT',      r'\+|\-|\*'),
        ('OP_REL',       r'==|!=|>=|<=|>|<'),
        ('OP_LOGICO',    r'\be\b|\bou\b|\bnao\b'),
        ('DELIM',        r'\(|\)|\{|\}|;'),
        ('NUM',          r'\d+(\.\d+)?'),
        ('ID',           r'[a-zA-Z_][a-zA-Z0-9_]*'),
        ('STRING',       r'"[^"\n]*"?'),
        ('CHAR',         r"'[^'\n]?'?"),
        ('SKIP',         r'[ \t]+'),
        ('PularLinha',   r'\n'),
        ('MISMATCH',     r'.'),
    ]

    tok_regex = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in tabela_de_token)
    palavras_reservadas = {'bau', 'funil', 'ejetor', 'redstone', 'trilho', 'craftar', 'fornalha', 'e', 'ou', 'nao'}

    line_num = 1
    line_start = 0
    pilha_chaves = []

    terminal.delete('1.0', tk.END)

    for mo in re.finditer(tok_regex, codigo):
        kind = mo.lastgroup
        value = mo.group()
        column = mo.start() - line_start + 1

        if kind == 'PularLinha':
            line_num += 1
            line_start = mo.end()
        elif kind == 'SKIP' or kind == 'COMENTARIO':
            continue
        elif kind == 'DELIM':
            if value == '{':
                pilha_chaves.append((line_num, column))
            elif value == '}':
                if pilha_chaves:
                    pilha_chaves.pop()
                else:
                    terminal.insert(tk.END, f"Linha {line_num}, Coluna {column}: Erro: chave '}}' sem abertura\n")
        elif kind == 'MISMATCH':
            if value == '/':
                terminal.insert(tk.END, f"Linha {line_num}, Coluna {column}: Erro: uso incorreto de comentário ou símbolo inválido '{value}'\n")
            else:
                terminal.insert(tk.END, f"Linha {line_num}, Coluna {column}: Erro: símbolo inválido '{value}'\n")
        elif kind == 'ID':
            if value not in palavras_reservadas and any(value.startswith(p) for p in palavras_reservadas):
                terminal.insert(tk.END, f"Linha {line_num}, Coluna {column}: Erro: palavra reservada mal escrita '{value}'\n")
            elif re.match(r'\d', value):
                terminal.insert(tk.END, f"Linha {line_num}, Coluna {column}: Erro: identificador mal formado '{value}'\n")
            elif len(value) > 20:
                terminal.insert(tk.END, f"Linha {line_num}, Coluna {column}: Erro: identificador muito longo '{value}'\n")
        elif kind == 'NUM':
            if len(value.replace('.', '')) > 10:
                terminal.insert(tk.END, f"Linha {line_num}, Coluna {column}: Erro: número muito grande '{value}'\n")
            elif re.search(r'\d+\.\D|\.\d+', value):
                terminal.insert(tk.END, f"Linha {line_num}, Coluna {column}: Erro: número mal formado '{value}'\n")
        elif kind == 'STRING':
            if not value.endswith('"'):
                terminal.insert(tk.END, f"Linha {line_num}, Coluna {column}: Erro: string mal formada '{value}'\n")
        elif kind == 'CHAR':
            if not value.endswith("'"):
                terminal.insert(tk.END, f"Linha {line_num}, Coluna {column}: Erro: caractere mal formado '{value}'\n")
        else:
            terminal.insert(tk.END, f"Linha {line_num}, Coluna {column}: Token:<{kind}, {value}>\n", 'token')
    for linha, coluna in pilha_chaves:
        terminal.insert(tk.END, f"Linha {linha}, Coluna {coluna}: Erro: chave '{{' aberta sem fechamento\n")

def salvar_codigo(codigo):
    with open(ARQUIVO_CODIGO, 'w', encoding='utf-8') as f:
        f.write(codigo)

def carregar_codigo():
    if os.path.exists(ARQUIVO_CODIGO):
        with open(ARQUIVO_CODIGO, 'r', encoding='utf-8') as f:
            return f.read()
    return ""

def criar_interface():
    janela = tk.Tk()
    janela.title("MineScript - Analisador Léxico")
    janela.state('zoomed')

    bg = "#1e1e1e"
    fg = "#ffffff"
    highlight = "#2d2d2d"


    janela.configure(bg=bg)

    frame_principal = tk.Frame(janela, bg=bg)
    frame_principal.pack(fill=tk.BOTH, expand=True)

    label1 = tk.Label(frame_principal, text="Código MineScript:", bg=bg, fg=fg)
    label1.pack(anchor='nw', padx=10, pady=(10, 0))

    entrada = scrolledtext.ScrolledText(frame_principal, font=("Consolas", 12), height=15,
                                        undo=True, bg=highlight, fg=fg, insertbackground=fg)
    entrada.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    entrada.insert(tk.END, carregar_codigo())

   
    
    label2 = tk.Label(frame_principal, text="terminal:", bg=bg, fg=fg)
    label2.pack(anchor='nw', padx=10, pady=(10, 0))

    terminal = scrolledtext.ScrolledText(frame_principal, font=("Consolas", 12), height=10,
                                      fg='yellow', bg=highlight, insertbackground='red')
    terminal.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
    terminal.tag_config("erro", foreground="red")
    terminal.tag_config("token", foreground="skyblue")  # opcional

    frame_botoes = tk.Frame(janela, bg=bg)
    frame_botoes.pack(fill=tk.X, padx=10, pady=10)

    def executar():
        codigo = entrada.get("1.0", tk.END)
        salvar_codigo(codigo)
        analisador_lexico(codigo, terminal)

    tk.Button(frame_botoes, text="Executar Análise", bg="green", fg="white", font=("Arial", 12),
              command=executar).pack(side=tk.LEFT, padx=10)

    tk.Button(frame_botoes, text="Limpar Saída", bg="orange", fg="white", font=("Arial", 12),
              command=lambda: terminal.delete("1.0", tk.END)).pack(side=tk.LEFT, padx=10)

    tk.Button(frame_botoes, text="Sair", bg="red", fg="white", font=("Arial", 12),
              command=janela.destroy).pack(side=tk.RIGHT, padx=10)

    codigo = entrada.get("1.0", tk.END)
    entrada.bind('<Control-s>', salvar_codigo(codigo))

    janela.mainloop()

criar_interface()
