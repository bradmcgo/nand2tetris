import sys
import os
import re

class SymbolTable:
    def __init__(self):
        self.table = []
        self.staticIndex = 0
        self.fieldIndex = 0
        self.varIndex = 0
        self.argIndex = 0

    def add_row_class(self, name, type, kind, index):
        self.table.append({"name": name, "type": type, "kind": kind, "index": index})

    def reset(self):
        self.table = []
        self.staticIndex = 0
        self.fieldIndex = 0
        self.varIndex = 0
        self.argIndex = 0

    def define(self, name, type, kind):

        if kind == "static":
            self.add_row_class(name, type, kind, self.staticIndex)
            self.staticIndex += 1

        elif kind == "field":
            self.add_row_class(name, type, kind, self.fieldIndex)
            self.fieldIndex += 1
            
        elif kind == "var":
            self.add_row_class(name, type, kind, self.varIndex)
            self.varIndex += 1

        elif kind == "arg":
            self.add_row_class(name, type, kind, self.argIndex)
            self.argIndex += 1

        else:
            self.add_row_class(name, type, kind, self.argIndex)

    def varCount(self, kind):
        numberOfVars = sum(1 for row in self.table if row["kind"] == kind)
        return numberOfVars
    
    def kindOf(self, name):
        for row in self.table:
            if row["name"] == name:
                return row["kind"]
        return "NONE"

    def typeOf(self, name):
        for row in self.table:
            if row["name"] == name:
                return row["type"]

    def indexOf(self, name):
        for row in self.table:
            if row["name"] == name:
                return row["index"]
            

class JackTokenizer:
    def __init__(self, text):
        self.lines = text.split('\n')
        self.cleanLines = []
        for line in self.lines:
            self.cleanedLine = re.sub(r'//.*$', '', line)
            self.cleanLines.append(self.cleanedLine)

        cleanedText = '\n'.join(self.cleanLines)
        cleanedText = re.sub(r'/\*.*?\*/', '', cleanedText, flags=re.DOTALL)
        lexicalElements = ["class", "constructor", "function", "method", "field", "static", "var", "int", "char", "boolean", "void", "true", "false", "null", "this", "let", "do", "if", "else", "while", "return", "{", "}", "(", ")", "[", "]", ".", ",", ";", "+", "-", "*", "/", "&", "|", "<", ">", "=", "~"]
        
        self.lines = cleanedText.split()
        self.result = []
        inQuotes = False
        self.temp = ""

        for line in self.lines:
            for char in line:
                if char.isdigit():
                    self.temp += char
                else:
                    if self.temp and self.temp.isdigit():
                        if 0 <= int(self.temp) <= 32767:
                            self.result.append(self.temp)
                        else:
                            print("Integer is not between 0 and 32767.")
                        self.temp = ""
                    if char == '"':
                        if inQuotes:
                            self.temp += char
                            self.result.append(self.temp)
                            self.temp = ""
                            inQuotes = False
                        else:
                            if self.temp:
                                self.result.append(self.temp)
                                self.temp = ""
                            self.temp += char
                            inQuotes = True
                    elif inQuotes:
                        self.temp += char
                    elif char in lexicalElements:
                        if self.temp:
                            self.result.append(self.temp)
                            self.temp = ""
                        self.result.append(char)
                    elif char.isspace():
                        if self.temp:
                            self.result.append(self.temp)
                            self.temp = ""
                    else:
                        self.temp += char
            if self.temp and self.temp.isdigit():
                if 0 <= int(self.temp) <= 32767:
                    self.result.append(self.temp)
                else:
                    print("Integer is not between 0 and 32767.")
                self.temp = ""
            elif self.temp and not inQuotes:
                self.result.append(self.temp)
                self.temp = ""
            elif self.temp and inQuotes:
                self.temp += ' '
        
        self.current_token = -1
        self.current_instruction = ""
        self.instruction_type = ""
        self.the_symbol = ""


    def hasMoreTokens(self):
        if self.current_token < len(self.result) - 1:
            return True
        return False
    
    def advance(self):
        self.current_token += 1
        if self.hasMoreTokens():
            self.current_instruction = ""
            self.current_instruction = self.result[self.current_token]
        else:
            print("No more tokens.")
    
    def tokenType(self):
        keywords = ["class", "constructor", "function", "method", "field", "static", "var", "int", "char", "boolean", "void", "true", "false", "null", "this", "let", "do", "if", "else", "while", "return"]
        if any(self.current_instruction.startswith(keyword) for keyword in keywords):
            self.instruction_type = "KEYWORD"
            return "KEYWORD"
        symbols = ["{", "}", "(", ")", "[", "]", ".", ",", ";", "+", "-", "*", "/", "&", "|", "<", ">", "=", "~"]
        if any(self.current_instruction.startswith(symbol) for symbol in symbols):
            self.instruction_type = "SYMBOL"
            return "SYMBOL"
        if self.current_instruction.isdigit():
            decimal = int(self.current_instruction)
            if 0 <= decimal <= 32767:
                self.instruction_type = "INT_CONST"
                return "INT_CONST"
        if self.current_instruction.startswith('"'):
            self.instruction_type = "STRING_CONST"
            return "STRING_CONST"
        if not self.current_instruction.startswith('"'):
            if not self.current_instruction[0].isdigit():
                self.instruction_type = "IDENTIFIER"
                return "IDENTIFIER"                
            else:
                return "Not an identifier."
        
    def keyWord(self):
        self.current_instruction = self.current_instruction
        return self.current_instruction

    def symbol(self):
        if self.current_instruction == "<":
            return "&lt;"
        elif self.current_instruction == ">":
            return "&gt;"
        elif self.current_instruction == "&":
            return "&amp;"
        else:
            return self.current_instruction
        
    def identifier(self):
        return str(self.current_instruction)

    def intVal(self):
        return int(self.current_instruction)

    def stringVal(self):
        self.current_instruction = self.current_instruction.replace('"', '')
        return str(self.current_instruction)


class VMWriter:
    def __init__(self, outputFile):
        self.outputFile = outputFile

    def writePush(self, segment, index=None):
        if index is not None:
            self.outputFile.write(f"push {segment} {index}\n")
        else:
            self.outputFile.write(f"push {segment}\n")

    def writePop(self, segment, index):
        self.outputFile.write(f"pop {segment} {index}\n")

    def writeArithmetic(self, command):
        if command == "*":
            self.outputFile.write("call Math.multiply 2\n")
        elif command == "/":
            self.outputFile.write("call Math.divide 2\n")
        elif command == "+":
            self.outputFile.write("add\n")
        elif command == "-":
            self.outputFile.write("sub\n")
        elif command == "neg":
            self.outputFile.write("neg\n")
        elif command == "not":
            self.outputFile.write("not\n")
        elif command == "&gt;":
            self.outputFile.write("gt\n")
        elif command == "&lt;":
            self.outputFile.write("lt\n")
        elif command == "=":
            self.outputFile.write("eq\n")
        elif command == "&amp;":
            self.outputFile.write("and\n")
        elif command == "and":
            self.outputFile.write("and\n")
        elif command == "or":
            self.outputFile.write("or\n")
        elif command == "|":
            self.outputFile.write("or\n")   
        elif command == "&":
            self.outputFile.write("and\n")

    def writeLabel(self, label):
        self.outputFile.write(f"label {label}\n")

    def writeGoto(self, label):
        self.outputFile.write(f"goto {label}\n")

    def writeIf(self, label):
        self.outputFile.write(f"if-goto {label}\n")

    def writeCall(self, name, nArgs):
        self.outputFile.write(f"call {name} {nArgs}\n")

    def writeFunction(self, name, nVars):
        self.outputFile.write(f"function {name} {nVars}\n")

    def writeReturn(self):
        self.outputFile.write("return\n")

    def close(self):
        self.outputFile.close()



subTypeTable = []
def addSubType(type, name):
    subTypeTable.append({"name": name, "type": type})

def returnSubType(name):
    for row in subTypeTable:
        if row["name"] == name:
            return row["type"]


class CompilationEngine:
    def __init__(self, jackTokenizer, outputFile):
        self.jackTokenizer = jackTokenizer
        self.outputFile = outputFile
        self.filename = ""
        self.className = ""
        self.classSymbolTable = SymbolTable()
        self.subSymbolTable = SymbolTable()
        self.vmWriter = VMWriter(self.outputFile)
        self.current_name = ""
        self.current_type = ""
        self.current_kind = ""
        self.doClassMethod = []
        self.subCallFunction = False
        self.ExpressionListCounter = 0
        self.numOfArgs = 0
        self.argCounter = 1
        self.returnArray = []
        self.unaryOp = False
        self.label_counter = 0
        self.segment = ""
        self.index = ""
        self.andOr = False
        self.andOrSymbol = ""
        self.isArray = False
        self.thatFlag = False
        self.noClass = False
        self.negate = False
        self.letFlag = False
        self.jackTokenizer.advance()

    def _typeOfChar(self):
        if self.jackTokenizer.tokenType() == "KEYWORD":
            self.current_type = self.jackTokenizer.keyWord()
        if self.jackTokenizer.tokenType() == "IDENTIFIER":
            self.current_type = self.jackTokenizer.identifier()

    def _checkStar(self):
        while True:
            if self.jackTokenizer.symbol() == ",":
                self.jackTokenizer.advance()

                self.current_name = self.jackTokenizer.identifier()
                self.classSymbolTable.define(self.current_name, self.current_type, self.current_kind)

                self.jackTokenizer.advance()
            else:
                self.jackTokenizer.advance()
                break

    def _subCheckStar(self):
        while True:
            if self.jackTokenizer.symbol() == ",":
                self.jackTokenizer.advance()

                self.current_name = self.jackTokenizer.identifier()
                self.subSymbolTable.define(self.current_name, self.current_type, self.current_kind)

                self.jackTokenizer.advance()
            else:
                self.jackTokenizer.advance()
                break


    def _checkTypeStar(self):
        while True:
            if self.jackTokenizer.symbol() == ",":
                self.jackTokenizer.advance()
                self.jackTokenizer.advance()

                self.current_name = self.jackTokenizer.identifier()
                self.subSymbolTable.define(self.current_name, self.current_type, "arg")

                self.jackTokenizer.advance()
            else:
                break

    def _checkStarExpression(self):
        expression = []
        while True:
            if self.jackTokenizer.symbol() == ",":
                self.jackTokenizer.advance()
                expression.append(self.compileExpression())
                self.ExpressionListCounter += 1
            else:
                break
        return expression
        
    def _op(self, token):
        ops = ['+', '-', '*', '/', '&amp;', '|', '&lt;', '&gt;', '=']
        if token in ops:
            return True
        else:
            return False
        
    def _unaryOp(self, token):
        unaryOps = ['-', '~']
        if token in unaryOps:
            return True
        else:
            return False
        
    def _keywordConstant(self, token):
        keywordConstants = ['true', 'false', 'null', 'this']
        if token in keywordConstants:
            return True
        else:
            return False
        

    def _subroutineCall(self):
        self.doClassMethod.append(self.jackTokenizer.identifier())
        varnameOrMethod = self.jackTokenizer.identifier()
        self.jackTokenizer.advance()
        if self.jackTokenizer.symbol() == "(":
            self.noClass = True
            kindSubCall = self.subSymbolTable.kindOf("this")
            indexSubCall = self.subSymbolTable.indexOf("this")
            if kindSubCall == "NONE":
                kindSubCall = "pointer"
                indexSubCall = 0

            if kindSubCall == "arg":
                kindSubCall = "argument"
            elif kindSubCall == "var":
                kindSubCall = "local"

            varnameOrMethod = self.className + "." + varnameOrMethod
            self.vmWriter.writePush(kindSubCall, indexSubCall)
            
            self.jackTokenizer.advance()
            numOfArgs = self.compileExpressionList()
            self.ExpressionListCounter = 0

            numOfArgs += 1

            self.vmWriter.writeCall(varnameOrMethod, numOfArgs)
            self.jackTokenizer.advance()
        else:
            if self.subSymbolTable.indexOf(varnameOrMethod) != None:
                self.vmWriter.writePush("local", self.subSymbolTable.indexOf(varnameOrMethod))
            else:
                if self.classSymbolTable.indexOf(varnameOrMethod) != None:
                    if self.classSymbolTable.kindOf(varnameOrMethod) == "field":
                        self.vmWriter.writePush("this", self.classSymbolTable.indexOf(varnameOrMethod))
            self.jackTokenizer.advance()
            self.doClassMethod.append("." + self.jackTokenizer.identifier())
            self.doClassMethod[0] = self.doClassMethod[0] + self.doClassMethod[1]
            del self.doClassMethod[1]          
            self.jackTokenizer.advance()
            self.jackTokenizer.advance()
            numOfArgs = self.compileExpressionList()
            self.ExpressionListCounter = 0
            self.jackTokenizer.advance()


    def compileClass(self):
        if self.jackTokenizer.keyWord() == "class":
            self.jackTokenizer.advance()
            self.className = self.jackTokenizer.identifier()
            self.jackTokenizer.advance()
            self.jackTokenizer.advance()

            while True:
                if self.jackTokenizer.tokenType() == "KEYWORD" and self.jackTokenizer.keyWord() == "static" or self.jackTokenizer.keyWord() == "field":
                    self.compileClassVarDec()
                else:
                    print("Not a keyword OR not static or field.")
                    break
            
            while True:
                if self.jackTokenizer.tokenType() == "KEYWORD" and self.jackTokenizer.keyWord() == "constructor" or self.jackTokenizer.keyWord() == "function" or self.jackTokenizer.keyWord() == "method":
                    self.compileSubroutine()
                else:
                    print("Not a keyword OR not constructor, function, or method.")
                    break

            self.jackTokenizer.advance()
        else:
            return "not class."
        


    def compileClassVarDec(self):
        self.current_kind = self.jackTokenizer.keyWord()
        self.jackTokenizer.advance()
        self._typeOfChar()
        self.jackTokenizer.advance()

        self.current_name = self.jackTokenizer.identifier()
        self.classSymbolTable.define(self.current_name, self.current_type, self.current_kind)

        self.jackTokenizer.advance()
        self._checkStar()

    def compileSubroutine(self):
        self.subSymbolTable.reset()
        self.current_sub_kind = self.jackTokenizer.keyWord()
            
        self.jackTokenizer.advance()
        self._typeOfChar()
        self.jackTokenizer.advance()

        self.subroutineName = self.jackTokenizer.identifier()
        if self.current_sub_kind == "method":
            self.subSymbolTable.define("this", self.className, "arg")
            addSubType("method", self.subroutineName)
        elif self.current_sub_kind == "function":
            addSubType("function", self.subroutineName)
        
        self.jackTokenizer.advance()
        self.compileParameterList()
        self.jackTokenizer.advance()
        self.compileSubroutineBody()

    def compileParameterList(self):
        self.jackTokenizer.advance()
        if self.jackTokenizer.symbol() != ")":
            self._typeOfChar()
            self.jackTokenizer.advance()

            self.current_name = self.jackTokenizer.identifier()
            self.subSymbolTable.define(self.current_name, self.current_type, "arg")

            self.jackTokenizer.advance()
            self._checkTypeStar()
        else:
            pass


    def compileSubroutineBody(self):
        self.jackTokenizer.advance()
        while True:
            if self.jackTokenizer.tokenType() == "KEYWORD" and self.jackTokenizer.keyWord() == "var":
                self.compileVarDec()
            else:
                print("Not a keyword or not var.")
                break
        functionVarCount = self.subSymbolTable.varCount("var")
        self.vmWriter.writeFunction(f"{self.className}.{self.subroutineName}", functionVarCount)
        if self.current_sub_kind == "method":
            self.vmWriter.writePush("argument", 0)
            self.vmWriter.writePop("pointer", 0)
        if self.current_sub_kind == "constructor":
            self.vmWriter.writePush("constant", self.classSymbolTable.varCount("field"))
            self.vmWriter.writeCall("Memory.alloc", 1)
            self.vmWriter.writePop("pointer", 0)
        self.compileStatements()
        self.jackTokenizer.advance()
        
        if self.jackTokenizer.result[self.jackTokenizer.current_token + 1] == "function" or self.jackTokenizer.result[self.jackTokenizer.current_token + 1] == "method":
            self.jackTokenizer.advance()


    def compileVarDec(self):
        self.current_kind = self.jackTokenizer.keyWord()
        self.jackTokenizer.advance()
        self._typeOfChar()
        self.jackTokenizer.advance()

        self.current_name = self.jackTokenizer.identifier()
        self.subSymbolTable.define(self.current_name, self.current_type, self.current_kind)

        self.jackTokenizer.advance()
        self._subCheckStar()        
    
    def compileStatements(self):
        while True:
            if self.jackTokenizer.tokenType() == "KEYWORD":
                if self.jackTokenizer.keyWord() == "let":
                    self.compileLet()
                    if self.jackTokenizer.symbol() != "}":
                        self.jackTokenizer.advance()
                elif self.jackTokenizer.keyWord() == "if":
                    self.compileIf()
                elif self.jackTokenizer.keyWord() == "while":
                    self.compileWhile()
                elif self.jackTokenizer.keyWord() == "do":
                    self.compileDo()
                elif self.jackTokenizer.keyWord() == "return":
                    self.compileReturn()
                else:
                    return "Not a valid keyword."
            else:
                break

    def compileLet(self):
        self.letFlag = False
        self.jackTokenizer.advance()
        self.letVarName = self.jackTokenizer.identifier()
        letKind = self.subSymbolTable.kindOf(self.letVarName)
        if letKind == "arg":
            letKind = "argument"
        elif letKind == "var":
            letKind = "local"

        if self.jackTokenizer.result[self.jackTokenizer.current_token + 1] == "[":
            self.isArray = True
            self.compileExpression()
            self.vmWriter.writePop("temp", 0)
            self.vmWriter.writePop("pointer", 1)
            self.vmWriter.writePush("temp", 0)
            self.vmWriter.writePop("that", 0)
        else:
            self.letFlag = True
            self.jackTokenizer.advance()
            self.jackTokenizer.advance()
            self.compileExpression()
        if self.isArray == False:
            if self.subSymbolTable.kindOf(self.letVarName) != "NONE":
                self.vmWriter.writePop(letKind, self.subSymbolTable.indexOf(self.letVarName))
            else:
                letKind = self.classSymbolTable.kindOf(self.letVarName)
                if letKind == "field":
                    letKind = "this"
                self.vmWriter.writePop(letKind, self.classSymbolTable.indexOf(self.letVarName))
        self.isArray = False

    def compileIf(self):
        self.jackTokenizer.advance()
        self.jackTokenizer.advance()
        self.compileExpression()
        if self.andOr == True:
            if self.andOrSymbol == "and":
                self.vmWriter.writeArithmetic("and")
            elif self.andOrSymbol == "or":
                self.vmWriter.writeArithmetic("or")
        self.andOr = False
        self.vmWriter.writeArithmetic("not")
        self.label_counter += 1
        label1 = f"L{self.label_counter}"
        self.label_counter += 1
        label2 = f"L{self.label_counter}"
        self.vmWriter.writeIf(label1)
        if self.jackTokenizer.symbol() == ")" and self.jackTokenizer.result[self.jackTokenizer.current_token + 1] == "{":
            self.jackTokenizer.advance()
        self.jackTokenizer.advance()
        self.label_counter += 1
        self.compileStatements()
        self.vmWriter.writeGoto(label2)
        self.vmWriter.writeLabel(label1)
        self.jackTokenizer.advance()
        if self.jackTokenizer.keyWord() == "else":
            self.jackTokenizer.advance()
            self.jackTokenizer.advance()
            self.compileStatements()
            self.jackTokenizer.advance()
        self.vmWriter.writeLabel(label2)

    def compileWhile(self):
        self.label_counter += 1
        label1 = f"L{self.label_counter}"
        self.label_counter += 1
        label2 = f"L{self.label_counter}"
        self.jackTokenizer.advance()
        self.jackTokenizer.advance()
        self.vmWriter.writeLabel(label1)
        self.compileExpression()
        if self.andOr == True:
            if self.andOrSymbol == "and":
                self.vmWriter.writeArithmetic("and")
            elif self.andOrSymbol == "or":
                self.vmWriter.writeArithmetic("or")
        self.andOr = False
        self.vmWriter.writeArithmetic("not")
        self.vmWriter.writeIf(label2)
        if self.jackTokenizer.symbol() != "{":
            self.jackTokenizer.advance()
        self.jackTokenizer.advance()
        self.compileStatements()
        self.vmWriter.writeGoto(label1)
        self.vmWriter.writeLabel(label2)
        self.jackTokenizer.advance()

    def compileDo(self):
        self.jackTokenizer.advance()
        self._subroutineCall()
        self.vmWriter.writePop("temp", "0")
        self.argCounter = 0
        self.jackTokenizer.advance()

    def compileReturn(self):
        if self.current_type == "void" and self.current_sub_kind == "method" or self.current_sub_kind == "function":
            self.vmWriter.writePush("constant", "0")
        elif self.current_sub_kind == "method" and self.current_type != "void":
            self.vmWriter.writePush("argument", 0)
            self.vmWriter.writePop("pointer", 0)
        elif self.current_sub_kind == "function" and self.current_type != "void":
            pass
        if self.current_sub_kind == "constructor":
            self.vmWriter.writePush("pointer", 0)
        self.jackTokenizer.advance()
        if self.jackTokenizer.tokenType() != "SYMBOL":
            self.compileExpression()
            self.jackTokenizer.advance()
        else:
            pass
        self.vmWriter.writeReturn()

    def codeWrite(self, exp):
        if len(exp) == 1 and exp[0] != "None":
            if exp[0] == "not":
                self.vmWriter.writeArithmetic(exp[0])
            elif exp[0] == "&amp;":
                self.vmWriter.writeArithmetic(exp[0])
            elif exp[0] == "-":
                self.vmWriter.writeArithmetic(exp[0])
            elif exp[0] == "true":
                self.vmWriter.writePush("constant", 1)
                self.vmWriter.writeArithmetic("neg")
            elif exp[0] == "null" or exp[0] == "false":
                self.vmWriter.writePush("constant", 0)
            elif exp[0] == "this":
                self.vmWriter.writePush("pointer", 0)
            elif self.subSymbolTable.kindOf(exp[0]) == "var":
                self.vmWriter.writePush("local", self.subSymbolTable.indexOf(exp[0]))
            elif self.subSymbolTable.kindOf(exp[0]) == "arg":
                self.vmWriter.writePush("argument", self.subSymbolTable.indexOf(exp[0]))
            elif self.classSymbolTable.kindOf(exp[0]) == "field":
                self.vmWriter.writePush("this", self.classSymbolTable.indexOf(exp[0]))
            elif self.classSymbolTable.kindOf(exp[0]) == "static":
                self.vmWriter.writePush("static", self.classSymbolTable.indexOf(exp[0]))
            else:
                self.vmWriter.writePush("constant", exp[0])
        elif len(exp) == 3:
            self.codeWrite([exp[0]])
            self.codeWrite([exp[2]])
            self.vmWriter.writeArithmetic(exp[1])
        elif len(exp) == 2:
            if self._op(exp[1]):
                self.codeWrite([exp[0]])
                self.vmWriter.writeArithmetic(exp[1])
            elif self._op(exp[0]):
                self.codeWrite([exp[1]])
                self.vmWriter.writeArithmetic(exp[0])
            else:
                self.codeWrite([exp[1]])
                self.vmWriter.writeArithmetic(exp[0])
        elif len(exp) > 3 and not isinstance(exp, str):
            for i in range(1, len(exp)):
                self.codeWrite(exp[i])
            self.vmWriter.writeCall(exp[0], len(exp) - 1)


    def compileExpression(self):
        self.expOpExp = []
        localArray = self.expOpExp.copy()
        self.expCounter = 0
        whileTrue = False
        if self.jackTokenizer.symbol() == ")":
            return
        else:
            compiledTerm = self.compileTerm()
            if self.unaryOp == True and not isinstance(compiledTerm, int):
                for term in compiledTerm:
                    localArray.append(term)
                self.unaryOp = False
            else:
                compiledTerm = str(compiledTerm)
                localArray.append(compiledTerm)
            if self.jackTokenizer.result[self.jackTokenizer.current_token + 1] == "let" or self.jackTokenizer.result[self.jackTokenizer.current_token + 1] == "do" or self.jackTokenizer.result[self.jackTokenizer.current_token + 1] == "if" or self.jackTokenizer.result[self.jackTokenizer.current_token + 1] == "while":
                pass
            else:
                self.jackTokenizer.advance()
                if self.negate == True and self.jackTokenizer.symbol() == "&amp;":
                    self.codeWrite(localArray)
            while True:
                self.andOr = False
                if self._op(self.jackTokenizer.symbol()):
                    if self.jackTokenizer.symbol() == "&amp;" or self.jackTokenizer.symbol() == "|":
                        self.andOr = True
                        if self.jackTokenizer.symbol() == "&amp;" and self.jackTokenizer.result[self.jackTokenizer.current_token + 1] == "(":
                            self.andOrSymbol = "and"
                        elif self.jackTokenizer.symbol() == "|" and self.jackTokenizer.result[self.jackTokenizer.current_token + 1] == "(":
                            self.andOrSymbol = "or"
                    whileTrue = True
                    if self.jackTokenizer.symbol() == "-":
                        self.codeWrite(localArray)
                        localArray = []
                    if self.negate == True and self.jackTokenizer.symbol() == "&amp;":
                        localArray = []
                    self.negate = False
                    self.expCounter += 1
                    localArray.append(self.jackTokenizer.symbol())
                    if self.jackTokenizer.result[self.jackTokenizer.current_token + 1] != "let" or self.jackTokenizer.result[self.jackTokenizer.current_token + 1] != "do" or self.jackTokenizer.result[self.jackTokenizer.current_token + 1] != "if" or self.jackTokenizer.result[self.jackTokenizer.current_token + 1] != "while":
                        self.jackTokenizer.advance()
                    if self.compileTerm() != None:
                        localArray.append(str(self.compileTerm()))
                    self.codeWrite(localArray)
                    if self.thatFlag == True:
                        self.vmWriter.writePush("that", 0)
                        self.thatFlag = False
                    self.returnArray = localArray
                    localArray = []
                    self.jackTokenizer.advance()
                else:
                    if whileTrue == False:
                        self.codeWrite(localArray)
                        if self.thatFlag == True:
                            self.vmWriter.writePush("that", 0)
                            self.thatFlag = False
                        self.returnArray = localArray
                    whileTrue = False
                    break
            self.expCounter = 0

            if self.jackTokenizer.symbol() == ",":
                self.argCounter += 1
                pass
        return self.returnArray

    def compileTerm(self):
        if self.jackTokenizer.tokenType() == "IDENTIFIER" and self.jackTokenizer.result[self.jackTokenizer.current_token + 1] == "[":
            if self.subSymbolTable.kindOf(self.jackTokenizer.identifier()) == "arg":
                self.vmWriter.writePush("argument", self.subSymbolTable.indexOf(self.jackTokenizer.identifier()))
            else:
                self.vmWriter.writePush("local", self.subSymbolTable.indexOf(self.jackTokenizer.identifier()))
            self.jackTokenizer.advance()
            self.jackTokenizer.advance()
            self.compileExpression()
            self.vmWriter.writeArithmetic("+")

            if self.jackTokenizer.result[self.jackTokenizer.current_token + 1] != "=":
                self.vmWriter.writePop("pointer", 1)
                self.vmWriter.writePush("that", 0)
                self.letFlag = False

            if self.jackTokenizer.result[self.jackTokenizer.current_token + 1] == "=" or self.jackTokenizer.result[self.jackTokenizer.current_token + 1] == ";":
                self.letFlag = True

            if self.jackTokenizer.result[self.jackTokenizer.current_token + 1] != ";" and self.jackTokenizer.result[self.jackTokenizer.current_token + 1] != "]" and self.jackTokenizer.result[self.jackTokenizer.current_token + 1] != ")" and self.jackTokenizer.result[self.jackTokenizer.current_token + 1] != "+" and self.jackTokenizer.result[self.jackTokenizer.current_token + 1] != "*":
                self.jackTokenizer.advance()
                self.jackTokenizer.advance()
                self.compileExpression()

        if self.jackTokenizer.tokenType() == "IDENTIFIER" and self.jackTokenizer.result[self.jackTokenizer.current_token + 1] == ".":
            className = self.jackTokenizer.identifier()
            self.jackTokenizer.advance()
            self.jackTokenizer.advance()
            methodName = self.jackTokenizer.identifier()
            letClassMethod = f"{className}.{methodName}"
            self.doClassMethod.append(letClassMethod)
            if self.classSymbolTable.indexOf(className) != None:
                    if self.classSymbolTable.kindOf(className) == "field":
                        self.vmWriter.writePush("this", self.classSymbolTable.indexOf(className))

            self.jackTokenizer.advance()
            self.jackTokenizer.advance()
            argNumber = self.compileExpressionList()
            self.argCounter += argNumber
            self.ExpressionListCounter = 0
        if self.jackTokenizer.tokenType() == "IDENTIFIER" and self.jackTokenizer.result[self.jackTokenizer.current_token + 1] == "(":
            self.vmWriter.writePush(self.subSymbolTable.kindOf("this"), self.subSymbolTable.indexOf("this"))
            methodName = self.jackTokenizer.identifier()
            self.jackTokenizer.advance()
            self.jackTokenizer.advance()
            argNumber = self.compileExpressionList()
            self.argCounter += argNumber
            self.ExpressionListCounter = 0
            if self.current_kind == "method":
                self.argCounter += 1
                thisType = self.subSymbolTable.typeOf("this")
            self.vmWriter.writeCall(f"{thisType}.{methodName}", self.argCounter)
        if self.jackTokenizer.tokenType() == "INT_CONST":
            return self.jackTokenizer.intVal()
        if self.jackTokenizer.tokenType() == "STRING_CONST":
            lookup_table = {
                ' ': 32, '!': 33, '"': 34, '#': 35, '$': 36, '%': 37, '&': 38, "'": 39,
                '(': 40, ')': 41, '*': 42, '+': 43, ',': 44, '-': 45, '.': 46, '/': 47,
                '0': 48, '1': 49, '2': 50, '3': 51, '4': 52, '5': 53, '6': 54, '7': 55,
                '8': 56, '9': 57, ':': 58, ';': 59, '<': 60, '=': 61, '>': 62, '?': 63,
                '@': 64, 'A': 65, 'B': 66, 'C': 67, 'D': 68, 'E': 69, 'F': 70, 'G': 71,
                'H': 72, 'I': 73, 'J': 74, 'K': 75, 'L': 76, 'M': 77, 'N': 78, 'O': 79,
                'P': 80, 'Q': 81, 'R': 82, 'S': 83, 'T': 84, 'U': 85, 'V': 86, 'W': 87,
                'X': 88, 'Y': 89, 'Z': 90, '[': 91, '\\': 92, ']': 93, '^': 94, '_': 95,
                '`': 96, 'a': 97, 'b': 98, 'c': 99, 'd': 100, 'e': 101, 'f': 102, 'g': 103,
                'h': 104, 'i': 105, 'j': 106, 'k': 107, 'l': 108, 'm': 109, 'n': 110, 'o': 111,
                'p': 112, 'q': 113, 'r': 114, 's': 115, 't': 116, 'u': 117, 'v': 118, 'w': 119,
                'x': 120, 'y': 121, 'z': 122, '{': 123, '|': 124, '}': 125, '~': 126,
                'DEL': 127, 'newLine': 128, 'backSpace': 129, 'leftArrow': 130, 'upArrow': 131,
                'rightArrow': 132, 'downArrow': 133, 'home': 134, 'end': 135, 'pageUp': 136,
                'pageDown': 137, 'insert': 138, 'delete': 139, 'esc': 140, 'f1': 141, 'f2': 142,
                'f3': 143, 'f4': 144, 'f5': 145, 'f6': 146, 'f7': 147, 'f8': 148, 'f9': 149,
                'f10': 150, 'f11': 151, 'f12': 152
            }
            def get_character_code(c):
                return lookup_table.get(c, None)

            string = self.jackTokenizer.stringVal()
            stringLength = len(string)
            self.vmWriter.writePush("constant", stringLength)
            self.vmWriter.writeCall("String.new", 1)
            for c in string:
                char = get_character_code(c)
                self.vmWriter.writePush("constant", char)
                self.vmWriter.writeCall("String.appendChar", 2)
        elif self.jackTokenizer.tokenType() == "IDENTIFIER":
            return self.jackTokenizer.identifier()
        if self.jackTokenizer.tokenType() == "KEYWORD":
            if self.current_sub_kind != "constructor":
                return self.jackTokenizer.keyWord()
            elif self.jackTokenizer.keyWord() == "false" or self.jackTokenizer.keyWord() == "true":
                return self.jackTokenizer.keyWord()
            else:
                pass
        if self.jackTokenizer.tokenType() == "SYMBOL" and self.jackTokenizer.symbol() == "(":
            self.jackTokenizer.advance()
            self.compileExpression()
        if self._unaryOp(self.jackTokenizer.symbol()):
            symbol = self.jackTokenizer.symbol()
            identifier = None
            if symbol == "-":
                self.unaryOp = True
                symbol = "neg"
                self.jackTokenizer.advance()
                identifier = self.compileTerm()
            else:
                pass

            if symbol == "~":
                symbol = "not"
                self.jackTokenizer.advance()
                self.compileExpression()
                self.negate = True
            
            if identifier is not None:
                return symbol, str(identifier)
            else:
                return symbol

    def compileExpressionList(self):
        firstExpression = self.compileExpression()
        self.returnArray = []
        self.functAndExpression = self.doClassMethod
        if firstExpression != None:
            self.ExpressionListCounter += 1
            self.functAndExpression.extend(firstExpression)
        nExpressions = self._checkStarExpression()
        if len(self.functAndExpression) == 1 and any('.' in element for element in self.functAndExpression):
            splitFunctAndExpr = sum([elem.split('.') if '.' in elem else [elem] for elem in self.functAndExpression], [])
            splitFunctAndExprClass = splitFunctAndExpr[0]
            splitFunctAndExprMethod = splitFunctAndExpr[1]
            numberOfArguments = 0
            if returnSubType(splitFunctAndExprMethod) == "function":
                numberOfArguments = 0
            
            if returnSubType(splitFunctAndExprMethod) == "method":
                numberOfArguments += 1

            if splitFunctAndExprClass == "Keyboard" or splitFunctAndExprMethod == "new" or splitFunctAndExprMethod == "clearScreen":
                numberOfArguments = 0

            if self.subSymbolTable.kindOf(splitFunctAndExprClass) != "NONE":
                    self.vmWriter.writeCall(str(self.subSymbolTable.typeOf(splitFunctAndExprClass)) + "." + splitFunctAndExprMethod, numberOfArguments)
            elif self.classSymbolTable.kindOf(splitFunctAndExprClass) != "NONE":
                    self.vmWriter.writeCall(str(self.classSymbolTable.typeOf(splitFunctAndExprClass)) + "." + splitFunctAndExprMethod, numberOfArguments)
            else:
                self.vmWriter.writeCall(self.functAndExpression[0], numberOfArguments)
        else:
            pass

        if self.subCallFunction == True:
            self.vmWriter.writeCall(str(self.doClassMethod[0]), self.ExpressionListCounter)
            self.subCallFunction = False
        else:
            if firstExpression != None and self.noClass == False:
                if self.current_kind == "method":
                    self.argCounter += 1
                if any('.' in element for element in self.doClassMethod[0]):
                    splitFunctAndExpr2 = sum([elem.split('.') if '.' in elem else [elem] for elem in self.functAndExpression], [])
                    splitFunctAndExprClass2 = splitFunctAndExpr2[0]
                    splitFunctAndExprMethod2 = splitFunctAndExpr2[1]
                    if splitFunctAndExprClass2 == "Keyboard" or splitFunctAndExprMethod2 == "clearScreen":
                        self.ExpressionListCounter = 0

                    if returnSubType(splitFunctAndExprMethod2) == "method":
                        self.ExpressionListCounter += 1
            
                if self.subSymbolTable.kindOf(self.doClassMethod[0]) != "NONE":
                    self.vmWriter.writeCall(str(self.subSymbolTable.kindOf(self.doClassMethod[0])), self.ExpressionListCounter)
                elif self.classSymbolTable.kindOf(self.doClassMethod[0]) != "NONE":
                    self.vmWriter.writeCall(str(self.classSymbolTable.kindOf(self.doClassMethod[0])), self.ExpressionListCounter)
                else:
                    if any('.' in element for element in self.doClassMethod[0]):
                        if self.subSymbolTable.kindOf(splitFunctAndExprClass2) != "NONE":
                            self.vmWriter.writeCall(str(self.subSymbolTable.typeOf(splitFunctAndExprClass2)) + "." + splitFunctAndExprMethod2, self.ExpressionListCounter)
                        elif self.classSymbolTable.kindOf(splitFunctAndExprClass2) != "NONE":
                                self.vmWriter.writeCall(str(self.classSymbolTable.typeOf(splitFunctAndExprClass2)) + "." + splitFunctAndExprMethod2, self.ExpressionListCounter)
                        else:
                            self.vmWriter.writeCall(str(self.doClassMethod[0]), self.ExpressionListCounter)
                    else:
                        self.vmWriter.writeCall(str(self.doClassMethod[0]), self.ExpressionListCounter)
        
        self.noClass = False

        if nExpressions:
            for expression in nExpressions:
                self.functAndExpression.append(expression)
        self.doClassMethod = []
        return self.ExpressionListCounter


if len(sys.argv) != 2:
    sys.exit(1)

directory = sys.argv[1]
files = [file for file in os.listdir(directory) if file.endswith('.jack')]
directory_name = os.path.basename(os.path.normpath(directory))
directory_path = os.path.join(directory, directory_name)

if "PongGame.jack" in files:
    files.append(files.pop(files.index("PongGame.jack")))

if "Main.jack" in files:
    files.append(files.pop(files.index("Main.jack")))

def main():
    for file_name in files:
        file_name_no_ext = file_name.split(".")[0]
        file_path = os.path.join(directory, file_name)
        filestream = open(directory + f"{file_name_no_ext}" + ".vm","w")
        
        with open(file_path, 'r') as file:
            text = file.read()
            jackTokenizer = JackTokenizer(text)
            compilationEngine = CompilationEngine(jackTokenizer, filestream)
            compilationEngine.compileClass()

if __name__ == "__main__":
    main()