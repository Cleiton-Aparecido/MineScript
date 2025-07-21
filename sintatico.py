import tkinter as tk
from typing import List, Tuple, Any

class AnalisadorSintatico:
    def __init__(self, tokens: List[Tuple[str, str]], terminal: tk.Text):
        self.tokens = tokens
        self.pos = 0
        self.terminal = terminal
        self.has_error = False
        self.declared = set()
        self.symbols = {}
        self.functions = {}

    def token_atual(self) -> Tuple[str, str]:
        return self.tokens[self.pos] if self.pos < len(self.tokens) else ('EOF', '')

    def peek(self) -> Tuple[str, str]:
        return self.tokens[self.pos+1] if self.pos+1 < len(self.tokens) else ('EOF', '')

    def consumir(self, tipo: str):
        if self.token_atual()[0] == tipo:
            self.pos += 1
        else:
            self.terminal.insert(
                tk.END,
                f"Erro sintático: esperado {tipo}, encontrado {self.token_atual()[0]}\n",
                "erro"
            )
            self.has_error = True
            self.pos += 1

    def analisar(self):
        while self.token_atual()[0] != 'EOF':
            tok = self.token_atual()[0]
            if tok == 'FUNCAO':
                self.func_decl()
            elif tok == 'QUADRO':
                self.print_stmt()
            else:
                self.stmt()

    def stmt(self):
        tok = self.token_atual()[0]
        # Chamada de função
        if tok == 'ID' and self.peek()[0] == 'DELIM' and self.peek()[1] == '(':
            _ = self.expr()
            self.consumir('DELIM')  # ;
        elif tok == 'QUADRO':
            self.print_stmt()
        elif tok in ('VARIAVEL', 'ID'):
            self.atribuicao()
        elif tok == 'IF':
            self.if_stmt()
        elif tok == 'LOOP_WHILE':
            self.while_stmt()
        elif tok == 'LOOP_FOR':
            self.for_stmt()
        elif tok == 'RETORNO':
            self.return_stmt()
        else:
            val = self.token_atual()[1]
            self.terminal.insert(
                tk.END,
                f"Erro sintático: statement inesperado '{val}'\n",
                "erro"
            )
            self.has_error = True
            self.pos += 1

    def func_decl(self):
        # craftar nome(params) { corpo }
        self.consumir('FUNCAO')
        name = self.token_atual()[1]; self.consumir('ID')
        self.consumir('DELIM')  # (
        params: List[str] = []
        if self.token_atual()[0] == 'VARIAVEL':
            while True:
                self.consumir('VARIAVEL')
                pname = self.token_atual()[1]; self.consumir('ID')
                params.append(pname)
                if self.token_atual() == ('DELIM', ','):
                    self.consumir('DELIM')
                else:
                    break
        self.consumir('DELIM')  # )
        self.consumir('DELIM')  # {
        start = self.pos
        depth = 1
        while depth > 0:
            tok, val = self.token_atual()
            if tok == 'EOF':
                self.terminal.insert(
                    tk.END,
                    f"Erro sintático: função '{name}' sem '}}' de fechamento\n",
                    "erro"
                )
                self.has_error = True
                break
            if tok == 'DELIM' and val == '{': depth += 1
            elif tok == 'DELIM' and val == '}': depth -= 1
            self.pos += 1
        end = self.pos - 1
        body = self.tokens[start:end]
        if self.token_atual() == ('DELIM', '}'):
            self.consumir('DELIM')
        self.functions[name] = (params, body)

    def atribuicao(self):
        if self.token_atual()[0] == 'VARIAVEL':
            self.consumir('VARIAVEL')
            name = self.token_atual()[1]; self.consumir('ID')
            self.declared.add(name)
        else:
            name = self.token_atual()[1]
            if name not in self.declared:
                self.terminal.insert(
                    tk.END,
                    f"Erro semântico: variável '{name}' não declarada\n",
                    "erro"
                )
                self.has_error = True
            self.consumir('ID')
        self.consumir('ATRIBUICAO')
        val = self.expr()
        self.symbols[name] = val
        self.consumir('DELIM')

    def print_stmt(self):
        self.consumir('QUADRO'); self.consumir('DELIM')  # (
        vals = [self.expr()]
        while self.token_atual() == ('DELIM', ','):
            self.consumir('DELIM'); vals.append(self.expr())
        self.consumir('DELIM')  # )
        if self.token_atual() == ('DELIM', ';'):
            self.consumir('DELIM')
        self.terminal.insert(tk.END, ''.join(str(v) for v in vals) + '\n')

    def return_stmt(self):
        self.consumir('RETORNO')
        self.symbols['__return__'] = self.expr()
        self.consumir('DELIM')

    def if_stmt(self):
        self.consumir('IF'); self.consumir('DELIM')  # (
        cond = self.expr(); self.consumir('DELIM')  # )
        if cond:
            self.consumir('DELIM')  # {
            while not (self.token_atual() == ('DELIM', '}')):
                self.stmt()
            self.consumir('DELIM')  # }
            if self.token_atual()[0] == 'ELSE':
                self.consumir('ELSE'); self.skip_block_body()
        else:
            self.skip_block_body()
            if self.token_atual()[0] == 'ELSE':
                self.consumir('ELSE'); self.skip_block_body()

    def while_stmt(self):
        self.consumir('LOOP_WHILE'); self.consumir('DELIM')  # (
        start = self.pos
        cond = self.expr(); self.consumir('DELIM')  # )
        if cond:
            self.consumir('DELIM')  # {
            while cond:
                checkpoint = self.pos
                while not (self.token_atual() == ('DELIM', '}')):
                    self.stmt()
                self.consumir('DELIM')  # }
                self.pos = start; cond = self.expr(); self.consumir('DELIM')
            self.skip_block_body()
        else:
            self.skip_block_body()

    def for_stmt(self):
        self.consumir('LOOP_FOR'); self.consumir('DELIM')  # (
        if self.token_atual()[0] == 'VARIAVEL':
            self.atribuicao()
        elif self.token_atual()[1] == ';':
            self.consumir('DELIM')
        cond = True
        if self.token_atual()[1] != ';':
            cond = self.expr()
        self.consumir('DELIM')
        post_start = self.pos
        if self.token_atual()[1] != ')':
            self.expr()
        self.consumir('DELIM')
        if cond:
            while cond:
                self.skip_to_body()
                while not (self.token_atual() == ('DELIM', '}')):
                    self.stmt()
                self.consumir('DELIM')
                self.pos = post_start; cond = self.expr(); self.consumir('DELIM')
            self.skip_block_body()
        else:
            self.skip_block_body()

    def expr(self) -> Any:
        return self.expr_logic()

    def expr_logic(self) -> Any:
        left = self.expr_rel()
        while self.token_atual()[0] == 'OP_LOGICO':
            op = self.token_atual()[1]; self.consumir('OP_LOGICO')
            right = self.expr_rel()
            if op == 'e': left = left and right
            else: left = left or right
        return left

    def expr_rel(self) -> Any:
        left = self.expr_arit()
        if self.token_atual()[0] == 'OP_REL':
            op = self.token_atual()[1]; self.consumir('OP_REL')
            right = self.expr_arit()
            left = {
                '==': left == right, '!=': left != right,
                '>': left > right, '<': left < right,
                '>=': left >= right, '<=': left <= right
            }[op]
        return left

    def expr_arit(self) -> Any:
        val = self.term()
        while self.token_atual()[0] == 'OP_ARIT':
            op = self.token_atual()[1]; self.consumir('OP_ARIT')
            right = self.term()
            if op == '+': val = val + right
            elif op == '-': val = val - right
            elif op == '*': val = val * right
            elif op == '/': val = val / right
        return val

    def term(self) -> Any:
        tok, val = self.token_atual()
        if tok == 'OP_ARIT' and val == '-':
            self.consumir('OP_ARIT'); return -self.term()
        if tok == 'NUM':
            self.consumir('NUM'); return float(val) if '.' in val else int(val)
        if tok == 'STRING':
            self.consumir('STRING'); return val.strip('"')
        if tok == 'CHAR':
            self.consumir('CHAR'); return val.strip("'")
        if tok == 'ID' and self.peek()[0] == 'DELIM' and self.peek()[1] == '(':
            name = val; self.consumir('ID'); self.consumir('DELIM')
            args = []
            if not self.token_atual() == ('DELIM', ')'):
                args.append(self.expr())
                while self.token_atual() == ('DELIM', ','):
                    self.consumir('DELIM'); args.append(self.expr())
            self.consumir('DELIM')
            if name not in self.functions:
                self.terminal.insert(
                    tk.END,
                    f"Erro semântico: função '{name}' não declarada\n",
                    "erro"
                )
                self.has_error = True; return None
            params, body = self.functions[name]
            old_sym, old_dec = self.symbols.copy(), self.declared.copy()
            for p, a in zip(params, args):
                self.declared.add(p); self.symbols[p] = a
            child = AnalisadorSintatico(body + [('EOF','')], self.terminal)
            child.declared, child.symbols, child.functions = (
                self.declared.copy(), self.symbols.copy(), self.functions
            )
            child.analisar()
            ret = child.symbols.get('__return__', None)
            self.symbols, self.declared = old_sym, old_dec
            return ret
        if tok == 'ID':
            if val not in self.symbols:
                self.terminal.insert(
                    tk.END,
                    f"Erro semântico: variável '{val}' não declarada\n",
                    "erro"
                )
                self.has_error = True; self.pos += 1; return None
            self.consumir('ID'); return self.symbols[val]
        if tok == 'DELIM' and val == '(':
            self.consumir('DELIM'); v = self.expr(); self.consumir('DELIM'); return v
        self.terminal.insert(
            tk.END,
            f"Erro sintático: termo inválido '{val}'\n",
            "erro"
        )
        self.has_error = True; self.pos += 1; return None

    def skip_to_body(self):
        while self.token_atual()[0] != 'EOF' and self.token_atual() != ('DELIM','{'):
            self.pos += 1
        if self.token_atual() == ('DELIM','{'): self.consumir('DELIM')

    def skip_block_body(self):
        depth = 0
        while self.token_atual()[0] != 'EOF':
            tok, val = self.token_atual()
            if tok == 'DELIM' and val == '{': depth += 1
            elif tok == 'DELIM' and val == '}':
                if depth == 0:
                    self.consumir('DELIM'); return
                depth -= 1
            self.pos += 1