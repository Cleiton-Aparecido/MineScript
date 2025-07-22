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

class While(ASTNode):
    def __init__(self, condition: ASTNode, body: List[ASTNode]):
        self.condition = condition
        self.body = body

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
        if token is None:
            token = self.token_atual()
        _, val, line, col = token
        self.terminal.insert(tk.END, f"[Linha {line}, Coluna {col}] {msg}: '{val}'\n", "erro")
        self.has_error = True

    def consumir(self, tipo: str, val: str=None):
        tok, valor, _, _ = self.token_atual()
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
            if node:
                stmts.append(node)
        return Program(stmts)

    def parse_stmt(self):
        tok = self.token_atual()[0]
        if tok == 'VARIAVEL':           return self.parse_var_decl()
        if tok == 'ID' and self.peek()[0]=='ATRIBUICAO':   return self.parse_assign()
        if tok == 'ID' and self.peek()[0]=='DELIM' and self.peek()[1]=='(':  return self.parse_call_stmt()
        if tok == 'QUADRO':             return self.parse_print()
        if tok == 'FUNCAO':             return self.parse_func_decl()
        if tok == 'RETORNO':            return self.parse_return()
        if tok == 'LOOP_WHILE':         return self.parse_while()

        # inesperado
        self.erro("Erro sintático: statement inesperado", self.token_atual())
        self.pos += 1
        return None

    def parse_var_decl(self):
        self.consumir('VARIAVEL')
        if self.token_atual()[0]=='ID':
            name = self.token_atual()[1]; self.consumir('ID')
        else:
            self.erro("Erro sintático: esperado identificador", self.token_atual()); name="<erro>"
        self.consumir('ATRIBUICAO')
        expr = self.parse_expr()
        if self.token_atual()[0]=='DELIM' and self.token_atual()[1]==';':
            self.consumir('DELIM',';')
        else:
            self.erro("Erro sintático: esperado ';' ao final da declaração", self.token_atual())
        return VarDecl(name, expr)

    def parse_assign(self):
        name = self.token_atual()[1]; self.consumir('ID')
        self.consumir('ATRIBUICAO')
        expr = self.parse_expr()
        if self.token_atual()[0]=='DELIM' and self.token_atual()[1]==';':
            self.consumir('DELIM',';')
        else:
            self.erro("Erro sintático: esperado ';' ao final da atribuição", self.token_atual())
        return Assign(name, expr)

    def parse_call_stmt(self):
        call = self.parse_call_expr()
        if self.token_atual()[0]=='DELIM' and self.token_atual()[1]==';':
            self.consumir('DELIM',';')
        else:
            self.erro("Erro sintático: esperado ';' após chamada", self.token_atual())
        return call

    def parse_print(self):
        self.consumir('QUADRO'); self.consumir('DELIM','(')
        args = [ self.parse_expr() ]
        while self.token_atual()[0]=='DELIM' and self.token_atual()[1]==',':
            self.consumir('DELIM',','); args.append(self.parse_expr())
        self.consumir('DELIM',')'); self.consumir('DELIM',';')
        return Print(args)

    def parse_func_decl(self):
        self.consumir('FUNCAO')
        if self.token_atual()[0]=='ID':
            name=self.token_atual()[1]; self.consumir('ID')
        else:
            self.erro("Erro sintático: esperado nome de função", self.token_atual()); name="<erro>"
        self.consumir('DELIM','(')
        # parâmetros
        params=[]
        while self.token_atual()[0]=='VARIAVEL':
            self.consumir('VARIAVEL')
            if self.token_atual()[0]=='ID':
                params.append(self.token_atual()[1]); self.consumir('ID')
            if self.token_atual()[0]=='DELIM' and self.token_atual()[1]==',':
                self.consumir('DELIM',',')
        self.consumir('DELIM',')')
        # corpo
        if not (self.token_atual()[0]=='DELIM' and self.token_atual()[1]=='{'):
            self.erro("Erro sintático: esperado '{' de abertura", self.token_atual())
        else:
            self.consumir('DELIM','{')
        body=[]
        # loop até achar '}' ou EOF
        while self.token_atual()[0] != 'EOF' and not (self.token_atual()[0]=='DELIM' and self.token_atual()[1]=='}'):
            stmt = self.parse_stmt()
            if stmt: body.append(stmt)
        if self.token_atual()[0]=='DELIM' and self.token_atual()[1]=='}':
            self.consumir('DELIM','}')
        else:
            self.erro("Erro sintático: esperado '}' de fechamento", self.token_atual())
        return FuncDecl(name, params, body)

    def parse_return(self):
        self.consumir('RETORNO')
        expr=self.parse_expr()
        if self.token_atual()[0]=='DELIM' and self.token_atual()[1]==';':
            self.consumir('DELIM',';')
        else:
            self.erro("Erro sintático: esperado ';' após 'fornalha'", self.token_atual())
        return Return(expr)

    def parse_while(self):
        self.consumir('LOOP_WHILE')      # 'redstone'
        self.consumir('DELIM','(')
        cond = self.parse_expr()
        self.consumir('DELIM',')')
        self.consumir('DELIM','{')
        body=[]
        # loop até achar '}' ou EOF
        while self.token_atual()[0] != 'EOF' and not (self.token_atual()[0]=='DELIM' and self.token_atual()[1]=='}'):
            stmt = self.parse_stmt()
            if stmt: body.append(stmt)
        if self.token_atual()[0]=='DELIM' and self.token_atual()[1]=='}':
            self.consumir('DELIM','}')
        else:
            self.erro("Erro sintático: esperado '}' de fechamento do loop", self.token_atual())
        return While(cond, body)

    def parse_expr(self):
        node = self.parse_term()
        # aritmética
        while self.token_atual()[0]=='OP_ARIT':
            op=self.token_atual()[1]; self.consumir('OP_ARIT')
            right=self.parse_term()
            node=BinOp(node,op,right)
        # relacional
        if self.token_atual()[0]=='OP_REL':
            op=self.token_atual()[1]; self.consumir('OP_REL')
            right=self.parse_term()
            node=BinOp(node,op,right)
        return node

    def parse_term(self):
        tok,val,_,_ = self.token_atual()
        # unary minus
        if tok=='OP_ARIT' and val=='-':
            self.consumir('OP_ARIT')
            nt,nv,_,_ = self.token_atual()
            if nt=='NUM':
                self.consumir('NUM')
                num = float(nv) if '.' in nv else int(nv)
                return Literal(-num)
            right=self.parse_term()
            return BinOp(Literal(0),'-',right)
        if tok=='NUM':
            self.consumir('NUM'); return Literal(float(val) if '.' in val else int(val))
        if tok=='STRING':
            self.consumir('STRING'); return Literal(val.strip('"'))
        if tok=='CHAR':
            self.consumir('CHAR'); return Literal(val.strip("'"))
        if tok=='ID' and self.peek()[0]=='DELIM' and self.peek()[1]=='(':
            return self.parse_call_expr()
        if tok=='ID':
            self.consumir('ID'); return Var(val)
        if tok=='DELIM' and val=='(':
            self.consumir('DELIM','(')
            node=self.parse_expr()
            self.consumir('DELIM',')')
            return node
        # termo inválido
        self.erro("Erro sintático: termo inválido", self.token_atual())
        self.pos+=1
        return Literal(None)

    def parse_call_expr(self):
        name=self.token_atual()[1]; self.consumir('ID')
        self.consumir('DELIM','(')
        args=[]
        if not (self.token_atual()[0]=='DELIM' and self.token_atual()[1]==')'):
            args.append(self.parse_expr())
            while self.token_atual()[0]=='DELIM' and self.token_atual()[1]==',':
                self.consumir('DELIM',','); args.append(self.parse_expr())
        self.consumir('DELIM',')')
        return Call(name,args)

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
            out=''.join(str(self.eval_expr(a)) for a in node.args)
            self.terminal.insert(tk.END, out+"\n")
        elif isinstance(node, FuncDecl):
            self.functions[node.name] = (node.params, node.body)
        elif isinstance(node, Return):
            self.symbols['__return__'] = self.eval_expr(node.expr)
        elif isinstance(node, Call):
            args=[self.eval_expr(a) for a in node.args]
            if node.name not in self.functions:
                self.erro(f"Erro semântico: função '{node.name}' não declarada", self.token_atual())
                return
            params,body=self.functions[node.name]
            old_sym,old_dec=dict(self.symbols),set(self.declared)
            for p,v in zip(params,args): self.declared.add(p); self.symbols[p]=v
            for s in body: self.execute(s)
            ret=self.symbols.get('__return__',None)
            self.symbols, self.declared = old_sym, old_dec
            return ret
        elif isinstance(node, While):
            while self.eval_expr(node.condition):
                for stmt in node.body: self.execute(stmt)

    def eval_expr(self, node: ASTNode):
        if isinstance(node, Literal): return node.value
        if isinstance(node, Var):     return self.symbols.get(node.name,None)
        if isinstance(node, BinOp):
            l=self.eval_expr(node.left); r=self.eval_expr(node.right)
            if node.op in ('+','-','*','/'):
                return {'+':l+r,'-':l-r,'*':l*r,'/':l/r}[node.op]
            return {'==':l==r,'!=':l!=r,'>':l>r,'<':l<r,'>=':l>=r,'<=':l<=r}[node.op]
        if isinstance(node, Call):
            return self.execute(node)
        return None

    # ---- Impressão da AST ----
    def print_tree(self, node=None, indent=0):
        if node is None:
            self.pos=0
            node=self.parse()
        pad='  '*indent
        t=type(node).__name__
        info=getattr(node,'name',getattr(node,'value',''))
        self.terminal.insert(tk.END, f"{pad}{t}" + (f": {info}" if info else "") + "\n")
        for fld in ('statements','body','args','expr','left','right'):
            val=getattr(node,fld,None)
            if isinstance(val,list):
                for c in val: self.print_tree(c,indent+1)
            elif isinstance(val,ASTNode):
                self.print_tree(val,indent+1)
