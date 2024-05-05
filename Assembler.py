import sys

class Parser:
    def __init__(self, text):
        self.lines = text.split('\n')
        self.current_line = 0
        self.current_instruction = ""
        self.instruction_type = ""
        self.the_symbol = ""
        self.desti = ""
        self.compu = ""
        self.jumpi = ""
    
    def reset(self):
        self.current_line = 0
        self.current_instruction = ""
        self.instruction_type = ""
        self.the_symbol = ""
        self.desti = ""
        self.compu = ""
        self.jumpi = ""

    def hasMoreLines(self):
        if self.current_line < len(self.lines):
            return True
        return False
    
    def advance(self):
        self.current_line += 1
        if self.hasMoreLines():
            readLine = self.lines[self.current_line]
            self.current_instruction = ""
            if readLine == "" or readLine.startswith("//"):
                pass
            else:
                self.current_instruction = readLine
            return True
        return False
    
    def instructionType(self):
        if self.current_instruction.startswith("@"):
            self.instruction_type = "A_INSTRUCTION"
            return "A_INSTRUCTION"
        if self.current_instruction.startswith("D") or self.current_instruction.startswith("M") or self.current_instruction.startswith("A") or self.current_instruction.startswith("0"):
            self.instruction_type = "C_INSTRUCTION"
            return "C_INSTRUCTION"
        if self.current_instruction.startswith("("):
            self.instruction_type = "L_INSTRUCTION"
            return "L_INSTRUCTION"
    
    def symbol(self):
        if self.instruction_type == "L_INSTRUCTION":
            returnSymbolNoParenthesis = self.lines[self.current_line].replace('(', '').replace(')', '').replace(' ', '')
            self.the_symbol = returnSymbolNoParenthesis
            return returnSymbolNoParenthesis
        if self.instruction_type == "A_INSTRUCTION":
            returnSymbolNoAt = str(self.lines[self.current_line].replace('@', '').replace(' ', ''))
            self.the_symbol = returnSymbolNoAt
            return returnSymbolNoAt
    
    def dest(self):
        if self.instruction_type == "C_INSTRUCTION":
            # return up to the equals.
            destText = self.current_instruction
            if "=" in destText:
                destSplit = destText.split("=")[0]
                self.desti = destSplit
                return destSplit
            else:
                return "None"
    
    def comp(self):
        if self.instruction_type == "C_INSTRUCTION":
            compText = self.current_instruction
            if ';' in compText:
                output_string = compText.split(';')[0]
                self.compu = output_string
                return output_string
            elif '=' in compText:
                output_string = compText.split('=')[1]
                self.compu = output_string
                return output_string
            else:
                return None
    
    def jump(self):
        if self.instruction_type == "C_INSTRUCTION":
            # return after the semicolon.
            jumpText = self.current_instruction
            separator = ";"
            if separator in jumpText:
                jump_parts = jumpText.split(separator)
                if len(jump_parts) > 1:
                    jump_after_separator = jump_parts[1]
                    self.jumpi = jump_after_separator
                    return jump_after_separator
                else:
                    return None
            else:
                print("No jump instruction or separator not found.")
                return "None"
            
class CodeModule:
    def __init__(self, value):
        self.value = value

    def dest(self):
        if self.value == "None":
            return "000"
        if self.value == "M":
            return "001"
        if self.value == "D":
            return "010"
        if self.value == "DM":
            return "011"
        if self.value == "MD":
            return "011"
        if self.value == "A":
            return "100"
        if self.value == "AM":
            return "101"
        if self.value == "AD":
            return "110"
        if self.value == "ADM":
            return "111"
    
    def comp(self):
        if self.value == "0":
            return "0101010"
        if self.value == "1":
            return "0111111"
        if self.value == "-1":
            return "0111010"
        if self.value == "D":
            return "0001100"
        if self.value == "A":
            return "0110000"
        if self.value == "M":
            return "1110000"
        if self.value == "!D":
            return "0001101"
        if self.value == "!A":
            return "0110001"
        if self.value == "!M":
            return "1110001"
        if self.value == "-D":
            return "0001111"
        if self.value == "-A":
            return "0110011"
        if self.value == "-M":
            return "1110011"
        if self.value == "D+1":
            return "0011111"
        if self.value == "A+1":
            return "0110111"
        if self.value == "M+1":
            return "1110111"
        if self.value == "D-1":
            return "0001110"
        if self.value == "A-1":
            return "0110010"
        if self.value == "M-1":
            return "1110010"
        if self.value == "D+A":
            return "0000010"
        if self.value == "D+M":
            return "1000010"
        if self.value == "D-A":
            return "0010011"
        if self.value == "D-M":
            return "1010011"
        if self.value == "A-D":
            return "0000111"
        if self.value == "M-D":
            return "1000111"
        if self.value == "D&A":
            return "0000000"
        if self.value == "D&M":
            return "1000000"
        if self.value == "D|A":
            return "0010101"
        if self.value == "D|M":
            return "1010101"
        
    def jump(self):
        if self.value == "None":
            return "000"
        if self.value == "JGT":
            return "001"
        if self.value == "JEQ":
            return "010"
        if self.value == "JGE":
            return "011"
        if self.value == "JLT":
            return "100"
        if self.value == "JNE":
            return "101"
        if self.value == "JLE":
            return "110"
        if self.value == "JMP":
            return "111"
        
class SymbolTable:
    def __init__(self):
        initial_symbols = {
        'R0': 0,
        'R1': 1,
        'R2': 2,
        'R3': 3,
        'R4': 4,
        'R5': 5,
        'R6': 6,
        'R7': 7,
        'R8': 8,
        'R9': 9,
        'R10': 10,
        'R11': 11,
        'R12': 12,
        'R13': 13,
        'R14': 14,
        'R15': 15,
        'SP': 0,
        'LCL': 1,
        'ARG': 2,
        'THIS': 3,
        'THAT': 4,
        'SCREEN': 16384,
        'KBD': 24576
    }
        self.table = initial_symbols if initial_symbols is not None else dict()

    def addEntry(self, symbol, address):
        self.table[symbol] = address
    
    def contains(self, symbol):
        if symbol in self.table:
            return True
        else:
            return False

    def getAddress(self, symbol):
        if symbol in self.table:
            return self.table[symbol]
        else:
            return "Symbol not found in symbol table."

def main():
    filename = sys.argv[1]
    filenameString = str(filename)
    filenameNoExt = filenameString.split('.')[0]
    symbolTable = SymbolTable()

    # first pass
    with open(filename, 'r') as file:
        text = file.read()
        parser1 = Parser(text)
        lineNumber = 0

        while parser1.hasMoreLines():
            parser1.advance()
            instructionType1 = parser1.instructionType()

            if instructionType1 == "A_INSTRUCTION" or instructionType1 == "C_INSTRUCTION":
                lineNumber += 1
            else:
                pass

            if instructionType1 == "L_INSTRUCTION":
                parserSymbolLInstruct = parser1.symbol()
                nextAddressValue = lineNumber
                symbolTable.addEntry(parserSymbolLInstruct, nextAddressValue)
            else:
                pass

    # second pass
    with open(filename, 'r') as file2:
        text2 = file2.read()
        parser2 = Parser(text2)
        reservedAddresses = 16

        while parser2.hasMoreLines():
            parser2.advance()
            instructionType2 = parser2.instructionType()
            def number_string_to_15bit_binary(value):
                num = int(value)
                if num < 0 or num > 32767:
                    raise ValueError("The number is out of the 15-bit range.")
                binary_value = format(num, '015b')
                return binary_value

            if instructionType2 == "A_INSTRUCTION":
                parserSymbolAInstruct = parser2.symbol()
                if not parserSymbolAInstruct[0].isdigit():
                    if symbolTable.contains(parserSymbolAInstruct):
                        symbolAInstructAddress = symbolTable.getAddress(parserSymbolAInstruct)
                        aSymbolInstruction = "0" + number_string_to_15bit_binary(symbolAInstructAddress)
                        # append to next line in output file. create output file first?
                        hs = open(filenameNoExt + ".hack","a")
                        hs.write(aSymbolInstruction + "\n")
                        hs.close()
                    else:
                        # add symbol to symbol table starting at address 16.
                        symbolTable.addEntry(parserSymbolAInstruct, reservedAddresses)
                        symbolAInstructAddress = symbolTable.getAddress(parserSymbolAInstruct)
                        aSymbolInstruction = "0" + number_string_to_15bit_binary(symbolAInstructAddress)
                        reservedAddresses += 1
                        # append to next line in output file. create output file first?
                        hs = open(filenameNoExt + ".hack","a")
                        hs.write(aSymbolInstruction + "\n")
                        hs.close()

                else:
                    def number_string_to_15bit_binary(value):
                        num = int(value)
                        if num < 0 or num > 32767:
                            raise ValueError("The number is out of the 15-bit range.")
                        binary_value = format(num, '015b')
                        return binary_value
                    aInstruction = "0" + number_string_to_15bit_binary(parserSymbolAInstruct)
                    # append to next line in output file. create output file first?
                    hs = open(filenameNoExt + ".hack","a")
                    hs.write(aInstruction + "\n")
                    hs.close()

            if instructionType2 == "C_INSTRUCTION":
                destParse = parser2.dest()
                compParse = parser2.comp()
                jumpParse = parser2.jump()

                # call CodeModule methods to translate dest, comp, and jump into binary representations.
                codeModuleDest = CodeModule(destParse)
                codeModuleComp = CodeModule(compParse)
                codeModuleJump = CodeModule(jumpParse)

                destTranslation = str(codeModuleDest.dest())
                compTranslation = str(codeModuleComp.comp())
                jumpTranslation = str(codeModuleJump.jump())
                # concatenate binary representations.
                cInstruction = "111" + compTranslation + destTranslation + jumpTranslation
                # append to next line in output file. create output file first?
                fs = open(filenameNoExt + ".hack","a")
                fs.write(cInstruction + "\n")
                fs.close()

if __name__ == "__main__":
    main()