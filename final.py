############################################################
# Final Project
#
# Team members: James Jang and Sidd Singal
#
# Emails: Byumho.Jang@students.olin.edu and siddharth.singal@students.olin.edu
#
# Remarks: Transcripts in the email
#


import sys

#
# Expressions
#

class Exp (object):
    pass


class EValue (Exp):
    # Value literal (could presumably replace EInteger and EBoolean)
    def __init__ (self,v):
        self._value = v
    
    def __str__ (self):
        return "EValue({})".format(self._value)

    def eval (self,env):
        return self._value

    
class EPrimCall (Exp):
    # Call an underlying Python primitive, passing in Values
    #
    # simplifying the prim call
    # it takes an explicit function as first argument

    def __init__ (self,prim,es):
        self._prim = prim
        self._exps = es

    def __str__ (self):
        return "EPrimCall(<prim>,[{}])".format(",".join([ str(e) for e in self._exps]))

    def eval (self,env):
        vs = [ e.eval(env) for e in self._exps ]
        return apply(self._prim,vs)


class EIf (Exp):
    # Conditional expression

    def __init__ (self,e1,e2,e3):
        print e1
        self._cond = e1
        self._then = e2
        self._else = e3

    def __str__ (self):
        return "EIf({},{},{})".format(self._cond,self._then,self._else)

    def eval (self,env):
        v = self._cond.eval(env)
        if v.type != "boolean":
            raise Exception ("Runtime error: condition not a Boolean")
        if v.value:
            return self._then.eval(env)
        else:
            return self._else.eval(env)


class ELet (Exp):
    # local binding
    # allow multiple bindings
    # eager (call-by-avlue)

    def __init__ (self,bindings,e2):
        self._bindings = bindings
        self._e2 = e2

    def __str__ (self):
        return "ELet([{}],{})".format(",".join([ "({},{})".format(id,str(exp)) for (id,exp) in self._bindings ]),self._e2)

    def eval (self,env):
        new_env = [ (id,e.eval(env)) for (id,e) in self._bindings] + env
        return self._e2.eval(new_env)

class EId (Exp):
    # identifier

    def __init__ (self,id):
        self._id = id

    def __str__ (self):
        return "EId({})".format(self._id)

    def eval (self,env):
        for (id,v) in env:
            if self._id == id:
                return v
        raise Exception("Runtime error: unknown identifier {}".format(self._id))


class ECall (Exp):
    # Call a defined function in the function dictionary

    def __init__ (self,fun,exps):
        self._fun = fun
        self._args = exps

    def __str__ (self):
        return "ECall({},[{}])".format(str(self._fun),",".join(str(e) for e in self._args))

    def eval (self,env):
        f = self._fun.eval(env)
        if f.type != "function":
            raise Exception("Runtime error: trying to call a non-function")
        args = [ e.eval(env) for e in self._args]
        if len(args) != len(f.params):
            raise Exception("Runtime error: argument # mismatch in call")
        new_env = zip(f.params,args) + f.env
        return f.body.eval(new_env)

class EProcCall (Exp):
    # Call a defined function in the function dictionary

    def __init__ (self,fun,exps):
        self._fun = fun
        self._args = exps

    def __str__ (self):
        return "EProcCall({},[{}])".format(str(self._fun),",".join(str(e) for e in self._args))

    def eval (self,env):
        f = self._fun.eval(env)
        if f.type != "procedure":
            raise Exception("Runtime error: trying to call a non-function")
        args = [ e.eval(env) for e in self._args]
        if len(args) != len(f.params):
            raise Exception("Runtime error: argument # mismatch in call")
        new_env = zip(f.params,args) + f.env
        f.body.eval(new_env)
        return VNone()




class EFunction (Exp):
    # Creates an anonymous function

    def __init__ (self,params,body):
        self._params = params
        self._body = body

    def __str__ (self):
        return "EFunction([{}],{})".format(",".join(self._params),str(self._body))

    def eval (self,env):
        return VClosure(self._params,self._body,env)


class ERefCell (Exp):
    # this could (should) be turned into a primitive
    # operation.  (WHY?)

    def __init__ (self,initialExp):
        self._initial = initialExp

    def __str__ (self):
        return "ERefCell({})".format(str(self._initial))

    def eval (self,env):
        v = self._initial.eval(env)
        return VRefCell(v)

class EDo (Exp):

    def __init__ (self,exps):
        self._exps = exps

    def __str__ (self):
        return "EDo([{}])".format(",".join(str(e) for e in self._exps))

    def eval (self,env):
        # default return value for do when no arguments
        v = VNone()
        for e in self._exps:
            v = e.eval(env)
        return v

class EWhile (Exp):

    def __init__ (self,cond,exp):
        self._cond = cond
        self._exp = exp

    def __str__ (self):
        return "EWhile({},{})".format(str(self._cond),str(self._exp))

    def eval (self,env):
        c = self._cond.eval(env)
        if c.type != "boolean":
            raise Exception ("Runtime error: while condition not a Boolean")
        while c.value:
            self._exp.eval(env)
            c = self._cond.eval(env)
            if c.type != "boolean":
                raise Exception ("Runtime error: while condition not a Boolean")
        return VNone()

class EProcedure (Exp):
    # Creates an anonymous function

    def __init__ (self,params,body):
        self._params = params
        self._body = body

    def __str__ (self):
        return "EProcedure([{}],{})".format(",".join(self._params),str(self._body))

    def eval (self,env):
        return VProcedure(self._params,self._body,env)

class EWithArray (Exp):
    def __init__ (self,exp1,exp2):
        self._record = exp1
        self._exp = exp2
        
    def __str__ (self):
        return "EWithArray({},{})".format(str(self._record),str(self._exp))

    def eval (self,env):
        records = self._record.eval(env)[1]
        return self._exp.eval(records+env)

class EArray (Exp):
    
    def __init__ (self,v):
        self._value = [ VNone()]
        self._index = v


    def __str__ (self):
        return "EArray({},{})".format(str(self._value),str(self._index))

    def eval (self,env):
        i = self._index.eval(env)
        self._value = self._value * i.value
        bind = [
        ("index", 
            VRefCell(VClosure(["x"],
                                  EPrimCall(self.index,[EId("x")]),
                                  env))),
        ("length", 
            VRefCell(VClosure([],
                                  EPrimCall(self.length, []),
                                  env))),
        ("map", 
            VRefCell(VClosure(["x"],
                                  EPrimCall(self.mapA,[EId("x")]),
                                  env)))
        ]
        return self._value, bind


    def index(self,i):
        return self._value[i.value]

    def length(self):
        return VInteger(len(self._value))
    
    def mapA(self,f):
        return map(f, self._value) 
    

    
#
# Values
#

class Value (object):
    pass


class VInteger (Value):
    # Value representation of integers
    
    def __init__ (self,i):
        self.value = i
        self.type = "integer"

    def __str__ (self):
        return str(self.value)

    
class VBoolean (Value):
    # Value representation of Booleans
    
    def __init__ (self,b):
        self.value = b
        self.type = "boolean"

    def __str__ (self):
        return "true" if self.value else "false"

    
class VClosure (Value):
    
    def __init__ (self,params,body,env):
        self.params = params
        self.body = body
        self.env = env
        self.type = "function"

    def __str__ (self):
        return "<function [{}] {}>".format(",".join(self.params),str(self.body))

    
class VRefCell (Value):

    def __init__ (self,initial):
        self.content = initial
        self.type = "ref"

    def __str__ (self):
        return "<ref {}>".format(str(self.content))


class VNone (Value):

    def __init__ (self):
        self.type = "none"

    def __str__ (self):
        return "none"

class VString (Value):
    # Value representation of integers
    
    def __init__ (self,i):
        self.value = i
        self.type = "string"

    def __str__ (self):
        return str(self.value)

class VArray (Value):
    def __init__ (self):
        self.value = [ VNone() ]
        self.type = "array"

    def __str__ (self):
        return str(self.value)

class VProcedure (Value):

    def __init__(self,params,body,env):
        self.params = params
        self.body = body
        self.env = env
        self.type = "procedure"

    def __str__(self):
        return "<procedure [{}] {}>".format(",".join(self.params),str(self.body))


###############################################
###############################################
## MOST OF INHERITANCE AND POLYMORPHISM CODE ##
###############################################
###############################################

class ENotImplemented (Exp):

    def eval(self,env):
        return VNotImplemented()

class VNotImplemented (Value):

    def __init__(self):
        self.type = "notimplemented"

    def __str__(self):
        return "<function not implemented>"

class ETemplate(Value):

    def __init__ (self, isAbstract, name, superclass, params, superargs, functions):

        self._isAbstract = isAbstract
        self._name = name
        self._superclass = superclass
        self._defEnv = []
        self._params = [param for param in params]
        self._superargs = [superarg for superarg in superargs]
        self._functions = functions

    def eval(self,env):
        scv = self._superclass.eval(env)
        fullname = self._name + "." + scv._fullname
        fullparams = [self._params] + scv._params
        superargs = [self._superargs] + scv._superargs

        for envElem in scv._defEnv:
            self._defEnv.insert(0,envElem)

        self._defEnv = scv._defEnv[:]

        for function in self._functions:
            # print(function[1].eval(env).type)
            # if ((not self._isAbstract) and (function[1].eval(env).type == "notimplemented")):
            #     raise Exception("Runtime error: Cannot create a concrete class with an abstract method")
            self._defEnv.insert(0,(function[0],VRefCell(function[1].eval(env))))

        names = set()
        if(not self._isAbstract):
            for (name,envElem) in self._defEnv:
                if(not name in names):
                    if envElem.content.type  == "notimplemented":
                        raise Exception("Runtime error: Cannot create a concrete class with an abstract method")
                    else:
                        names.add(name)

        return VTemplate(self._isAbstract,self._name,fullname,fullparams,superargs,self._defEnv)

class VTemplate(Value):

    def __init__(self,isAbstract,name,fullname,params,superargs,defEnv):
        self.type = "template"
        self._isAbstract = isAbstract
        self._name = name
        self._fullname = fullname
        self._params = params
        self._superargs = superargs
        self._defEnv = defEnv

    def __str__(self):
        return "<template {}>".format(self._fullname)

class EObject(Exp):

    def __init__(self,classid,args):
        self._class = classid
        self._args = args

    def eval(self,env):
        classtemp = self._class.eval(env)
        if classtemp.type != "template":
            raise Exception("Runtime error: {} not defined as a template".format(self._class))
        if classtemp._isAbstract:
            raise Exception("Runtime error: Cannot instantiate an abstract class")
        if len(classtemp._params[0])!=len(self._args):
            raise Exception("Runtime error: Must supply the following arguments".format(len(classtemp._params)))

        newEnv = classtemp._defEnv
        for i in range(len(self._args)):
            newEnv.insert(0,(classtemp._params[0][i],VRefCell(self._args[i].eval(env))))

        params = classtemp._params[1:-1]
        superargs = classtemp._superargs[:-1]

        for app in zip(params,superargs):
            for i in range(len(app[0])):
                newEnv.insert(0,(app[0][i],VRefCell(app[1][i].eval(newEnv))))

        return VObject(classtemp,newEnv)
        
class VObject(Value):

    def __init__(self,classt,env):
        self._class = classt
        self._env = env

    def __str__(self):
        return "<object of type {}>".format(self._class._fullname)

class EObjectBinding(Exp):

    def __init__(self,template,obj):
        self._template = template
        self._object = obj

    def eval(self,env):
        objectv = self._object.eval(env)
        templatev = self._template.eval(env)

        if(not (objectv._class._fullname.endswith(templatev._fullname))):
            raise Exception("Runtime error Cannot instantiate because {} is not of type {}".format(objectv._class._fullname,templatev._fullname))
        return VObjectBinding(templatev,objectv)

class VObjectBinding(Value):

    def __init__(self,temp,obj):
        self._template = temp
        self._object = obj

    def __str__(self):
        return "<object binding {} {}>".format(self._template,self._object)

class EWith(Value):

    def __init__(self,obj,function,args):
        self._object = obj
        self._function = function
        self._args = args

    def eval(self,env):
        objectv = self._object.eval(env)._object
        templatev = self._object.eval(env)._template
        try:
            self._function.eval(templatev._defEnv)
        except Exception as e:
            raise Exception("Runtime error: this function is not accessible or does not exist.")

        functionv = self._function.eval(objectv._env)
        args = [ e.eval(env) for e in self._args]
        newEnv = zip(functionv.params,args) + objectv._env
        functionv.body.eval(newEnv)
        return VNone()

###############################################
###############################################


# Primitive operations

def oper_lt (v1, v2):
  if v1.type == "integer" and v2.type == "integer":
        return VBoolean(v1.value < v2.value)
  raise Exception ("Runtime error: trying to compare non-numbers")
  
def oper_gt (v1, v2):
  if v1.type == "integer" and v2.type == "integer":
        return VBoolean(v1.value > v2.value)
  raise Exception ("Runtime error: trying to compare non-numbers")
  
def oper_le (v1, v2):
  if v1.type == "integer" and v2.type == "integer":
        return VBoolean(v1.value <= v2.value)
  raise Exception ("Runtime error: trying to compare non-numbers")
  
def oper_ge (v1, v2):
  if v1.type == "integer" and v2.type == "integer":
        return VBoolean(v1.value >= v2.value)
  raise Exception ("Runtime error: trying to compare non-numbers")

def oper_eq (v1, v2):
  if v1.type == "integer" and v2.type == "integer":
        return VBoolean(v1.value == v2.value)
  raise Exception ("Runtime error: trying to compare non-numbers")

def oper_plus (v1,v2): 
    if v1.type == "integer" and v2.type == "integer":
        return VInteger(v1.value + v2.value)
    raise Exception ("Runtime error: trying to add non-numbers")

def oper_minus (v1,v2):
    if v1.type == "integer" and v2.type == "integer":
        return VInteger(v1.value - v2.value)
    raise Exception ("Runtime error: trying to subtract non-numbers")

def oper_times (v1,v2):
    if v1.type == "integer" and v2.type == "integer":
        return VInteger(v1.value * v2.value)
    raise Exception ("Runtime error: trying to multiply non-numbers")

def oper_divide_i (v1,v2):
    if v1.type == "integer" and v2.type == "integer":
        return VInteger(int(v1.value / v2.value))
    raise Exception ("Runtime error: trying to divide non-numbers")

def oper_zero (v1):
    if v1.type == "integer":
        return VBoolean(v1.value==0)
    raise Exception ("Runtime error: type error in zero?")

def oper_length(v1): # (returns the length of a string)
    if v1.type == "string":
        return VInteger(len(v1.value))
    raise Exception ("Runtime error: not a string")

def oper_substring(v1,v2,v3): # (returns part of a string as a new string)
    if v1.type == "string" and v2.type == "integer" and v3.type == "integer":
        return VString(v1.value[v2.value:v3.value])
    raise Exception ("Runtime error: not a string")

def oper_concat(v1,v2): # (concatenate two strings into a new one)
    if v1.type == "string" and v2.type == "string":
        return VString(v1.value + v2.value)
    raise Exception ("Runtime error: not a string")

def oper_startswith(v1,v2): # (check if a string starts with another string)
    if v1.type == "string" and v2.type == "string":
        return VBoolean(v1.value.startswith(v2.value))
    raise Exception ("Runtime error: not a string")

def oper_endswith(v1,v2): # (check if a string ends with another string)
    if v1.type == "string" and v2.type == "string":
        return VBoolean(v1.value.endswith(v2.value))
    raise Exception ("Runtime error: not a string")

def oper_lower(v1): # (converts every character of a string into lowercase, returning a new string)
    if v1.type == "string":
        return VString(v1.value.lower())
    raise Exception ("Runtime error: not a string")

def oper_upper(v1): # (converts every character of a string into uppercase, returning a new string).
    if v1.type == "string":
        return VString(v1.value.upper())
    raise Exception ("Runtime error: not a string")

def oper_deref (v1):
    if v1.type == "ref":
        return v1.content
    raise Exception ("Runtime error: dereferencing a non-reference value")

def oper_update (v1,v2):
    if v1.type == "ref":
        v1.content = v2
        return VNone()
    raise Exception ("Runtime error: updating a non-reference value")

def oper_update_arr (v1,v2,v3):
    if v1.type == "ref":
        v1.content[0][v3.value] = v2
        return VNone()
    raise Exception ("Runtime error: updating a non-reference value")
 
def oper_print (v1):
    print v1
    return VNone()

    
############################################################
# IMPERATIVE SURFACE SYNTAX
#



##
## PARSER
##
# cf http://pyparsing.wikispaces.com/

from pyparsing import Word, Literal, ZeroOrMore, OneOrMore, Keyword, Forward, alphas, alphanums, NoMatch, quotedString


def initial_env_imp ():
    # A sneaky way to allow functions to refer to functions that are not
    # yet defined at top level, or recursive functions
    env = []
    env.insert(0,
               ("+",
                VRefCell(VClosure(["x","y"],
                                  EPrimCall(oper_plus,[EId("x"),EId("y")]),
                                  env))))
    env.insert(0,
               ("-",
                VRefCell(VClosure(["x","y"],
                                  EPrimCall(oper_minus,[EId("x"),EId("y")]),
                                  env))))
    env.insert(0,
               ("*",
                VRefCell(VClosure(["x","y"],
                                  EPrimCall(oper_times,[EId("x"),EId("y")]),
                                  env))))
    env.insert(0,
               ("/",
                VRefCell(VClosure(["x","y"],
                                  EPrimCall(oper_divide_i,[EId("x"),EId("y")]),
                                  env))))
    env.insert(0,
               ("zero?",
                VRefCell(VClosure(["x"],
                                  EPrimCall(oper_zero,[EId("x")]),
                                  env))))
    env.insert(0,
               ("<",
                VRefCell(VClosure(["x","y"],
                                  EPrimCall(oper_lt,[EId("x"),EId("y")]),
                                  env))))
                                  
    env.insert(0,
               (">",
                VRefCell(VClosure(["x","y"],
                                  EPrimCall(oper_gt,[EId("x"),EId("y")]),
                                  env))))
                                  
    env.insert(0,
               ("<=",
                VRefCell(VClosure(["x","y"],
                                  EPrimCall(oper_le,[EId("x"),EId("y")]),
                                  env))))
                                  
    env.insert(0,
               (">=",
                VRefCell(VClosure(["x","y"],
                                  EPrimCall(oper_ge,[EId("x"),EId("y")]),
                                  env))))

    env.insert(0,
               ("==",
                VRefCell(VClosure(["x","y"],
                                  EPrimCall(oper_eq,[EId("x"),EId("y")]),
                                  env))))
    env.insert(0,
               ("length",
                VRefCell(VClosure(["x"],
                                  EPrimCall(oper_length,[EId("x")]),
                                  env))))
    env.insert(0,
               ("substring",
                VRefCell(VClosure(["x", "y", "z"],
                                  EPrimCall(oper_substring,[EId("x"),EId("y"),EId("z")]),
                                  env))))

    env.insert(0,
               ("concat",
                VRefCell(VClosure(["x", "y"],
                                  EPrimCall(oper_concat,[EId("x"),EId("y")]),
                                  env))))

    env.insert(0,
               ("startswith",
                VRefCell(VClosure(["x","y"],
                                  EPrimCall(oper_startswith,[EId("x"),EId("y")]),
                                  env))))

    env.insert(0,
               ("endswith",
                VRefCell(VClosure(["x","y"],
                                  EPrimCall(oper_endswith,[EId("x"),EId("y")]),
                                  env))))

    env.insert(0,
               ("lower",
                VRefCell(VClosure(["x"],
                                  EPrimCall(oper_lower,[EId("x")]),
                                  env))))
    env.insert(0,
               ("upper",
                VRefCell(VClosure(["x"],
                                  EPrimCall(oper_upper,[EId("x")]),
                                  env))))

    return env




def parse_imp (input):
    # parse a string into an element of the abstract representation

    # Grammar:
    #
    # <expr> ::= <integer>
    #            true
    #            false
    #            <identifier>
    #            ( if <expr> <expr> <expr> )
    #            ( function ( <name ... ) <expr> )    
    #            ( <expr> <expr> ... )
    #
    # <decl> ::= var name = expr ; 
    #
    # <stmt> ::= if <expr> <stmt> else <stmt>
    #            while <expr> <stmt>
    #            name <- <expr> ;
    #            print <expr> ;
    #            <block>
    #
    # <block> ::= { <decl> ... <stmt> ... }
    #
    # <toplevel> ::= <decl>
    #                <stmt>
    #


    idChars = alphas+"_+*-/?!=<>"

    pIDENTIFIER = Word(idChars, idChars+"0123456789")
    #### NOTE THE DIFFERENCE
    pIDENTIFIER.setParseAction(lambda result: EPrimCall(oper_deref,[EId(result[0])]))

    pIDENTIFIERS = ZeroOrMore(pIDENTIFIER)
    pIDENTIFIERS.setParseAction(lambda result: [result])

    # A name is like an identifier but it does not return an EId...
    pNAME = Word(idChars,idChars+"0123456789")

    pNAMES = ZeroOrMore(pNAME)
    pNAMES.setParseAction(lambda result: [result])

    pINTEGER = Word("0123456789")
    pINTEGER.setParseAction(lambda result: EValue(VInteger(int(result[0]))))

    pBOOLEAN = Keyword("true") | Keyword("false")
    pBOOLEAN.setParseAction(lambda result: EValue(VBoolean(result[0]=="true")))
    
    def escapeString(inStr):
        inStr = inStr[1:-1]
        outStr = ""
        i = 0
        while(i < len(inStr) - 1):
            if(inStr[i]=='\\'):
                if(inStr[i+1]=='\\' or inStr[i+1]=='\"'):
                    i+=1
            outStr+=inStr[i]
            i+=1
        outStr+=inStr[-1]
        return outStr
         
    pSTRING = quotedString.copy()
    pSTRING.setParseAction(lambda result: EValue(VString(escapeString(result[0]))))

    pEXPR = Forward()

    pEXPRS = ZeroOrMore(pEXPR)
    pEXPRS.setParseAction(lambda result: [result])

    pIF = "(" + Keyword("if") + pEXPR + pEXPR + pEXPR + ")"
    pIF.setParseAction(lambda result: EIf(result[2],result[3],result[4]))

    def mkFunBody (params,body):
        bindings = [ (p,ERefCell(EId(p))) for p in params ]
        return ELet(bindings,body)

    pFUN = "(" + Keyword("function") + "(" + pNAMES + ")" + pEXPR + ")"
    pFUN.setParseAction(lambda result: EFunction(result[3],mkFunBody(result[3],result[5])))

    pBINDING = "(" + pNAME + pEXPR + ")"
    pBINDING.setParseAction(lambda result: (result[1],result[2]))

    pBINDINGS = ZeroOrMore(pBINDING)
    pBINDINGS.setParseAction(lambda result: [ result ])

    pCALL = "(" + pEXPR + pEXPRS + ")"
    pCALL.setParseAction(lambda result: ECall(result[1],result[2]))

    pEXPR << (pINTEGER | pBOOLEAN | pSTRING | pIDENTIFIER | pIF | pFUN | pCALL)

    pDECL_VAR = "var" + pNAME + "=" + pEXPR + ";"
    pDECL_VAR.setParseAction(lambda result: (result[1],result[3]))    

    pDECL_ARRAY = "var" + pNAME + "<-" + "(" + "new-array" + pEXPR + ")" + ";"
    pDECL_ARRAY.setParseAction(lambda result: (result[1] , EArray(result[5])))

    # hack to get pDECL to match only PDECL_VAR (but still leave room
    # to add to pDECL later)
    pDECL = ( pDECL_VAR | pDECL_ARRAY | NoMatch() )

    pDECLS = ZeroOrMore(pDECL)
    pDECLS.setParseAction(lambda result: [result])

    

    pSTMT = Forward()

    pSTMT_IF_1 = "if" + pEXPR + pSTMT + "else" + pSTMT
    pSTMT_IF_1.setParseAction(lambda result: EIf(result[1],result[2],result[4]))

    pSTMT_IF_2 = "if" + pEXPR + pSTMT
    pSTMT_IF_2.setParseAction(lambda result: EIf(result[1],result[2],EValue(VBoolean(True))))
   
    pSTMT_WHILE = "while" + pEXPR + pSTMT
    pSTMT_WHILE.setParseAction(lambda result: EWhile(result[1],result[2]))

    pSTMT_PRINT = "print" + pEXPR + ";"
    pSTMT_PRINT.setParseAction(lambda result: EPrimCall(oper_print,[result[1]]));

    pSTMT_UPDATE = pNAME + "<-" + pEXPR + ";"
    pSTMT_UPDATE.setParseAction(lambda result: EPrimCall(oper_update,[EId(result[0]),result[2]]))

    pSTMTARR_UPDATE = pNAME + "[" + pEXPR + "]" + "<-" + pEXPR + ";"
    pSTMTARR_UPDATE.setParseAction(lambda result: EPrimCall(oper_update_arr,[EId(result[0]),result[5], result[2]]))

    # pSTMT_FOR = "for" + "(" + pSTMT_UPDATE + pEXPR + ";" + pSTMT_UPDATE + ")" + pSTMT
    # pSTMT_FOR.setParseAction(lambda result: EDo([result[2],EWhile(result[3], EDo([result[7],result[5]])) ] ))

    pSTMT_FOR = "for" + pSTMT_UPDATE + pEXPR + ";" + pSTMT_UPDATE + pSTMT
    pSTMT_FOR.setParseAction(lambda result: EDo([result[1],EWhile(result[2], EDo([result[5],result[4]])) ] ))

    pSTMTS = ZeroOrMore(pSTMT)
    pSTMTS.setParseAction(lambda result: [result])

    def mkBlock (decls,stmts):
        bindings = [ (n,ERefCell(expr)) for (n,expr) in decls ]
        return ELet(bindings,EDo(stmts))
        
    pSTMT_BLOCK = "{" + pDECLS + pSTMTS + "}"
    pSTMT_BLOCK.setParseAction(lambda result: mkBlock(result[1],result[2]))

    pDEFPROC = "procedure" + pNAME + "(" + pNAMES + ")" + pSTMT
    pDEFPROC.setParseAction(lambda result: {"result":"procedure",
                                            "proc":(result[1],EProcedure(result[3],mkFunBody(result[3],result[5])))})

    pSTMT_PROC = pIDENTIFIER + "(" + pEXPRS + ")" + ";"
    pSTMT_PROC.setParseAction(lambda result: EProcCall(result[0],result[2]))

    pWITH = "(" + Keyword("with") + pIDENTIFIER + pIDENTIFIER + "(" + pEXPRS +")" + ")"
    pWITH.setParseAction(lambda result: EWith(result[2],result[3],result[5]))

    pNOTIMPLEMENTED = Keyword("<>")
    pNOTIMPLEMENTED.setParseAction(lambda result: ENotImplemented())

    pSTMT << ( pSTMT_IF_1 | pSTMT_IF_2 | pSTMT_WHILE | pSTMT_PRINT | pSTMT_FOR | pSTMT_UPDATE | pSTMTARR_UPDATE | pSTMT_BLOCK | pSTMT_PROC | pWITH)

    # can't attach a parse action to pSTMT because of recursion, so let's duplicate the parser
    pTOP_STMT = pSTMT.copy()
    pTOP_STMT.setParseAction(lambda result: {"result":"statement",
                                             "stmt":result[0]})

    pTOP_DECL = pDECL.copy()
    pTOP_DECL.setParseAction(lambda result: {"result":"declaration",
                                             "decl":result[0]})

    pABSTRACT = "#abs" + pSTMT
    pABSTRACT.setParseAction(lambda result: {"result":"abstract",
                                             "stmt":result[1]})

    pQUIT = Keyword("#quit")
    pQUIT.setParseAction(lambda result: {"result":"quit"})

    pDEFFUN = "(" + pNAME + "(" + pNAMES + ")" + pSTMT + ")"
    pDEFFUN.setParseAction(lambda result: (result[1], EProcedure(result[3],mkFunBody(result[3],result[5])) ))

    pDEFABSFUN = "(" + pNAME + "(" + pNAMES + ")" + pNOTIMPLEMENTED + ")"
    pDEFABSFUN.setParseAction(lambda result: (result[1], ENotImplemented()))

    pDEFFUNS = ZeroOrMore((pDEFFUN | pDEFABSFUN))
    pDEFFUNS.setParseAction(lambda result: [result])

    pTEMPLATE = Keyword("class") + "(" + pNAME + pIDENTIFIER + "(" + pNAMES + ")" + "(" + pIDENTIFIERS + ")" + "(" + pDEFFUNS + ")" + ")"
    pTEMPLATE.setParseAction(lambda result: {"result":"template",
                                             "temp":(result[2],ETemplate(False, result[2], result[3], result[5], result[8], result[11]))})

    pABSTEMPLATE = Keyword("absclass") + "(" + pNAME + pIDENTIFIER + "(" + pNAMES + ")" + "(" + pIDENTIFIERS + ")" + "(" + pDEFFUNS + ")" + ")"
    pABSTEMPLATE.setParseAction(lambda result: {"result":"template",
                                             "temp":(result[2],ETemplate(True, result[2], result[3], result[5], result[8], result[11]))})

    pNEWOBJ = Keyword("new") + pIDENTIFIER + "(" + pEXPRS + ")"
    pNEWOBJ.setParseAction(lambda result: EObject(result[1],result[3]))

    pOBJASS = Keyword("obj") + pIDENTIFIER + pNAME + "=" + pNEWOBJ
    pOBJASS.setParseAction(lambda result: {"result":"objectassignment",
                                            "assignment":(result[2],EObjectBinding(result[1],result[4]))})

    pMULTI = Keyword("#multi")
    pMULTI.setParseAction(lambda result: {"result":"multi"})

    pTOP = (pQUIT | pABSTRACT | pTOP_DECL | pTOP_STMT | pDEFPROC | pTEMPLATE | pOBJASS | pMULTI | pABSTEMPLATE)

    result = pTOP.parseString(input)[0]
    return result    # the first element of the result is the expression


def shell_imp ():
    # A simple shell
    # Repeatedly read a line of input, parse it, and evaluate the result

    print "Inheritance and Polymorphism"
    print "#quit to quit, #abs to see abstract representation"
    env = initial_env_imp()
    env.insert(0,
                ("Object",
                VRefCell(VTemplate(
                    False,"Object","Object",[[]],[],initial_env_imp()))))
    multi = False

        
    while True:
        if not multi:
            inp = raw_input("imp> ")

        multi = False

        try:
            result = parse_imp(inp) 

            if result["result"] == "statement":
                stmt = result["stmt"]
                # print "Abstract representation:", exp
                v = stmt.eval(env)

            elif result["result"] == "abstract":
                print result["stmt"]

            elif result["result"] == "quit":
                return

            elif result["result"] == "declaration":
                (name,expr) = result["decl"]
                v = expr.eval(env)
                env.insert(0,(name,VRefCell(v)))
                print "{} defined".format(name)

            elif result["result"] == "procedure":
                (name,proc) = result["proc"]
                v = proc.eval(env)
                env.insert(0,(name,VRefCell(v)))
                print "{} defined".format(name)

            elif result["result"] == "template":
                (name,temp) = result["temp"]
                v = temp.eval(env)
                env.insert(0,(name,VRefCell(v)))
                print "{} defined".format(v._fullname)

            elif result["result"] == "objectassignment":
                (name,ass) = result["assignment"]
                v = ass.eval(env)
                env.insert(0,(name,VRefCell(v)))
                print "{} of type {} got assigned a {} object".format(name,v._template._fullname,v._object._class._fullname)

            elif result["result"] == "multi":
                multi = True
                inp = ""
                nextLine = raw_input("| ")
                while(not (nextLine == "#end")):
                    inp += nextLine
                    nextLine = raw_input("| ")
                
                
        except Exception as e:
            print "Exception: {}".format(e)