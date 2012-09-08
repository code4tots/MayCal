'''
<-------------- imports and helpful global vars ------------------------------->
'''
from itertools import takewhile, dropwhile
alnum_ = '1234567890_abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'


'''
<-------------- Lexer and other parser helpers -------------------------------->
'''
def isIdentifier(strg):
    for c in strg:
        if c not in alnum_: return False
    return True

def lex(strg):
    return (strg.replace('(', ' ( ').
                 replace(')', ' ) ').
                 replace(',', ' , ').
                 replace('\\', ' \\ ').
                 split())
                
'''
<-------------- Parser methods ------------------------------------------------>
'''
def parse(tokens):
    tokens = parseParenthesis(tokens)
    tokens = parseLambdaExpr(tokens)
    tokens = parseIfExpr(tokens)
    tokens = parseBinop(tokens, {':': 'cons'}, isLeftAssociative = False)
    tokens = parseBinop(tokens, {'^': 'exponent'}, isLeftAssociative = False)
    tokens = parseBinop(tokens, {'*': 'multiply', '/': 'divide'})
    tokens = parseBinop(tokens, {'+': 'add', '-': 'subtract'})
    tokens = parseBinop(tokens, {'%': 'modulo'})
    tokens = parseBinop(tokens, {'=': 'equals', '<': 'lessThan', '>': 'greaterThan'})
    # if len(tokens) != 1, then parse isn't complete yet
    return tokens[0]
    
    
def parseParenthesis(tokens):
    
    while '(' in tokens:
        # Find the first inner most parenthesis
        b = 0
        while tokens[b] != ')': b += 1
    
        a = b-1
        while tokens[a] != '(': a -= 1
        
        if a > 0 and (isinstance(tokens[a-1],list) or isIdentifier(tokens[a-1])):
            # If the left parenthesis is directly preceded by
            # a list or string, this is a function call
            fn = tokens[a-1]
            args = []
            
            notComma = lambda x: x != ','
            buffer = tokens[a:b] # ( ... , ... , (no end parenthesis)
            while len(buffer) > 0:
                buffer = buffer[1:] # remove either ( or comma
                args.append(parse(list(takewhile(notComma, buffer))))
                buffer = list(dropwhile(notComma, buffer))
                
            tokens = tokens[:a-1] + [ [fn] + args ] + tokens[b+1:]
        else:
            # Otherwise, the parenthesis was just for grouping
            tokens = tokens[:a] + [ parse(tokens[a+1:b]) ] + tokens[b+1:]
            
    return tokens
    
def parseLambdaExpr(tokens):
    while '\\' in tokens:
        a = 0
        while tokens[a] != '\\': a += 1
        
        b = a + 1
        while tokens[b] != '->': b += 1
        
        argNames = tokens[a+1:b]
        expr = parse(tokens[b+1:])
        
        tokens = tokens[:a] + [ ['lambda', argNames, expr] ]
    return tokens
        
        
def parseIfExpr(tokens):
    while 'if' in tokens:
        # Randomly pick an 'if', 'then', 'else', that will work.
        # As a result it will be bad practice to nest if statements without parenthesis
        a = 0
        while tokens[a] != 'if': a += 1
        
        b = a + 1
        while tokens[b] != 'else': b += 1
        
        tokens = [ ['if_function', parse(tokens[a+1:b]), parse(tokens[:a]), parse(tokens[b+1:]) ] ]
        
    return tokens
    
    
def parseBinop(tokens, operators, isLeftAssociative = True):
    def containsOperator(tokens):
        for token in tokens:
            if isinstance(token,str) and token in operators: return True
        return False
        
    while containsOperator(tokens):
        i = 1 if isLeftAssociative else len(tokens) - 2
        
        if isLeftAssociative:
            while (not isinstance(tokens[i],str)) or tokens[i] not in operators: i += 1
        else:
            while (not isinstance(tokens[i],str)) or tokens[i] not in operators: i -= 1
            
        tokens = tokens[:i-1] + [ [operators[tokens[i]], tokens[i-1], tokens[i+1]] ] + tokens[i+2:]
        
    return tokens
        
'''
<-------------- Built-in functions -------------------------------------------->
'''

def MayCalcFunc(fn):
    def wrapper(ev, *args):
        return fn( *list(map(ev, args)) )
    return wrapper
    
@MayCalcFunc
def Add(a,b): return a + b

@MayCalcFunc
def Subtract(a,b): return a - b

@MayCalcFunc
def Multiply(a,b): return a * b

@MayCalcFunc
def Divide(a,b): return a / b

@MayCalcFunc
def Exponent(a,b): return a ** b

@MayCalcFunc
def Equals(a,b): return a == b

@MayCalcFunc
def LessThan(a,b): return a < b

@MayCalcFunc
def GreaterThan(a,b): return a > b

@MayCalcFunc
def Modulo(a,b): return a % b

@MayCalcFunc
def Cons(a,b): return [a] + b

@MayCalcFunc
def Car(a): return a[0]

@MayCalcFunc
def Cdr(a): return a[1:]

def If_function(ev, condition, a, b):
    if ev(condition): return ev(a)
    return ev(b)

def Lambda(ev, argNames, expr):
    def applyBindings(expr, bindings):
        if isinstance(expr,list):
            for i in range(len(expr)):
                if isinstance(expr[i],str) and expr[i] in bindings:
                    expr[i] = bindings[expr[i]]
                elif isinstance(expr[i], list):
                    applyBindings(expr[i],bindings)
    
    def copyListFunc(lis):
        copyList = lis[:]
        for i in range(len(lis)):
            if isinstance(copyList[i],list):
                copyList[i] = copyListFunc(copyList[i])
        return copyList

    @MayCalcFunc
    def wrapper(*args):
        bindings = {k:v for k,v in zip(argNames,args)}
        copyExpr = copyListFunc(expr) if isinstance(expr,list) else expr
        applyBindings(copyExpr, bindings)
        return ev(copyExpr)
    return wrapper

'''
<-------------- Evaluator stuff ----------------------------------------------->
'''

class Evaluator(object):
    def __init__(self, env):
        self.env = env
        
    def __call__(self, expr):
        ret = expr
        if isinstance(expr, list):
            ret = self(expr[0])(self, *expr[1:])
        elif isinstance(expr, str):
            try:        ret = int(expr)
            except:
                try:    ret = float(expr)
                except: ret = self.env[expr]
        return ret
    

class Environment(object):
    def __init__(self):
        self.base = {
            'True': True,
            'False': False,
            
            '[]': [],
            'nil': [],
            'cons': Cons,
            'car': Car,
            'cdr': Cdr,
        
            'add': Add,
            'subtract': Subtract,
            'multiply': Multiply,
            'divide': Divide,
            'exponent': Exponent,
            'equals': Equals,
            'lessThan': LessThan,
            'greaterThan': GreaterThan,
            'modulo': Modulo,
            'lambda': Lambda,
            'if_function': If_function,
        }
        
        self.env = {}
        
    def __getitem__(self, key):
        try:    return int(key)
        except:
            try:    return float(key)
            except: pass
        if key in self.env: return self.env[key]
        return self.base[key]
        
    def __setitem__(self, key, value):
        self.env[key] = value
        
    def clear(self):
        self.env = {}
    
    def infoStr(self, includeBase = False):
        ret = 'in user environment:\n'
        for key in self.env:
            ret += '%-10s : %s\n' % (key, self.env[key])
        if includeBase:
            ret += '\nin base environment:\n'
            for key in self.base:
                ret += '%-10s : %s\n' % (key, self.base[key])
        return ret

class Interpreter(object):
    def __init__(self):
        self.env = Environment()        
        self.ev = Evaluator(self.env)
        
    def __call__(self, strg):
        tokens = lex(strg)
        ret = None
        if tokens == ['who']:
            print(self.env.infoStr())
            
        elif tokens == ['whos']:
            print(self.env.infoStr(includeBase=True))
            
        elif tokens == ['clear']:
            self.env.clear()
            
        elif ':=' in tokens:
            # If '=' token is there, there's some sort of assignment
            notEq = lambda x : x != ':='
            
            var = parse(list(takewhile(notEq, tokens)))
            exprTokens = list(dropwhile(notEq,tokens))[1:]
            expr = parse(exprTokens)
            
            if isinstance(var,list):
                # If the lhs is a list, we're defining some sort of function.
                # This allows function shorthand
                self.env[var[0]] = self.ev( parse(['\\'] + var[1:] + ['->'] + exprTokens) )
            else:
                # Otherwise, we have normal assignment where we assign
                # a single value
                self.env[var] = self.ev(expr)
            
        else:
            ret = self.ev(parse(tokens))
            
        return ret
        
def main():
    i = Interpreter()
    try:
        inp = raw_input('>> ')
        while True:
            ret = i(inp)
            if ret != None: print(ret)
            inp = raw_input('>> ')
    except EOFError:
        pass
    print('')
        
if __name__ == '__main__': main()
