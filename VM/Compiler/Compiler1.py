import sys
import os
import re

class JackTokenizer:
    def __init__(self, text):
        lines = text.split('\n')
        self.cleanLines = []
        for line in lines:
            self.cleanedLine = re.sub(r'//.*$', '', line)
            self.cleanLines.append(self.cleanedLine)

        cleanedText = '\n'.join(self.cleanLines)
        cleanedText = re.sub(r'/\*.*?\*/', '', cleanedText, flags=re.DOTALL)
        
        lexicalElements = ["class", "constructor", "function", "method", "field", "static", "var", "int", "char", "boolean", "void", "true", "false", "null", "this", "let", "do", "if", "else", "while", "return", "{", "}", "(", ")", "[", "]", ".", ",", ";", "+", "-", "*", "/", "&", "|", "<", ">", "=", "~"]
        
        lines = cleanedText.split()
        self.result = []
        inQuotes = False
        temp = ""

        for line in lines:
            for char in line:
                if char.isdigit():
                    temp += char
                else:
                    if temp and temp.isdigit():
                        if 0 <= int(temp) <= 32767:
                            self.result.append(temp)
                        else:
                            print("Integer is not between 0 and 32767.")
                        temp = ""
                    if char == '"':
                        if inQuotes:
                            temp += char
                            print("self.temp:", temp)
                            self.result.append(temp)
                            temp = ""
                            inQuotes = False
                        else:
                            if temp:
                                self.result.append(temp)
                                temp = ""
                            temp += char
                            inQuotes = True
                    elif inQuotes:
                        temp += char
                    elif char in lexicalElements:
                        if temp:
                            self.result.append(temp)
                            temp = ""
                        self.result.append(char)
                    elif char.isspace():
                        if temp:
                            self.result.append(temp)
                            temp = ""
                    else:
                        temp += char
            if temp and temp.isdigit():
                if 0 <= int(temp) <= 32767:
                    self.result.append(temp)
                else:
                    print("Integer is not between 0 and 32767.")
                temp = ""
            elif temp and not inQuotes:
                self.result.append(temp)
                temp = ""
            elif temp and inQuotes:
                temp += ' '



        print("self.result", self.result)

        self.current_token = -1
        self.current_instruction = ""
        self.instruction_type = ""
        self.the_symbol = ""
        self.desti = ""
        self.compu = ""
        self.jumpi = ""

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
        if self.instruction_type == "KEYWORD":
            self.current_instruction = self.current_instruction
            return self.current_instruction
        else:    
            return "Not a keyword."

    def symbol(self):
        if self.instruction_type == "SYMBOL":
            if self.current_instruction == "<":
                return "&lt;"
            if self.current_instruction == ">":
                return "&gt;"
            if self.current_instruction == "&":
                return "&amp;"
            return self.current_instruction
        else:
            return "Not a symbol."
        
    def identifier(self):
        if self.instruction_type == "IDENTIFIER":
            return str(self.current_instruction)

    def intVal(self):
        if self.instruction_type == "INT_CONST":
            return int(self.current_instruction)

    def stringVal(self):
        if self.instruction_type == "STRING_CONST":
            self.current_instruction = self.current_instruction.replace('"', '')
            return str(self.current_instruction)

if len(sys.argv) != 2:
    sys.exit(1)

directory = sys.argv[1]
print("directory", directory)
files = [file for file in os.listdir(directory) if file.endswith('.jack')]
directory_name = os.path.basename(os.path.normpath(directory))
directory_path = os.path.join(directory, directory_name)
def main():
    # codeWriter = CodeWriter(filestream)
    for file_name in files:
        file_name_no_ext = file_name.split(".")[0]
        filestream = open(directory + f"{file_name_no_ext}" + "Tt.xml","a")
        file_path = os.path.join(directory, file_name)
        # codeWriter.setFileName(file_name)
        
        with open(file_path, 'r') as file:
            text = file.read()
            jackTokenizer = JackTokenizer(text)
            filestream.write("<tokens>\n")
            while jackTokenizer.hasMoreTokens():
                jackTokenizer.advance()
                tokenType = jackTokenizer.tokenType()
                if tokenType == "KEYWORD":
                    filestream.write(f"<keyword> {jackTokenizer.keyWord()} </keyword>\n")
                    # codeWriter.writeReturn()
                if tokenType == "SYMBOL":
                    filestream.write(f"<symbol> {jackTokenizer.symbol()} </symbol>\n")
                if tokenType == "INT_CONST":
                    filestream.write(f"<integerConstant> {jackTokenizer.intVal()} </integerConstant>\n")
                if tokenType == "STRING_CONST":
                    filestream.write(f"<stringConstant> {jackTokenizer.stringVal()} </stringConstant>\n")
                if tokenType == "IDENTIFIER":
                    filestream.write(f"<identifier> {jackTokenizer.identifier()} </identifier>\n")
            filestream.write("</tokens>\n")

    # codeWriter.close()

if __name__ == "__main__":
    main()