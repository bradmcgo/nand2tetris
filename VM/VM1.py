import sys
import os

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
        if self.current_instruction.startswith("push "):
            self.instruction_type = "C_PUSH"
            return "C_PUSH"
        if self.current_instruction.startswith("pop "):
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
            arg2Text = self.current_instruction.split()
            if len(arg2Text) >= 3:
                    return int(arg2Text[2])
            else:
                return "Not enough arguments in push/pop command or this is not a push/pop command."

def push():
    pushInstruction = "@SP\nA=M\nM=D\n@SP\nM=M+1"
    return pushInstruction

def pop():
    popInstruction = "@SP\nA=M-1\nD=M\nM=0\n"
    return popInstruction

def pushSegment(number, segment):
    segment_map = {
        "local": "LCL",
        "argument": "ARG",
        "this": "THIS",
        "that": "THAT"
    }
    push_segment_code = segment_map.get(segment, segment)
    pushSegmentInstruction = f"@{number}\nD=A\n@R13\nM=D\n@{push_segment_code}\nD=M\n@R13\nD=D+M\n\nA=D\nD=M\n"
    return pushSegmentInstruction

def popSegment(number, segment):
    segment_map = {
        "local": "LCL",
        "argument": "ARG",
        "this": "THIS",
        "that": "THAT"
    }
    pop_segment_code = segment_map.get(segment, segment)
    popSegmentInstruction = f"@{number}\nD=A\n@{pop_segment_code}\nD=D+M\n@R13\nM=D\n"
    return popSegmentInstruction

def pushPointer(segment):
    pushPointerInstruction = f"@{segment}\nD=M\n"
    return pushPointerInstruction

def popPointer(segment):
    popPointerInstruction = f"@{segment}\nM=D\n@SP\nM=M-1"
    return popPointerInstruction

def popArithmetic():
    popArithmeticInstruction = "@SP\nA=M-1\nD=M\nM=0\n@R13\nM=D\n@SP\nM=M-1\n@SP\nA=M-1\nD=M\nM=0\n@R14\nM=D\n@SP\nM=M-1\n"
    return popArithmeticInstruction

def addSubAndOr(operation):
    addSubAndOrInstruct = f"@R13\nD=M\n@R14\nD={operation}\n@SP\nA=M\nM=D\n@SP\nM=M+1"
    return addSubAndOrInstruct

def eqGtLt(operation):
    if not hasattr(eqGtLt, 'counter'):
        eqGtLt.counter = 0
    eqGtLt.counter += 1
    end_label = f"END{eqGtLt.counter}"
    end_jump_label = f"(END{eqGtLt.counter})"
    done_label = f"DONE{eqGtLt.counter}"
    done_jump_label = f"(DONE{eqGtLt.counter})"
    eqGtLtInstruct = f"@R13\nD=M\n@R14\nD=D-M\n@{end_label}\n{operation}\n@SP\nA=M\nM=0\n@SP\nM=M+1\n@{done_label}\nD;JMP\n{end_jump_label}\n@SP\nA=M\nM=-1\n@SP\nM=M+1\n{done_jump_label}"
    return eqGtLtInstruct

def negNot(operation):
    negNotInstruct = f"@SP\nA=M-1\nD=M\nM=0\n@SP\nM=M-1\nD={operation}\n@SP\nA=M\nM=D\n@SP\nM=M+1"
    return negNotInstruct

def constant(number):
    constantInstruct = f"@{number}\nD=A\n@SP\nA=M\nM=D\n@SP\nM=M+1"
    return constantInstruct

def staticPop(filename, number):
    staticInstruct = f"@SP\nA=M-1\nD=M\nM=0\n@{filename}.{number}\nM=D\n@SP\nM=M-1"
    return staticInstruct

def staticPush(filename, number):
    staticInstruct = f"@{filename}.{number}\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1"
    return staticInstruct

def tempPush(tempPushNum):
    tempPushNumber = str(tempPushNum + 5)
    tempPushInstruct = f"@R{tempPushNumber}\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1"
    return tempPushInstruct

def tempPop(tempPopNum):
    tempPopNumber = str(tempPopNum + 5)
    tempPopInstruct = f"@SP\nA=M-1\nD=M\nM=0\n@R{tempPopNumber}\nM=D\n@SP\nM=M-1"
    return tempPopInstruct

def fin():
    finInstruct = "@FIN\n0;JMP"
    return finInstruct

class CodeWriter:
    def __init__(self, outputFile):
        self.outputFile = outputFile
    
    def writeArithmetic(self, command):
        popArith = str(popArithmetic())
        if command == "add":
            addInstruct = "D+M"
            addString = addSubAndOr(addInstruct)
            arithmeticAssemblyAdd = popArith + addString + "\n"
            arithmeticAssemblyAdd = arithmeticAssemblyAdd.splitlines()
            self.outputFile.write("//" + f"{command} " + "\n")
            self.outputFile.writelines([item + "\n" for item in arithmeticAssemblyAdd])

        if command == "sub":
            subInstruct = "M-D"
            subString = addSubAndOr(subInstruct)
            arithmeticAssemblySub = popArith + subString + "\n"
            arithmeticAssemblySub = arithmeticAssemblySub.splitlines()
            self.outputFile.write("//" + f"{command} " + "\n")
            self.outputFile.writelines([item + "\n" for item in arithmeticAssemblySub])

        if command == "and":
            andInstruct = "D&M"
            andString = addSubAndOr(andInstruct)
            arithmeticAssemblyAnd = popArith + andString + "\n"
            arithmeticAssemblyAnd = arithmeticAssemblyAnd.splitlines()
            self.outputFile.write("//" + f"{command} " + "\n")
            self.outputFile.writelines([item + "\n" for item in arithmeticAssemblyAnd])

        if command == "or":
            orInstruct = "D|M"
            orString = addSubAndOr(orInstruct)
            arithmeticAssemblyOr = popArith + orString + "\n"
            arithmeticAssemblyOr = arithmeticAssemblyOr.splitlines()
            self.outputFile.write("//" + f"{command} " + "\n")
            self.outputFile.writelines([item + "\n" for item in arithmeticAssemblyOr])

        if command == "gt":
            gtInstruct = "D;JLT"
            gtString = eqGtLt(gtInstruct)
            arithmeticAssemblyGt = popArith + gtString + "\n"
            arithmeticAssemblyGt = arithmeticAssemblyGt.splitlines()
            self.outputFile.write("//" + f"{command} " + "\n")
            self.outputFile.writelines([item + "\n" for item in arithmeticAssemblyGt])

        if command == "lt":
            ltInstruct = "D;JGT"
            ltString = eqGtLt(ltInstruct)
            arithmeticAssemblyLt = popArith + ltString + "\n"
            arithmeticAssemblyLt = arithmeticAssemblyLt.splitlines()
            self.outputFile.write("//" + f"{command} " + "\n")
            self.outputFile.writelines([item + "\n" for item in arithmeticAssemblyLt])

        if command == "eq":
            eqInstruct = "D;JEQ"
            eqString = eqGtLt(eqInstruct)
            arithmeticAssemblyEq = popArith + eqString + "\n"
            arithmeticAssemblyEq = arithmeticAssemblyEq.splitlines()
            self.outputFile.write("//" + f"{command} " + "\n")
            self.outputFile.writelines([item + "\n" for item in arithmeticAssemblyEq])

        if command == "neg":
            negInstruct = "-D"
            negString = negNot(negInstruct)
            arithmeticAssemblyNeg = negString + "\n"
            arithmeticAssemblyNeg = arithmeticAssemblyNeg.splitlines()
            self.outputFile.write("//" + f"{command} " + "\n")
            self.outputFile.writelines([item + "\n" for item in arithmeticAssemblyNeg])

        if command == "not":
            notInstruct = "!D"
            notString = negNot(notInstruct)
            arithmeticAssemblyNot = notString + "\n"
            arithmeticAssemblyNot = arithmeticAssemblyNot.splitlines()
            self.outputFile.write("//" + f"{command} " + "\n")
            self.outputFile.writelines([item + "\n" for item in arithmeticAssemblyNot])


    def writePushPop(self, command, segment, index):
        if command == "C_PUSH" and segment == "local" or command == "C_PUSH" and segment == "argument" or command == "C_PUSH" and segment == "this" or command == "C_PUSH" and segment == "that":
            pushSegInstruct = pushSegment(index, segment)
            pushInstruct = push()
            pushSegmentInstruct = pushSegInstruct + pushInstruct + "\n"
            pushSegmentInstruct = pushSegmentInstruct.splitlines()
            self.outputFile.write("//push " + f"{segment} " + f"{index} " + "\n")
            self.outputFile.writelines([item + "\n" for item in pushSegmentInstruct])

        if command == "C_POP" and segment == "local" or command == "C_POP" and segment == "argument" or command == "C_POP" and segment == "this" or command == "C_POP" and segment == "that":
            popSegInstruct = popSegment(index, segment)
            popInstruct = pop()
            continuedInstruct = "@R13\nA=M\nM=D\n@SP\nM=M-1"
            popSegmentInstruct = popSegInstruct + popInstruct + continuedInstruct + "\n"
            popSegmentInstruct = popSegmentInstruct.splitlines()
            self.outputFile.write("//pop " + f"{segment} " + f"{index} " + "\n")
            self.outputFile.writelines([item + "\n" for item in popSegmentInstruct])

        if command == "C_PUSH" and segment == "pointer" and index == 0:
            pushPointInstruct = pushPointer("THIS")
            pushInstr = push()
            pushPointerInstruct = pushPointInstruct + pushInstr + "\n"
            pushPointerInstruct = pushPointerInstruct.splitlines()
            self.outputFile.write("//push " + f"{segment} " + f"{index} " + "\n")
            self.outputFile.writelines([item + "\n" for item in pushPointerInstruct])

        if command == "C_PUSH" and segment == "pointer" and index == 1:
            pushPointInstruct = pushPointer("THAT")
            pushInstr = push()
            pushPointerInstruct = pushPointInstruct + pushInstr + "\n"
            pushPointerInstruct = pushPointerInstruct.splitlines()
            self.outputFile.write("//push " + f"{segment} " + f"{index} " + "\n")
            self.outputFile.writelines([item + "\n" for item in pushPointerInstruct])

        if command == "C_POP" and segment == "pointer" and index == 0:
            popInstr = pop()
            popPointInstruct = popPointer("THIS")
            popPointerInstruct = popInstr + popPointInstruct + "\n"
            popPointerInstruct = popPointerInstruct.splitlines()
            self.outputFile.write("//pop " + f"{segment} " + f"{index} " + "\n")
            self.outputFile.writelines([item + "\n" for item in popPointerInstruct])

        if command == "C_POP" and segment == "pointer" and index == 1:
            popInstr = pop()
            popPointInstruct = popPointer("THAT")
            popPointerInstruct = popInstr + popPointInstruct + "\n"
            popPointerInstruct = popPointerInstruct.splitlines()
            self.outputFile.write("//pop " + f"{segment} " + f"{index} " + "\n")
            self.outputFile.writelines([item + "\n" for item in popPointerInstruct])

        if command == "C_PUSH" and segment == "constant":
            pushConstInstruct = constant(index)
            pushConstantInstruct = pushConstInstruct + "\n"
            pushConstantInstruct = pushConstantInstruct.splitlines()
            self.outputFile.write("//push " + f"{segment} " + f"{index} " + "\n")
            self.outputFile.writelines([item + "\n" for item in pushConstantInstruct])

        if command == "C_PUSH" and segment == "static":
            popStatInstruct = staticPush(filenameNoPath, index)
            popStaticInstruct = popStatInstruct + "\n"
            popStaticInstruct = popStaticInstruct.splitlines()
            self.outputFile.write("//push " + f"{segment} " + f"{index} " + "\n")
            self.outputFile.writelines([item + "\n" for item in popStaticInstruct])

        if command == "C_POP" and segment == "static":
            pushStatInstruct = staticPop(filenameNoPath, index)
            pushStaticInstruct = pushStatInstruct + "\n"
            pushStaticInstruct = pushStaticInstruct.splitlines()
            self.outputFile.write("//push " + f"{segment} " + f"{index} " + "\n")
            self.outputFile.writelines([item + "\n" for item in pushStaticInstruct])

        if command == "C_PUSH" and segment == "temp":
            tempPushInstruct = tempPush(index)
            tempPushInstruct = tempPushInstruct.splitlines()
            self.outputFile.write("//push " + f"{segment} " + f"{index} " + "\n")
            self.outputFile.writelines([item + "\n" for item in tempPushInstruct])
        
        if command == "C_POP" and segment == "temp":
            tempPopInstruct = tempPop(index)
            tempPopInstruct = tempPopInstruct.splitlines()
            self.outputFile.write("//pop " + f"{segment} " + f"{index} " + "\n")
            self.outputFile.writelines([item + "\n" for item in tempPopInstruct])

    def close(self):
        infiniteLoopInstruct = "(FIN)\n@FIN\n0;JMP"
        infiniteLoopInstruct = infiniteLoopInstruct.splitlines()
        self.outputFile.writelines([item + "\n" for item in infiniteLoopInstruct])
        self.outputFile.close()

filename = sys.argv[1]
filenameString = str(filename)
filenameNoExt = filenameString.split('.')[0]
filenameNoPath = os.path.basename(filenameString)
filenameNoPath = os.path.splitext(filenameNoPath)[0]
fs = open(filenameNoExt + ".asm","a")

def main():
    codeWriter = CodeWriter(fs)

    with open(filename, 'r') as file:
        text = file.read()
        parser = Parser(text)

        while parser.hasMoreLines():
            parser.advance()
            commandType = parser.commandType()
            if commandType == "C_ARITHMETIC":
                codeWriter.writeArithmetic(parser.arg1())
            
            if commandType == "C_PUSH":
                codeWriter.writePushPop("C_PUSH", parser.arg1(), parser.arg2())

            if commandType == "C_POP":
                codeWriter.writePushPop("C_POP", parser.arg1(), parser.arg2())

        codeWriter.close()

if __name__ == "__main__":
    main()