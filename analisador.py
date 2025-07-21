# analisador.py
import tkinter as tk
from tkinter import scrolledtext, filedialog, messagebox
import os
from lexico import lex
from sintatico import AnalisadorSintatico

ARQUIVO_CODIGO = "index.mine"

GRAMATICA = """
<program>       ::= { <stmt> }
<stmt>          ::= <var_decl> | <assign> | <print> | <if> | <while> | <for> | <func_decl> | <return> | <call_stmt>
<var_decl>      ::= 'bau' ID '=' <expr> ';'
<assign>        ::= ID '=' <expr> ';'
<print>         ::= 'quadro' '(' <expr> { ',' <expr> } ')' ';'
<if>            ::= 'funil' '(' <expr> ')' '{' { <stmt> } '}' [ 'ejetor' '{' { <stmt> } '}' ]
<while>         ::= 'redstone' '(' <expr> ')' '{' { <stmt> } '}'
<for>           ::= 'trilho' '(' ( <var_decl> | ';' ) <expr>? ';' <expr>? ')' '{' { <stmt> } '}'
<func_decl>     ::= 'craftar' ID '(' [ 'bau' ID { ',' 'bau' ID } ] ')' '{' { <stmt> } '}'
<return>        ::= 'fornalha' <expr> ';'
<call_stmt>     ::= ID '(' [ <expr> { ',' <expr> } ] ')' ';'
<expr>          ::= <term> { OP_ARIT <term> }
<term>          ::= NUM | STRING | CHAR | ID [ '(' [ <expr> { ',' <expr> } ] ')' ] | '(' <expr> ')'
"""

def salvar_codigo(codigo: str, path=None):
    p = path or ARQUIVO_CODIGO
    with open(p, 'w', encoding='utf-8') as f: f.write(codigo)

def carregar_codigo(path=None) -> str:
    p = path or ARQUIVO_CODIGO
    if os.path.exists(p): return open(p,'r',encoding='utf-8').read()
    return ""

def criar_interface():
    janela = tk.Tk()
    janela.title("MineScript – IDE")
    janela.state('zoomed')
    bg, fg, hl = "#333333", "#ffffff", "#1e1e1e"
    janela.configure(bg=bg)

    # Menu
    menu = tk.Menu(janela)
    arquivo = tk.Menu(menu, tearoff=0)
    arquivo.add_command(label="Abrir", command=lambda: cmd_abrir())
    arquivo.add_command(label="Salvar", command=lambda: cmd_salvar())
    arquivo.add_separator()
    arquivo.add_command(label="Sair", command=janela.destroy)
    menu.add_cascade(label="Arquivo", menu=arquivo)

    ajuda = tk.Menu(menu, tearoff=0)
    ajuda.add_command(label="Gramática", command=lambda: messagebox.showinfo("Gramática MineScript", GRAMATICA))
    menu.add_cascade(label="Ajuda", menu=ajuda)

    janela.config(menu=menu)

    frame = tk.Frame(janela, bg=bg)
    frame.pack(fill=tk.BOTH, expand=True)

    # Editor
    tk.Label(frame, text="Código Min e Script", bg=bg, fg=fg).pack(anchor='nw', padx=10, pady=(10,0))
    entrada = scrolledtext.ScrolledText(frame, font=("Consolas",12), height=20,
                                        undo=True, bg=hl, fg=fg, insertbackground=fg)
    entrada.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    # Botões
    btns = tk.Frame(frame, bg=bg)
    btns.pack(fill=tk.X, pady=5)
    tk.Button(btns, text="Abrir", width=10, command=lambda: cmd_abrir()).pack(side=tk.LEFT, padx=5)
    tk.Button(btns, text="Salvar", width=10, command=lambda: cmd_salvar()).pack(side=tk.LEFT)
    tk.Button(btns, text="Listar Tokens", width=12, command=lambda: cmd_listar()).pack(side=tk.LEFT, padx=5)
    tk.Button(btns, text="Limpar", width=10, command=lambda: cmd_limpar()).pack(side=tk.LEFT)
    tk.Button(btns, text="Executar", width=10, command=lambda: cmd_executar()).pack(side=tk.LEFT, padx=5)
    tk.Button(btns, text="Sair", width=10, command=janela.destroy).pack(side=tk.LEFT)

    # Terminais
    term_frame = tk.PanedWindow(frame, sashrelief=tk.RAISED, sashwidth=5, bg=bg)
    term_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    lex_frame = tk.Frame(term_frame, bg=bg)
    tk.Label(lex_frame, text="Tokens", bg=bg, fg=fg).pack(anchor='nw')
    term_lex = scrolledtext.ScrolledText(lex_frame, font=("Consolas",12), height=8,
                                         bg=hl, fg='skyblue', insertbackground='skyblue')
    term_lex.pack(fill=tk.BOTH, expand=True)
    lex_frame.pack(fill=tk.BOTH, expand=True)
    term_frame.add(lex_frame)

    sint_frame = tk.Frame(term_frame, bg=bg)
    tk.Label(sint_frame, text="Sintático / Execução", bg=bg, fg=fg).pack(anchor='nw')
    term_sint = scrolledtext.ScrolledText(sint_frame, font=("Consolas",12), height=8,
                                          bg=hl, fg='yellow', insertbackground='yellow')
    term_sint.pack(fill=tk.BOTH, expand=True)
    sint_frame.pack(fill=tk.BOTH, expand=True)
    term_frame.add(sint_frame)

    ast_frame = tk.Frame(term_frame, bg=bg)
    # tk.Label(ast_frame, text="Árvore Sintática", bg=bg, fg=fg).pack(anchor='nw')
    # term_ast = scrolledtext.ScrolledText(ast_frame, font=("Consolas",12), height=8,
    #                                      bg=hl, fg='white', insertbackground='white')
    # term_ast.pack(fill=tk.BOTH, expand=True)
    # ast_frame.pack(fill=tk.BOTH, expand=True)
    # term_frame.add(ast_frame)

    # Comandos
    current_path = None
    def cmd_abrir():
        nonlocal current_path
        p = filedialog.askopenfilename(filetypes=[("MineScript","*.mine"),("All","*.*")])
        if p:
            current_path = p
            entrada.delete("1.0",tk.END)
            entrada.insert(tk.END, carregar_codigo(p))

    def cmd_salvar():
        nonlocal current_path
        if not current_path:
            p = filedialog.asksaveasfilename(defaultextension=".mine",
                filetypes=[("MineScript","*.mine")])
            if not p: return
            current_path = p
        salvar_codigo(entrada.get("1.0",tk.END), current_path)

    def cmd_listar():
        term_lex.delete("1.0",tk.END)
        term_sint.delete("1.0",tk.END)
        # term_ast.delete("1.0",tk.END)
        tokens = lex(entrada.get("1.0",tk.END))
        term_lex.insert(tk.END, "—— LISTAGEM DE TOKENS ——\n")
        for t in tokens[:-1]:
            term_lex.insert(tk.END, f"{t[0]:<12} {t[1]:<10}  (L{t[2]},C{t[3]})\n")

    def cmd_limpar():
        entrada.delete("1.0",tk.END)
        term_lex.delete("1.0",tk.END)
        term_sint.delete("1.0",tk.END)
        # term_ast.delete("1.0",tk.END)

    def cmd_executar():
        term_lex.delete("1.0",tk.END)
        term_sint.delete("1.0",tk.END)
        # term_ast.delete("1.0",tk.END)
        # Léxico
        tokens = lex(entrada.get("1.0",tk.END))
        term_lex.insert(tk.END, "—— Análise Léxica ——\n")
        for t in tokens[:-1]:
            term_lex.insert(tk.END, f"{t[0]:<12} {t[1]:<10}  (L{t[2]},C{t[3]})\n","token")
        # Sintaxe & Execução
        term_sint.insert(tk.END, "\n—— Sintático & Execução ——\n")
        analisador = AnalisadorSintatico(tokens, term_sint)
        program = analisador.parse()
        if not analisador.has_error:
            analisador.execute(program)
            term_sint.insert(tk.END, "\nPrograma executado com sucesso.\n")
        # AST
        # term_ast.insert(tk.END, "\n—— Árvore Sintática ——\n")
        analisador.print_tree(node=program)

    janela.mainloop()

if __name__ == "__main__":
    criar_interface()
