# lexico.py
import re

def lex(codigo: str):
    tabela_de_token = [
        ('COMENTARIO',   r'//[^\n]*|#[^\n]*'),
        ('VARIAVEL',     r'\bbau\b'),
        ('QUADRO',       r'\bquadro\b'),
        ('FUNCAO',       r'\bcraftar\b'),
        ('IF',           r'\bfunil\b'),
        ('ELSE',         r'\bejetor\b'),
        ('LOOP_WHILE',   r'\bredstone\b'),
        ('LOOP_FOR',     r'\btrilho\b'),
        ('RETORNO',      r'\bfornalha\b'),
        ('ATRIBUICAO',   r'='),
        ('OP_ARIT',      r'[+\-*/]'),
        ('OP_REL',       r'==|!=|>=|<=|>|<'),
        ('OP_LOGICO',    r'\b(e|ou|nao)\b'),
        ('DELIM',        r'[(){};,]'),
        ('NUM',          r'\d+(\.\d+)?'),
        ('STRING',       r'"[^"\n]*"'),
        ('CHAR',         r"'[^'\n]'"),
        ('ID',           r'[A-Za-z_][A-Za-z0-9_]*'),
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
