# sintatico.py
import tkinter as tk

# Classe principal do analisador sintático/executador MineScript
class AnalisadorSintatico:
    def __init__(self, tokens, terminal):
        # tokens: lista de pares (TIPO, valor)
        # terminal: widget Tkinter para exibir mensagens e resultados
        self.tokens = tokens
        self.pos = 0                 # posição atual na lista de tokens
        self.terminal = terminal
        self.has_error = False       # flag de erro sintático/semântico
        self.declared = set()        # variáveis declaradas
        self.symbols = {}            # tabela de símbolos (nome -> valor)
        self.functions = {}          # tabela de funções (nome -> (params, body_tokens))

    def token_atual(self):
        # Retorna o token atual ou EOF se no final
        return self.tokens[self.pos] if self.pos < len(self.tokens) else ('EOF', '')

    def peek(self):
        # Olha o próximo token sem consumir
        return self.tokens[self.pos+1] if self.pos+1 < len(self.tokens) else ('EOF', '')

    def consumir(self, tipo):
        # Se o token atual for do tipo esperado, avança; senão, registra erro e avança
        if self.token_atual()[0] == tipo:
            self.pos += 1
        else:
            self.terminal.insert(tk.END,
                f"Erro sintático: esperado {tipo}, encontrado {self.token_atual()[0]}\n",
                "erro"
            )
            self.has_error = True
            self.pos += 1

    def analisar(self):
        # Loop principal: percorre todos os tokens até EOF
        while self.token_atual()[0] != 'EOF':
            tok = self.token_atual()[0]
            if tok == 'FUNCAO':
                # Declaração de função
                self.func_decl()
            elif tok == 'QUADRO':
                # Comando de impressão
                self.print_stmt()
            else:
                # Qualquer outro statement
                self.stmt()

    def stmt(self):
        # Identifica e executa diferentes tipos de statements
        tok = self.token_atual()[0]
        # Chamada de função como statement: exemplo ─ foo(1,2);
        if tok == 'ID' and self.peek()[0] == 'DELIM' and self.peek()[1] == '(':
            _ = self.expr()        # avalia call expression
            self.consumir('DELIM') # consome o ";"
        elif tok == 'QUADRO':
            # comando de print
            self.print_stmt()
        elif tok in ('VARIAVEL', 'ID'):
            # declaração ou atribuição de variável
            self.atribuicao()
        elif tok == 'IF':
            self.if_stmt()         # if/else
        elif tok == 'LOOP_WHILE':
            self.while_stmt()      # while
        elif tok == 'LOOP_FOR':
            self.for_stmt()        # for
        elif tok == 'RETORNO':
            # return dentro de função
            self.return_stmt()
        else:
            # qualquer outro token inesperado é erro
            val = self.token_atual()[1]
            self.terminal.insert(tk.END,
                f"Erro sintático: statement inesperado '{val}'\n",
                "erro"
            )
            self.has_error = True
            self.pos += 1

    def func_decl(self):
        # Declaração de função: craftar nome(params) { corpo }
        self.consumir('FUNCAO')            # consome 'craftar'
        name = self.token_atual()[1]
        self.consumir('ID')                # nome da função
        self.consumir('DELIM')             # '('
        # lê parâmetros: bau a, bau b, ...
        params = []
        if self.token_atual()[0] == 'VARIAVEL':
            while True:
                self.consumir('VARIAVEL')
                pname = self.token_atual()[1]
                self.consumir('ID')
                params.append(pname)
                if self.token_atual()[0] == 'DELIM' and self.token_atual()[1] == ',':
                    self.consumir('DELIM')
                else:
                    break
        self.consumir('DELIM')             # ')'
        # espera '{'
        if self.token_atual()[0] == 'DELIM' and self.token_atual()[1] == '{':
            self.consumir('DELIM')
        else:
            self.terminal.insert(tk.END, f"Erro sintático: esperado '{{' após função '{name}'\n", "erro")
            self.has_error = True
        # captura o corpo da função até fechar todas as chaves
        start = self.pos
        depth = 1
        while depth > 0:
            tok, val = self.token_atual()
            if tok == 'EOF':
                # fim inesperado sem '}'
                self.terminal.insert(tk.END, f"Erro sintático: função '{name}' sem '}}' de fechamento\n", "erro")
                self.has_error = True
                break
            if tok == 'DELIM' and val == '{': depth += 1
            elif tok == 'DELIM' and val == '}': depth -= 1
            self.pos += 1
        end = self.pos - 1
        body = self.tokens[start:end]
        # consome '}' final, se existir
        if self.token_atual()[0] == 'DELIM' and self.token_atual()[1] == '}':
            self.consumir('DELIM')
        # armazena na tabela de funções
        self.functions[name] = (params, body)

    def atribuicao(self):
        # Declaração ou atribuição de variável
        if self.token_atual()[0] == 'VARIAVEL':
            self.consumir('VARIAVEL')
            name = self.token_atual()[1]
            self.consumir('ID')
            self.declared.add(name)
        else:
            name = self.token_atual()[1]
            if name not in self.declared:
                # variável precisa existir antes
                self.terminal.insert(tk.END, f"Erro semântico: variável '{name}' não declarada\n", "erro")
                self.has_error = True
            self.consumir('ID')
        self.consumir('ATRIBUICAO')         # '='
        val = self.expr()                   # avalia expressão
        self.symbols[name] = val            # armazena valor
        self.consumir('DELIM')              # ';'

    def print_stmt(self):
        # Comando de impressão: quadro(arg1, arg2, ...);
        self.consumir('QUADRO')
        self.consumir('DELIM')  # '('
        vals = [self.expr()]
        # múltiplos argumentos separados por vírgula
        while self.token_atual()[0] == 'DELIM' and self.token_atual()[1] == ',':
            self.consumir('DELIM')
            vals.append(self.expr())
        self.consumir('DELIM')  # ')'
        if self.token_atual()[0] == 'DELIM' and self.token_atual()[1] == ';':
            self.consumir('DELIM')
        # concatena e imprime
        self.terminal.insert(tk.END, ''.join(str(v) for v in vals) + '\n')

    def return_stmt(self):
        # 'fornalha expr;' retorna valor de função
        self.consumir('RETORNO')
        val = self.expr()
        self.symbols['__return__'] = val
        self.consumir('DELIM')

    # Métodos para estruturas condicionais e loops seguem a mesma lógica de consumo e execução
    def if_stmt(self): ...  # código permanece comentado acima
    def while_stmt(self): ...
    def for_stmt(self):   ...

    # Expressões lógicas, relacionais e aritméticas:
    def expr(self):
        return self.expr_logic()

    def expr_logic(self): ...
    def expr_rel(self):   ...
    def expr_arit(self):  ...

    def term(self):
        # Termo: número, string, variável ou chamada de função
        tok, val = self.token_atual()
        # unary minus
        if tok == 'OP_ARIT' and val == '-':
            self.consumir('OP_ARIT')
            return -self.term()
        # números literais
        if tok == 'NUM':
            self.consumir('NUM'); return float(val) if '.' in val else int(val)
        # strings
        if tok == 'STRING':
            self.consumir('STRING'); return val.strip('"')
        # chars
        if tok == 'CHAR':
            self.consumir('CHAR'); return val.strip("'")
        # variáveis e chamadas de função
        if tok == 'ID': ...
        # expressões entre parênteses
        if tok == 'DELIM' and val == '(':
            self.consumir('DELIM'); v = self.expr(); self.consumir('DELIM'); return v
        # termo inválido
        self.terminal.insert(tk.END, f"Erro sintático: termo inválido '{val}'\n", "erro")
        self.has_error = True
        self.pos += 1
        return None

    # Métodos auxiliares para navegação de blocos
    def skip_to_body(self): ...
    def skip_block_body(self): ...

# analisador.py (permanece inalterado)
# Ele configura a interface Tkinter, chama o lexer (capturar_tokens)
# e depois cria AnalisadorSintatico(tokens, terminal).analisar()
