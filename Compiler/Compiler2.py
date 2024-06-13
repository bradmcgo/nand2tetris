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

        if kind == "field":
            self.add_row_class(name, type, kind, self.fieldIndex)
            self.fieldIndex += 1
            
        if kind == "var":
            self.add_row_class(name, type, kind, self.varIndex)
            self.varIndex += 1

        if kind == "arg":
            self.add_row_class(name, type, kind, self.argIndex)
            self.argIndex += 1

        else:
            self.add_row_class(name, type, kind, self.argIndex)

    def varCount(self, kind):
        numberOfVars = sum(1 for row in self.table if row["kind"] == kind)
        print("numberOfVars", numberOfVars)
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
        # print("self.lines:", self.lines)
        # Final list of tokens.
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

    def writePush(self, segment, index):
        self.outputFile.write(f"push {segment}{index}\n")

    def writePop(self, segment, index):
        self.outputFile.write(f"pop {segment}{index}\n")

    def writeArithmetic(self, command):
        self.outputFile.write(f"{command}\n")

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

        # if self.jackTokenizer.hasMoreTokens():
        self.jackTokenizer.advance()
        

    def _typeOfChar(self):
        if self.jackTokenizer.tokenType() == "KEYWORD":
            self.current_type = self.jackTokenizer.keyWord()
            return f"<keyword> {self.jackTokenizer.keyWord()} </keyword>\n"
        if self.jackTokenizer.tokenType() == "IDENTIFIER":
            self.current_type = self.jackTokenizer.identifier()

            kind = self.subSymbolTable.kindOf(self.jackTokenizer.identifier())
            if kind in ["arg", "var"]:
                return f"<identifier> {self.jackTokenizer.identifier()} </identifier><type> {self.subSymbolTable.typeOf(self.jackTokenizer.identifier())} </type><kind> {self.subSymbolTable.kindOf(self.jackTokenizer.identifier())} </kind><index> {self.subSymbolTable.indexOf(self.jackTokenizer.identifier())} </index>\n"
            else:
                return f"<identifier> {self.jackTokenizer.identifier()} </identifier><type> {self.classSymbolTable.typeOf(self.jackTokenizer.identifier())} </type><kind> {self.classSymbolTable.kindOf(self.jackTokenizer.identifier())} </kind><index> {self.classSymbolTable.indexOf(self.jackTokenizer.identifier())} </index>\n"
    
    def _checkStar(self):
        while True:
            if self.jackTokenizer.symbol() == ",":
                self.outputFile.write(f"<symbol> {self.jackTokenizer.symbol()} </symbol>\n")
                self.jackTokenizer.advance()

                self.current_name = self.jackTokenizer.identifier()
                self.classSymbolTable.define(self.current_name, self.current_type, self.current_kind)

                kind = self.subSymbolTable.kindOf(self.jackTokenizer.identifier())
                if kind in ["arg", "var"]:
                    self.outputFile.write(f"<identifier> {self.jackTokenizer.identifier()} </identifier><type> {self.subSymbolTable.typeOf(self.jackTokenizer.identifier())} </type><kind> {self.subSymbolTable.kindOf(self.jackTokenizer.identifier())} </kind><index> {self.subSymbolTable.indexOf(self.jackTokenizer.identifier())} </index>\n")
                else:
                    self.outputFile.write(f"<identifier> {self.jackTokenizer.identifier()} </identifier><type> {self.classSymbolTable.typeOf(self.jackTokenizer.identifier())} </type><kind> {self.classSymbolTable.kindOf(self.jackTokenizer.identifier())} </kind><index> {self.classSymbolTable.indexOf(self.jackTokenizer.identifier())} </index>\n")
                
                self.jackTokenizer.advance()
            else:
                self.outputFile.write(f"<symbol> {self.jackTokenizer.symbol()} </symbol>\n")
                self.jackTokenizer.advance()
                break

    def _subCheckStar(self):
        while True:
            if self.jackTokenizer.symbol() == ",":
                self.outputFile.write(f"<symbol> {self.jackTokenizer.symbol()} </symbol>\n")
                self.jackTokenizer.advance()

                self.current_name = self.jackTokenizer.identifier()
                self.subSymbolTable.define(self.current_name, self.current_type, self.current_kind)

                kind = self.subSymbolTable.kindOf(self.jackTokenizer.identifier())
                if kind in ["arg", "var"]:
                    self.outputFile.write(f"<identifier> {self.jackTokenizer.identifier()} </identifier><type> {self.subSymbolTable.typeOf(self.jackTokenizer.identifier())} </type><kind> {self.subSymbolTable.kindOf(self.jackTokenizer.identifier())} </kind><index> {self.subSymbolTable.indexOf(self.jackTokenizer.identifier())} </index>\n")
                else:
                    self.outputFile.write(f"<identifier> {self.jackTokenizer.identifier()} </identifier><type> {self.classSymbolTable.typeOf(self.jackTokenizer.identifier())} </type><kind> {self.classSymbolTable.kindOf(self.jackTokenizer.identifier())} </kind><index> {self.classSymbolTable.indexOf(self.jackTokenizer.identifier())} </index>\n")
                
                self.jackTokenizer.advance()
            else:
                self.outputFile.write(f"<symbol> {self.jackTokenizer.symbol()} </symbol>\n")
                self.jackTokenizer.advance()
                break


    def _checkTypeStar(self):
        while True:
            if self.jackTokenizer.symbol() == ",":
                self.outputFile.write(f"<symbol> {self.jackTokenizer.symbol()} </symbol>\n")
                self.jackTokenizer.advance()
                self.outputFile.write(self._typeOfChar())
                self.jackTokenizer.advance()

                self.current_name = self.jackTokenizer.identifier()
                self.subSymbolTable.define(self.current_name, self.current_type, "arg")

                kind = self.subSymbolTable.kindOf(self.jackTokenizer.identifier())
                if kind in ["arg", "var"]:
                    self.outputFile.write(f"<identifier> {self.jackTokenizer.identifier()} </identifier><type> {self.subSymbolTable.typeOf(self.jackTokenizer.identifier())} </type><kind> {self.subSymbolTable.kindOf(self.jackTokenizer.identifier())} </kind><index> {self.subSymbolTable.indexOf(self.jackTokenizer.identifier())} </index>\n")
                else:
                    self.outputFile.write(f"<identifier> {self.jackTokenizer.identifier()} </identifier><type> {self.classSymbolTable.typeOf(self.jackTokenizer.identifier())} </type><kind> {self.classSymbolTable.kindOf(self.jackTokenizer.identifier())} </kind><index> {self.classSymbolTable.indexOf(self.jackTokenizer.identifier())} </index>\n")
                
                self.jackTokenizer.advance()
            else:
                break

    def _checkStarExpression(self):
        while True:
            if self.jackTokenizer.symbol() == ",":
                self.jackTokenizer.advance()
                self.compileExpression()
            else:
                break

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
        self.outputFile.write(f"<identifier> {self.jackTokenizer.identifier()} </identifier>\n")        
        self.jackTokenizer.advance()
        if self.jackTokenizer.symbol() == "(":
            self.outputFile.write(f"<symbol> {self.jackTokenizer.symbol()} </symbol>\n")
            self.jackTokenizer.advance()
            self.compileExpressionList()
            self.outputFile.write(f"<symbol> {self.jackTokenizer.symbol()} </symbol>\n")
            self.jackTokenizer.advance()
        else:
            self.outputFile.write(f"<symbol> {self.jackTokenizer.symbol()} </symbol>\n")
            self.jackTokenizer.advance()

            kind = self.subSymbolTable.kindOf(self.jackTokenizer.identifier())
            if kind in ["arg", "var"]:
                self.outputFile.write(f"<identifier> {self.jackTokenizer.identifier()} </identifier><type> {self.subSymbolTable.typeOf(self.jackTokenizer.identifier())} </type><kind> {self.subSymbolTable.kindOf(self.jackTokenizer.identifier())} </kind><index> {self.subSymbolTable.indexOf(self.jackTokenizer.identifier())} </index>\n")
            else:
                self.outputFile.write(f"<identifier> {self.jackTokenizer.identifier()} </identifier><type> {self.classSymbolTable.typeOf(self.jackTokenizer.identifier())} </type><kind> {self.classSymbolTable.kindOf(self.jackTokenizer.identifier())} </kind><index> {self.classSymbolTable.indexOf(self.jackTokenizer.identifier())} </index>\n")

            self.jackTokenizer.advance()
            self.outputFile.write(f"<symbol> {self.jackTokenizer.symbol()} </symbol>\n")
            self.jackTokenizer.advance()
            self.compileExpressionList()
            self.outputFile.write(f"<symbol> {self.jackTokenizer.symbol()} </symbol>\n")
            self.jackTokenizer.advance()


    def compileClass(self):
        if self.jackTokenizer.keyWord() == "class":
            self.outputFile.write(f"<class>\n<keyword> {self.jackTokenizer.keyWord()} </keyword>\n")
            self.jackTokenizer.advance()
            self.className = self.jackTokenizer.identifier()
            self.outputFile.write(f"<identifier> {self.jackTokenizer.identifier()} </identifier>\n")
            self.jackTokenizer.advance()
            self.outputFile.write(f"<symbol> {self.jackTokenizer.symbol()} </symbol>\n")
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

            self.outputFile.write(f"<symbol> {self.jackTokenizer.symbol()} </symbol>\n")
            self.outputFile.write(f"</class>\n")
            self.jackTokenizer.advance()
        else:
            return "not class."
        
        print("classSymbolTable:", self.classSymbolTable.table)


    def compileClassVarDec(self):
        self.current_kind = self.jackTokenizer.keyWord()
        self.outputFile.write(f"<classVarDec>\n<keyword> {self.jackTokenizer.keyWord()} </keyword>\n")
        self.jackTokenizer.advance()
        self.outputFile.write(self._typeOfChar())
        self.jackTokenizer.advance()

        self.current_name = self.jackTokenizer.identifier()
        self.classSymbolTable.define(self.current_name, self.current_type, self.current_kind)

        kind = self.subSymbolTable.kindOf(self.jackTokenizer.identifier())
        if kind in ["arg", "var"]:
            self.outputFile.write(f"<identifier> {self.jackTokenizer.identifier()} </identifier><type> {self.subSymbolTable.typeOf(self.jackTokenizer.identifier())} </type><kind> {self.subSymbolTable.kindOf(self.jackTokenizer.identifier())} </kind><index> {self.subSymbolTable.indexOf(self.jackTokenizer.identifier())} </index>\n")
        else:
            self.outputFile.write(f"<identifier> {self.jackTokenizer.identifier()} </identifier><type> {self.classSymbolTable.typeOf(self.jackTokenizer.identifier())} </type><kind> {self.classSymbolTable.kindOf(self.jackTokenizer.identifier())} </kind><index> {self.classSymbolTable.indexOf(self.jackTokenizer.identifier())} </index>\n")

        self.jackTokenizer.advance()
        self._checkStar()
        self.outputFile.write(f"</classVarDec>\n")


    def compileSubroutine(self):
        self.subSymbolTable.reset()
        self.current_kind = self.jackTokenizer.keyWord()
        if self.current_kind == "method":
            self.subSymbolTable.define("this", self.className, "arg")
        self.outputFile.write(f"<subroutineDec>\n<keyword> {self.jackTokenizer.keyWord()} </keyword>\n")
        self.jackTokenizer.advance()
        self.outputFile.write(self._typeOfChar())
        self.jackTokenizer.advance()
        self.outputFile.write(f"<identifier> {self.jackTokenizer.identifier()} </identifier>\n")
        self.jackTokenizer.advance()
        self.outputFile.write(f"<symbol> {self.jackTokenizer.symbol()} </symbol>\n")
        self.compileParameterList()
        self.outputFile.write(f"<symbol> {self.jackTokenizer.symbol()} </symbol>\n")
        self.jackTokenizer.advance()
        self.compileSubroutineBody()
        self.outputFile.write(f"</subroutineDec>\n")

        print("subSymbolTable:", self.subSymbolTable.table)

    def compileParameterList(self):
        self.outputFile.write(f"<parameterList>\n")
        self.jackTokenizer.advance()
        if self.jackTokenizer.symbol() != ")":
            self.outputFile.write(self._typeOfChar())
            self.jackTokenizer.advance()

            self.current_name = self.jackTokenizer.identifier()
            self.subSymbolTable.define(self.current_name, self.current_type, "arg")

            kind = self.subSymbolTable.kindOf(self.jackTokenizer.identifier())
            if kind in ["arg", "var"]:
                self.outputFile.write(f"<identifier> {self.jackTokenizer.identifier()} </identifier><type> {self.subSymbolTable.typeOf(self.jackTokenizer.identifier())} </type><kind> {self.subSymbolTable.kindOf(self.jackTokenizer.identifier())} </kind><index> {self.subSymbolTable.indexOf(self.jackTokenizer.identifier())} </index>\n")
            else:
                self.outputFile.write(f"<identifier> {self.jackTokenizer.identifier()} </identifier><type> {self.classSymbolTable.typeOf(self.jackTokenizer.identifier())} </type><kind> {self.classSymbolTable.kindOf(self.jackTokenizer.identifier())} </kind><index> {self.classSymbolTable.indexOf(self.jackTokenizer.identifier())} </index>\n")
            
            self.jackTokenizer.advance()
            self._checkTypeStar()
            self.outputFile.write(f"</parameterList>\n")
        else:
            self.outputFile.write(f"</parameterList>\n")


    def compileSubroutineBody(self):
        self.outputFile.write(f"<subroutineBody>\n<symbol> {self.jackTokenizer.symbol()} </symbol>\n")
        self.jackTokenizer.advance()
        while True:
            if self.jackTokenizer.tokenType() == "KEYWORD" and self.jackTokenizer.keyWord() == "var":
                self.compileVarDec()
            else:
                print("Not a keyword or not var.")
                break
        self.compileStatements()
        self.jackTokenizer.advance()
        self.outputFile.write(f"<symbol> {self.jackTokenizer.symbol()} </symbol>\n")
        self.outputFile.write(f"</subroutineBody>\n")
        self.jackTokenizer.advance()


    def compileVarDec(self):
        self.current_kind = self.jackTokenizer.keyWord()
        self.outputFile.write(f"<varDec>\n<keyword> {self.jackTokenizer.keyWord()} </keyword>\n")
        self.jackTokenizer.advance()
        self.outputFile.write(self._typeOfChar())
        self.jackTokenizer.advance()

        self.current_name = self.jackTokenizer.identifier()
        self.subSymbolTable.define(self.current_name, self.current_type, self.current_kind)

        kind = self.subSymbolTable.kindOf(self.jackTokenizer.identifier())
        if kind in ["arg", "var"]:
            self.outputFile.write(f"<identifier> {self.jackTokenizer.identifier()} </identifier><type> {self.subSymbolTable.typeOf(self.jackTokenizer.identifier())} </type><kind> {self.subSymbolTable.kindOf(self.jackTokenizer.identifier())} </kind><index> {self.subSymbolTable.indexOf(self.jackTokenizer.identifier())} </index>\n")
        else:
            self.outputFile.write(f"<identifier> {self.jackTokenizer.identifier()} </identifier><type> {self.classSymbolTable.typeOf(self.jackTokenizer.identifier())} </type><kind> {self.classSymbolTable.kindOf(self.jackTokenizer.identifier())} </kind><index> {self.classSymbolTable.indexOf(self.jackTokenizer.identifier())} </index>\n")
        
        self.jackTokenizer.advance()
        self._subCheckStar()
        self.outputFile.write(f"</varDec>\n")
        
    
    def compileStatements(self):
        self.outputFile.write(f"<statements>\n")
        while True:
            if self.jackTokenizer.tokenType() == "KEYWORD":
                if self.jackTokenizer.keyWord() == "let":
                    self.compileLet()
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
                self.outputFile.write(f"</statements>\n")
                break


    def compileLet(self):
        self.outputFile.write(f"<letStatement>\n<keyword> {self.jackTokenizer.keyWord()} </keyword>\n")
        self.jackTokenizer.advance()

        kind = self.subSymbolTable.kindOf(self.jackTokenizer.identifier())
        if kind in ["arg", "var"]:
            self.outputFile.write(f"<identifier> {self.jackTokenizer.identifier()} </identifier><type> {self.subSymbolTable.typeOf(self.jackTokenizer.identifier())} </type><kind> {self.subSymbolTable.kindOf(self.jackTokenizer.identifier())} </kind><index> {self.subSymbolTable.indexOf(self.jackTokenizer.identifier())} </index>\n")
        else:
            self.outputFile.write(f"<identifier> {self.jackTokenizer.identifier()} </identifier><type> {self.classSymbolTable.typeOf(self.jackTokenizer.identifier())} </type><kind> {self.classSymbolTable.kindOf(self.jackTokenizer.identifier())} </kind><index> {self.classSymbolTable.indexOf(self.jackTokenizer.identifier())} </index>\n")
        
        self.jackTokenizer.advance()
        if self.jackTokenizer.symbol() == "[":
            self.outputFile.write(f"<symbol> {self.jackTokenizer.symbol()} </symbol>\n")
            self.jackTokenizer.advance()
            self.compileExpression()
            self.outputFile.write(f"<symbol> {self.jackTokenizer.symbol()} </symbol>\n")
            self.jackTokenizer.advance()

        self.outputFile.write(f"<symbol> {self.jackTokenizer.symbol()} </symbol>\n")
        self.jackTokenizer.advance()
        self.compileExpression()
        self.outputFile.write(f"<symbol> {self.jackTokenizer.symbol()} </symbol>\n")
        self.outputFile.write(f"</letStatement>\n")


    def compileIf(self):
        self.outputFile.write(f"<ifStatement>\n<keyword> {self.jackTokenizer.keyWord()} </keyword>\n")
        self.jackTokenizer.advance()
        self.outputFile.write(f"<symbol> {self.jackTokenizer.symbol()} </symbol>\n")
        self.jackTokenizer.advance()
        self.compileExpression()
        self.outputFile.write(f"<symbol> {self.jackTokenizer.symbol()} </symbol>\n")
        self.jackTokenizer.advance()
        self.outputFile.write(f"<symbol> {self.jackTokenizer.symbol()} </symbol>\n")
        self.jackTokenizer.advance()
        self.compileStatements()
        self.outputFile.write(f"<symbol> {self.jackTokenizer.symbol()} </symbol>\n")
        self.jackTokenizer.advance()
        if self.jackTokenizer.keyWord() == "else":
            self.outputFile.write(f"<keyword> {self.jackTokenizer.keyWord()} </keyword>\n")
            self.jackTokenizer.advance()
            self.outputFile.write(f"<symbol> {self.jackTokenizer.symbol()} </symbol>\n")
            self.jackTokenizer.advance()
            self.compileStatements()
            self.outputFile.write(f"<symbol> {self.jackTokenizer.symbol()} </symbol>\n")
            self.jackTokenizer.advance()
        self.outputFile.write(f"</ifStatement>\n")


    def compileWhile(self):
        self.outputFile.write(f"<whileStatement>\n<keyword> {self.jackTokenizer.keyWord()} </keyword>\n")
        self.jackTokenizer.advance()
        self.outputFile.write(f"<symbol> {self.jackTokenizer.symbol()} </symbol>\n")
        self.jackTokenizer.advance()
        self.compileExpression()
        self.outputFile.write(f"<symbol> {self.jackTokenizer.symbol()} </symbol>\n")
        self.jackTokenizer.advance()
        self.outputFile.write(f"<symbol> {self.jackTokenizer.symbol()} </symbol>\n")
        self.jackTokenizer.advance()
        self.compileStatements()
        self.outputFile.write(f"<symbol> {self.jackTokenizer.symbol()} </symbol>\n")
        self.outputFile.write(f"</whileStatement>\n")
        self.jackTokenizer.advance()


    def compileDo(self):
        self.outputFile.write(f"<doStatement>\n<keyword> {self.jackTokenizer.keyWord()} </keyword>\n")
        self.jackTokenizer.advance()
        self._subroutineCall()
        self.outputFile.write(f"<symbol> {self.jackTokenizer.symbol()} </symbol>\n")
        self.outputFile.write(f"</doStatement>\n")
        self.jackTokenizer.advance()


    def compileReturn(self):
        self.outputFile.write(f"<returnStatement>\n<keyword> {self.jackTokenizer.keyWord()} </keyword>\n")
        self.jackTokenizer.advance()
        if self.jackTokenizer.tokenType() != "SYMBOL":
            self.compileExpression()
            self.outputFile.write(f"<symbol> {self.jackTokenizer.symbol()} </symbol>\n")
        else:
            self.outputFile.write(f"<symbol> {self.jackTokenizer.symbol()} </symbol>\n")
        self.outputFile.write(f"</returnStatement>\n")


    def compileExpression(self):
        if self.jackTokenizer.symbol() == ")":
            return
        else:
            self.outputFile.write(f"<expression>\n")   
            self.compileTerm()
            self.jackTokenizer.advance()
            while True:
                if self._op(self.jackTokenizer.symbol()):
                    self.outputFile.write(f"<symbol> {self.jackTokenizer.symbol()} </symbol>\n")
                    self.jackTokenizer.advance()
                    self.compileTerm()
                    self.jackTokenizer.advance()
                else:
                    break
            self.outputFile.write(f"</expression>\n")
            if self.jackTokenizer.symbol() == ",":
                self.outputFile.write(f"<symbol> {self.jackTokenizer.symbol()} </symbol>\n")


    def compileTerm(self):
        self.outputFile.write(f"<term>\n")
        # additional logic for parsing lookaheads.
        if self.jackTokenizer.tokenType() == "IDENTIFIER" and self.jackTokenizer.result[self.jackTokenizer.current_token + 1] == "[":
            
            kind = self.subSymbolTable.kindOf(self.jackTokenizer.identifier())
            if kind in ["arg", "var"]:
                self.outputFile.write(f"<identifier> {self.jackTokenizer.identifier()} </identifier><type> {self.subSymbolTable.typeOf(self.jackTokenizer.identifier())} </type><kind> {self.subSymbolTable.kindOf(self.jackTokenizer.identifier())} </kind><index> {self.subSymbolTable.indexOf(self.jackTokenizer.identifier())} </index>\n")
            else:
                self.outputFile.write(f"<identifier> {self.jackTokenizer.identifier()} </identifier><type> {self.classSymbolTable.typeOf(self.jackTokenizer.identifier())} </type><kind> {self.classSymbolTable.kindOf(self.jackTokenizer.identifier())} </kind><index> {self.classSymbolTable.indexOf(self.jackTokenizer.identifier())} </index>\n")
            
            self.jackTokenizer.advance()
            self.outputFile.write(f"<symbol> {self.jackTokenizer.symbol()} </symbol>\n")
            self.jackTokenizer.advance()
            self.compileExpression()
            self.outputFile.write(f"<symbol> {self.jackTokenizer.symbol()} </symbol>\n")
        if self.jackTokenizer.tokenType() == "IDENTIFIER" and self.jackTokenizer.result[self.jackTokenizer.current_token + 1] == ".":
            
            kind = self.subSymbolTable.kindOf(self.jackTokenizer.identifier())
            if kind in ["arg", "var"]:
                self.outputFile.write(f"<identifier> {self.jackTokenizer.identifier()} </identifier><type> {self.subSymbolTable.typeOf(self.jackTokenizer.identifier())} </type><kind> {self.subSymbolTable.kindOf(self.jackTokenizer.identifier())} </kind><index> {self.subSymbolTable.indexOf(self.jackTokenizer.identifier())} </index>\n")
            else:
                self.outputFile.write(f"<identifier> {self.jackTokenizer.identifier()} </identifier><type> {self.classSymbolTable.typeOf(self.jackTokenizer.identifier())} </type><kind> {self.classSymbolTable.kindOf(self.jackTokenizer.identifier())} </kind><index> {self.classSymbolTable.indexOf(self.jackTokenizer.identifier())} </index>\n")
            
            self.jackTokenizer.advance()
            self.outputFile.write(f"<symbol> {self.jackTokenizer.symbol()} </symbol>\n")
            self.jackTokenizer.advance()
            
            kind = self.subSymbolTable.kindOf(self.jackTokenizer.identifier())
            if kind in ["arg", "var"]:
                self.outputFile.write(f"<identifier> {self.jackTokenizer.identifier()} </identifier><type> {self.subSymbolTable.typeOf(self.jackTokenizer.identifier())} </type><kind> {self.subSymbolTable.kindOf(self.jackTokenizer.identifier())} </kind><index> {self.subSymbolTable.indexOf(self.jackTokenizer.identifier())} </index>\n")
            else:
                self.outputFile.write(f"<identifier> {self.jackTokenizer.identifier()} </identifier><type> {self.classSymbolTable.typeOf(self.jackTokenizer.identifier())} </type><kind> {self.classSymbolTable.kindOf(self.jackTokenizer.identifier())} </kind><index> {self.classSymbolTable.indexOf(self.jackTokenizer.identifier())} </index>\n")
            
            self.jackTokenizer.advance()
            self.outputFile.write(f"<symbol> {self.jackTokenizer.symbol()} </symbol>\n")
            self.jackTokenizer.advance()
            self.compileExpressionList()
            self.outputFile.write(f"<symbol> {self.jackTokenizer.symbol()} </symbol>\n")
        if self.jackTokenizer.tokenType() == "INT_CONST":
            self.outputFile.write(f"<integerConstant> {self.jackTokenizer.intVal()} </integerConstant>\n")
        if self.jackTokenizer.tokenType() == "STRING_CONST":
            self.outputFile.write(f"<stringConstant> {self.jackTokenizer.stringVal()} </stringConstant>\n")
        elif self.jackTokenizer.tokenType() == "IDENTIFIER":
            
            kind = self.subSymbolTable.kindOf(self.jackTokenizer.identifier())
            if kind in ["arg", "var"]:
                self.outputFile.write(f"<identifier> {self.jackTokenizer.identifier()} </identifier><type> {self.subSymbolTable.typeOf(self.jackTokenizer.identifier())} </type><kind> {self.subSymbolTable.kindOf(self.jackTokenizer.identifier())} </kind><index> {self.subSymbolTable.indexOf(self.jackTokenizer.identifier())} </index>\n")
            else:
                self.outputFile.write(f"<identifier> {self.jackTokenizer.identifier()} </identifier><type> {self.classSymbolTable.typeOf(self.jackTokenizer.identifier())} </type><kind> {self.classSymbolTable.kindOf(self.jackTokenizer.identifier())} </kind><index> {self.classSymbolTable.indexOf(self.jackTokenizer.identifier())} </index>\n")
        
        if self.jackTokenizer.tokenType() == "KEYWORD":
            self.outputFile.write(f"<keyword> {self.jackTokenizer.keyWord()} </keyword>\n")
        if self.jackTokenizer.tokenType() == "SYMBOL" and self.jackTokenizer.symbol() == "(":
            self.outputFile.write(f"<symbol> {self.jackTokenizer.symbol()} </symbol>\n")
            self.jackTokenizer.advance()
            self.compileExpression()
            self.outputFile.write(f"<symbol> {self.jackTokenizer.symbol()} </symbol>\n")
        if self._unaryOp(self.jackTokenizer.symbol()):
            self.outputFile.write(f"<symbol> {self.jackTokenizer.symbol()} </symbol>\n")
            self.jackTokenizer.advance()
            self.compileTerm()
        self.outputFile.write(f"</term>\n")


    def compileExpressionList(self):
        self.outputFile.write(f"<expressionList>\n")
        self.compileExpression()
        # self.outputFile.write(f"<symbol> {self.jackTokenizer.symbol()} </symbol>\n")
        self._checkStarExpression()
        self.outputFile.write(f"</expressionList>\n")
        

if len(sys.argv) != 2:
    sys.exit(1)

directory = sys.argv[1]
# print("directory", directory)
files = [file for file in os.listdir(directory) if file.endswith('.jack')]
directory_name = os.path.basename(os.path.normpath(directory))
directory_path = os.path.join(directory, directory_name)
def main():
    for file_name in files:
        file_name_no_ext = file_name.split(".")[0]
        file_path = os.path.join(directory, file_name)
        filestream = open(directory + f"{file_name_no_ext}" + ".vm","a")
        # compilationEngine.setFileName(file_name)
        
        with open(file_path, 'r') as file:
            text = file.read()
            jackTokenizer = JackTokenizer(text)
            compilationEngine = CompilationEngine(jackTokenizer, filestream)
            print("self.jackTokenizer.current_token:", jackTokenizer.current_token)
            print("self.jackTokenizer.current_instruction:", jackTokenizer.current_instruction)
            print("self.jackTokenizer.current_instruction:", jackTokenizer.current_instruction)
            compilationEngine.compileClass()

if __name__ == "__main__":
    main()