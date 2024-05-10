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
    
    def commandType(self):
        if self.current_instruction == "add" or self.current_instruction == "sub" or self.current_instruction == "neg" or self.current_instruction == "eq" or self.current_instruction == "gt" or self.current_instruction == "lt" or self.current_instruction == "and" or self.current_instruction == "or" or self.current_instruction == "not":
            self.instruction_type = "C_ARITHMETIC"
            return "C_ARITHMETIC"
        if self.current_instruction.startswith("push"):
            self.instruction_type = "C_PUSH"
            return "C_PUSH"
        if self.current_instruction.startswith("pop"):
            self.instruction_type = "C_POP"
            return "C_POP"
        
    def arg1(self):
        if self.instruction_type == "C_ARITHMETIC":
            return self.current_instruction
        else:    
            arg1Text = self.current_instruction.split()
            # return up to the equals.
            if len(arg1Text) >= 2:
                return str(arg1Text[1])
            else:
                return "Not enough arguments in arithmetic command."

    def arg2(self):
        if self.instruction_type == "C_PUSH" or self.instruction_type == "C_POP":
            arg2Text = self.current_instruction
            if len(arg2Text) >= 3:
                try:
                    return int(arg2Text[2])
                except ValueError:
                    print("The string does not contain a valid integer.")
            else:
                return "Not enough arguments in push/pop command or this is not a push/pop command."

def push():
    pushInstruction = "@SP\nA=M\nM=D\n@SP\nM=M+1"
    return pushInstruction

def pop():
    popInstruction = "@SP\nA=M\nD=M"
    return popInstruction

def pushSegment(number, segment):
    pushSegmentInstruction = f"@{number}\nD=A\n@{segment}\nA=M\nA=D+M\nD=M"
    return pushSegmentInstruction

def popSegment(number, segment):
    popSegmentInstruction = f"@{number}\nD=A\n@{segment}\nD=D+M\n@R13\nM=D"
    return popSegmentInstruction

def pushPointer(segment):
    pushPointerInstruction = f"@{segment}\nA=M\nD=M"
    return pushPointerInstruction

def popPointer(segment):
    popPointerInstruction = f"@{segment}\nA=M\nM=D\n@SP\nM=M-1"
    return popPointerInstruction

def popArithmetic():
    popArithmeticInstruction = "@SP\nA=M\nD=M\n@R13\nM=D\n@SP\nM=M-1\nA=M\nD=M\n@R14\nM=D\n@SP\nM=M-1\n"
    return popArithmeticInstruction

def addSubAndOr(operation):
    addSubAndOrInstruct = f"@R13\nD=M\n@R14\nD={operation}\n@SP\nA=M\nM=D\n@SP\nM=M+1"
    return addSubAndOrInstruct

def eqGtLt(operation):
    eqGtLtInstruct = f"@R13\nD=M\n@R14\nD=D-M\n@END\n{operation}\n@SP\nA=M\nM=0\n@SP\nM=M+1\n(END)\n@SP\nA=M\nM=1\n@SP\nM=M+1"
    return eqGtLtInstruct

def negNot(operation):
    negNotInstruct = f"@SP\nA=M\nD=M\n@SP\nM=M-1\nD={operation}\n@SP\nA=M\nM=D\n@SP\nM=M+1"
    return negNotInstruct

def fin():
    finInstruct = "@FIN\n0;JMP"
    return finInstruct

class CodeWriter:
    def __init__(self, outputFile):
        self.outputFile = outputFile
        self.fs = open(self.outputFile + ".asm","a")

    
    def writeArithmetic(self, command):
        popArith = str(popArithmetic())
        if command == "add":
            addInstruct = "D+M"
            addString = str(addSubAndOr(addInstruct))
            arithmeticAssemblyAdd = popArith + addString
            arithmeticAssemblyAdd = arithmeticAssemblyAdd.splitlines()
            self.fs.write(arithmeticAssemblyAdd + "\n")
        if command == "sub":
            subInstruct = "D-M"
            subString = str(addSubAndOr(subInstruct))
            arithmeticAssemblySub = popArith + subString
            arithmeticAssemblySub = arithmeticAssemblySub.splitlines()
            self.fs.write(arithmeticAssemblySub + "\n")
        if command == "and":
            andInstruct = "D&M"
            andString = addSubAndOr(andInstruct)
            arithmeticAssemblyAnd = popArith + andString
            arithmeticAssemblyAnd = arithmeticAssemblyAnd.splitlines()
            self.fs.write(arithmeticAssemblyAnd + "\n")
        if command == "or":
            orInstruct = "D|M"
            orString = addSubAndOr(orInstruct)
            arithmeticAssemblyOr = popArith + orString
            arithmeticAssemblyOr = arithmeticAssemblyOr.splitlines()
            self.fs.write(arithmeticAssemblyOr + "\n")
        if command == "gt":
            gtInstruct = "D;JGT"
            gtString = eqGtLt(gtInstruct)
            arithmeticAssemblyGt = popArith + gtString
            arithmeticAssemblyGt = arithmeticAssemblyGt.splitlines()
            self.fs.write(arithmeticAssemblyGt + "\n")
        if command == "lt":
            ltInstruct = "D;JLT"
            ltString = eqGtLt(ltInstruct)
            arithmeticAssemblyLt = popArith + ltString
            arithmeticAssemblyLt = arithmeticAssemblyLt.splitlines()
            self.fs.write(arithmeticAssemblyLt + "\n")
        if command == "eq":
            eqInstruct = "D;JEQ"
            eqString = eqGtLt(eqInstruct)
            arithmeticAssemblyEq = popArith + eqString
            arithmeticAssemblyEq = arithmeticAssemblyEq.splitlines()
            self.fs.write(arithmeticAssemblyEq + "\n")


    def writePushPop(self, command, segment, index):
        if command == "C_PUSH" and segment == "local" or segment == "argument" or segment == "this" or segment == "that":

        if command == "C_PUSH" and segment == "pointer":

        if command == "C_POP" and segment == "local" or segment == "argument" or segment == "this" or segment == "that":

        if command == "C_POP" and segment == "pointer":

            
    def close(self):
        self.fs.close()


def main():
    filename = sys.argv[1]
    filenameString = str(filename)
    filenameNoExt = filenameString.split('.')[0]


    with open(filename, 'r') as file:
        text = file.read()
        parser = Parser(text)
        lineNumber = 0

        while parser.hasMoreLines():
            parser.advance()
            commandType = parser.commandType()

            if commandType == ""

            fs = open(filenameNoExt + ".hack","a")
            fs.write(cInstruction + "\n")
            fs.close()

if __name__ == "__main__":
    main()