# sintatico.py
import tkinter as tk
from typing import List, Tuple, Any

# --- Nós da AST ---
class ASTNode: pass

class Program(ASTNode):
    def __init__(self, statements: List[ASTNode]):
        self.statements = statements

class VarDecl(ASTNode):
    def __init__(self, name: str, expr: ASTNode):
        self.name, self.expr = name, expr

class Assign(ASTNode):
    def __init__(self, name: str, expr: ASTNode):
        self.name, self.expr = name, expr

class FuncDecl(ASTNode):
    def __init__(self, name: str, params: List[str], body: List[ASTNode]):
        self.name, self.params, self.body = name, params, body

class Return(ASTNode):
    def __init__(self, expr: ASTNode):
        self.expr = expr

class Print(ASTNode):
    def __init__(self, args: List[ASTNode]):
        self.args = args

class Call(ASTNode):
    def __init__(self, name: str, args: List[ASTNode]):
        self.name, self.args = name, args

class BinOp(ASTNode):
    def __init__(self, left: ASTNode, op: str, right: ASTNode):
        self.left, self.op, self.right = left, op, right

class Literal(ASTNode):
    def __init__(self, value: Any):
        self.value = value

class Var(ASTNode):
    def __init__(self, name: str):
        self.name = name

# --- Parser / Interpretador ---
class AnalisadorSintatico:
    def __init__(self, tokens: List[Tuple[str,str,int,int]], terminal: tk.Text):
        self.tokens = tokens
        self.pos = 0
        self.terminal = terminal
        self.has_error = False
        self.declared = set()
        self.symbols = {}
        self.functions = {}

    def token_atual(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else ('EOF','',0,0)

    def peek(self):
        return self.tokens[self.pos+1] if self.pos+1 < len(self.tokens) else ('EOF','',0,0)

    def erro(self, msg: str, token=None):
        if token is None: token = self.token_atual()
        _, val, line, col = token
        self.terminal.insert(tk.END,
            f"[Linha {line}, Coluna {col}] {msg}: '{val}'\n", "erro")
        self.has_error = True

    def consumir(self, tipo: str, val: str=None):
        tok,valor,_,_ = self.token_atual()
        if tok == tipo and (val is None or valor == val):
            self.pos += 1
        else:
            esperado = tipo + (f" '{val}'" if val else "")
            self.erro(f"Erro sintático: esperado {esperado}", self.token_atual())
            self.pos += 1

    # ---- Parsing ----
    def parse(self) -> Program:
        stmts = []
        while self.token_atual()[0] != 'EOF':
            node = self.parse_stmt()
            if node: stmts.append(node)
        return Program(stmts)

    def parse_stmt(self):
        tok,_,line,col = self.token_atual()
        if tok == 'VARIAVEL': return self.parse_var_decl()
        if tok == 'ID' and self.peek()[0]=='ATRIBUICAO': return self.parse_assign()
        if tok == 'ID' and self.peek()[0]=='DELIM' and self.peek()[1]=='(': return self.parse_call_stmt()
        if tok == 'QUADRO': return self.parse_print()
        if tok == 'FUNCAO': return self.parse_func_decl()
        if tok == 'RETORNO': return self.parse_return()
        # erro genérico
        self.erro("Erro sintático: statement inesperado", self.token_atual())
        self.pos += 1
        return None

    def parse_var_decl(self):
        self.consumir('VARIAVEL')
        name = self.token_atual()[1]; self.consumir('ID')
        self.consumir('ATRIBUICAO')
        expr = self.parse_expr()
        self.consumir('DELIM')
        return VarDecl(name, expr)

    def parse_assign(self):
        name = self.token_atual()[1]; self.consumir('ID')
        self.consumir('ATRIBUICAO')
        expr = self.parse_expr()
        self.consumir('DELIM')
        return Assign(name, expr)

    def parse_call_stmt(self):
        call = self.parse_call_expr()
        self.consumir('DELIM')
        return call

    def parse_print(self):
        self.consumir('QUADRO'); self.consumir('DELIM','(')
        args = [self.parse_expr()]
        while self.token_atual()[1] == ',':
            self.consumir('DELIM',','); args.append(self.parse_expr())
        self.consumir('DELIM',')'); self.consumir('DELIM')
        return Print(args)

    def parse_func_decl(self):
        self.consumir('FUNCAO')
        name = self.token_atual()[1]; self.consumir('ID')
        self.consumir('DELIM','(')
        params = []
        while self.token_atual()[0] == 'VARIAVEL':
            self.consumir('VARIAVEL')
            pname = self.token_atual()[1]; self.consumir('ID')
            params.append(pname)
            if self.token_atual()[1] == ',':
                self.consumir('DELIM',',')
        self.consumir('DELIM',')'); self.consumir('DELIM','{')
        body = []
        while not (self.token_atual()[0]=='DELIM' and self.token_atual()[1]=='}'):
            node = self.parse_stmt()
            if node: body.append(node)
        self.consumir('DELIM','}')
        return FuncDecl(name, params, body)

    def parse_return(self):
        self.consumir('RETORNO')
        expr = self.parse_expr()
        self.consumir('DELIM')
        return Return(expr)

    def parse_expr(self):
        node = self.parse_term()
        while self.token_atual()[0] == 'OP_ARIT':
            op = self.token_atual()[1]; self.consumir('OP_ARIT')
            right = self.parse_term()
            node = BinOp(node, op, right)
        return node

    def parse_term(self):
        # suporte a número negativo
        tok, val, _, _ = self.token_atual()
        if tok == 'OP_ARIT' and val == '-':
            self.consumir('OP_ARIT')
            ntok,nval,_,_ = self.token_atual()
            if ntok == 'NUM':
                self.consumir('NUM')
                num = float(nval) if '.' in nval else int(nval)
                return Literal(-num)
            # se não for literal, faz 0 - termo
            right = self.parse_term()
            return BinOp(Literal(0), '-', right)

        if tok == 'NUM':
            self.consumir('NUM')
            return Literal(float(val) if '.' in val else int(val))
        if tok == 'STRING':
            self.consumir('STRING')
            return Literal(val.strip('"'))
        if tok == 'CHAR':
            self.consumir('CHAR')
            return Literal(val.strip("'"))
        if tok == 'ID' and self.peek()[0]=='DELIM' and self.peek()[1]=='(':
            return self.parse_call_expr()
        if tok == 'ID':
            self.consumir('ID')
            return Var(val)
        if tok == 'DELIM' and val=='(':
            self.consumir('DELIM','(')
            node = self.parse_expr()
            self.consumir('DELIM',')')
            return node

        self.erro("Erro sintático: termo inválido", self.token_atual())
        self.pos += 1
        return None

    def parse_call_expr(self):
        name = self.token_atual()[1]; self.consumir('ID')
        self.consumir('DELIM','(')
        args = []
        if self.token_atual()[1] != ')':
            args.append(self.parse_expr())
            while self.token_atual()[1] == ',':
                self.consumir('DELIM',','); args.append(self.parse_expr())
        self.consumir('DELIM',')')
        return Call(name, args)

    # ---- Execução ----
    def execute(self, node: ASTNode):
        if isinstance(node, Program):
            for s in node.statements: self.execute(s)
        elif isinstance(node, VarDecl):
            self.declared.add(node.name)
            self.symbols[node.name] = self.eval_expr(node.expr)
        elif isinstance(node, Assign):
            self.symbols[node.name] = self.eval_expr(node.expr)
        elif isinstance(node, Print):
            out = ''.join(str(self.eval_expr(a)) for a in node.args)
            self.terminal.insert(tk.END, out + "\n")
        elif isinstance(node, FuncDecl):
            self.functions[node.name] = (node.params, node.body)
        elif isinstance(node, Return):
            self.symbols['__return__'] = self.eval_expr(node.expr)
        elif isinstance(node, Call):
            args = [self.eval_expr(a) for a in node.args]
            if node.name not in self.functions:
                self.erro(f"Erro semântico: função '{node.name}' não declarada", self.token_atual())
                return
            params, body = self.functions[node.name]
            old_sym, old_dec = dict(self.symbols), set(self.declared)
            for p,v in zip(params,args):
                self.declared.add(p); self.symbols[p]=v
            for s in body: self.execute(s)
            ret = self.symbols.get('__return__', None)
            self.symbols, self.declared = old_sym, old_dec
            return ret

    def eval_expr(self, node: ASTNode):
        if isinstance(node, Literal): return node.value
        if isinstance(node, Var):     return self.symbols.get(node.name, None)
        if isinstance(node, BinOp):
            l = self.eval_expr(node.left); r = self.eval_expr(node.right)
            return {'+':l+r,'-':l-r,'*':l*r,'/':l/r}[node.op]
        if isinstance(node, Call):
            return self.execute(node)
        return None

    # ---- Impressão da AST ----
    def print_tree(self, node=None, indent=0):
        if node is None:
            self.pos = 0
            node = self.parse()
        pad = '  '*indent
        t = type(node).__name__
        info = getattr(node,'name', getattr(node,'value',''))
        self.terminal.insert(tk.END, f"{pad}{t}" + (f": {info}" if info!="" else "") + "\n")
        for field in ('statements','body','args','expr','left','right'):
            val = getattr(node,field,None)
            if isinstance(val, list):
                for c in val: self.print_tree(c, indent+1)
            elif val and isinstance(val, ASTNode):
                self.print_tree(val, indent+1)
