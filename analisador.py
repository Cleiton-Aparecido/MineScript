import tkinter as tk
from tkinter import scrolledtext
import os
from lexico import lex
from sintatico import AnalisadorSintatico

ARQUIVO_CODIGO = "index.mine"

def salvar_codigo(codigo: str):
    with open(ARQUIVO_CODIGO, 'w', encoding='utf-8') as f:
        f.write(codigo)

def carregar_codigo() -> str:
    if os.path.exists(ARQUIVO_CODIGO):
        return open(ARQUIVO_CODIGO, 'r', encoding='utf-8').read()
    return ""

def criar_interface():
    janela = tk.Tk()
    janela.title("MineScript – IDE")
    janela.state('zoomed')

    bg, fg, hl = "#6e6d6d", "#ffffff", "#2d2d2d"
    janela.configure(bg=bg)

    frame = tk.Frame(janela, bg=bg)
    frame.pack(fill=tk.BOTH, expand=True)

    tk.Label(frame, text="Código MineScript:", bg=bg, fg=fg).pack(anchor='nw', padx=10, pady=(10,0))
    entrada = scrolledtext.ScrolledText(
        frame, font=("Consolas", 12), height=15,
        undo=True, bg=hl, fg=fg, insertbackground=fg
    )
    entrada.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
    entrada.insert(tk.END, carregar_codigo())

    tk.Label(frame, text="Terminal:", bg=bg, fg=fg).pack(anchor='nw', padx=10, pady=(10,0))
    terminal = scrolledtext.ScrolledText(
        frame, font=("Consolas", 12), height=10,
        bg=hl, fg='yellow', insertbackground='green'
    )
    terminal.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
    terminal.tag_config("erro", foreground="green")
    terminal.tag_config("token", foreground="skyblue")

    def executar():
        codigo = entrada.get("1.0", tk.END)
        salvar_codigo(codigo)
        terminal.delete("1.0", tk.END)

        tokens = lex(codigo)
        terminal.insert(tk.END, "—— Análise Léxica ——\n")
        for k, v in tokens[:-1]:
            terminal.insert(tk.END, f"Token:<{k}, {v}>\n", "token")

        terminal.insert(tk.END, "\n—— Análise Sintática & Execução ——\n")
        analisador = AnalisadorSintatico(tokens, terminal)
        analisador.analisar()
        if not analisador.has_error:
            terminal.insert(tk.END, "Programa executado com sucesso.\n")

    btn = tk.Button(frame, text="Executar", command=executar)
    btn.pack(pady=10)

    janela.mainloop()

if __name__ == "__main__":
    criar_interface()