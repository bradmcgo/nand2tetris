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
            readLine = readLine.lstrip()
            readLine = readLine.split('//')[0]
            self.current_instruction = ""
            if readLine == "" or readLine.startswith("//"):
                pass
            else:
                self.current_instruction = readLine
            return True
        return False
    
    def commandType(self):
        if self.current_instruction.startswith("add") or self.current_instruction.startswith("sub") or self.current_instruction.startswith("neg") or self.current_instruction.startswith("eq") or self.current_instruction.startswith("gt") or self.current_instruction.startswith("lt") or self.current_instruction.startswith("and") or self.current_instruction.startswith("or") or self.current_instruction.startswith("not"):
            self.instruction_type = "C_ARITHMETIC"
            return "C_ARITHMETIC"
        if self.current_instruction.startswith("push "):
            self.instruction_type = "C_PUSH"
            return "C_PUSH"
        if self.current_instruction.startswith("pop "):
            self.instruction_type = "C_POP"
            return "C_POP"
        if self.current_instruction.startswith("label "):
            self.instruction_type = "C_LABEL"
            return "C_LABEL"
        if self.current_instruction.startswith("goto "):
            self.instruction_type = "C_GOTO"
            return "C_GOTO"
        if self.current_instruction.startswith("if-goto "):
            self.instruction_type = "C_IF"
            return "C_IF"
        if self.current_instruction.startswith("function "):
            self.instruction_type = "C_FUNCTION"
            return "C_FUNCTION"
        if self.current_instruction.startswith("return"):
            self.instruction_type = "C_RETURN"
            return "C_RETURN"
        if self.current_instruction.startswith("call "):
            self.instruction_type = "C_CALL"
            return "C_CALL"
        
    def arg1(self):
        if self.instruction_type == "C_ARITHMETIC":
            return self.current_instruction
        else:    
            arg1Text = self.current_instruction.split()
            if len(arg1Text) >= 2:
                return str(arg1Text[1])
            else:
                return "Not enough arguments in arithmetic command."

    def arg2(self):
        if self.instruction_type == "C_PUSH" or self.instruction_type == "C_POP" or self.instruction_type == "C_FUNCTION" or self.instruction_type == "C_CALL":
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

def labelLabel(functionName, label):
    if functionName:
        labelInstruct = f"({functionName}${label})"
    else:
        labelInstruct = f"({label})"
    return labelInstruct

def gotoLabel(functionName, label):
    if functionName:
        gotoLabelInsruct = f"@{functionName}${label}\nD;JMP"
    else:
        gotoLabelInsruct = f"@{label}\nD;JMP"
    return gotoLabelInsruct

def ifGotoLabel(functionName, label):
    if functionName:
        ifGotoLabelInstruct = f"@SP\nA=M-1\nD=M\nM=0\n@SP\nM=M-1\n@{functionName}${label}\nD;JNE"
    else:
        ifGotoLabelInstruct = f"@SP\nA=M-1\nD=M\nM=0\n@SP\nM=M-1\n@{label}\nD;JNE"
    return ifGotoLabelInstruct


def functionInstruct(functionName, nVars, loopCounter, stopCounter):
    functInstruct = f"({functionName})\n@{nVars}\nD=A\n@R14\nM=D\n@R13\nM=0\n(LOOP{loopCounter})\n@R14\nD=M\n@R13\nD=D-M\n@STOP{stopCounter}\nD;JEQ\n@R13\n\nM=M+1\n@SP\nA=M\nM=0\n@SP\nM=M+1\n@LOOP{loopCounter}\nD;JMP\n(STOP{stopCounter})\n"
    return functInstruct

def callInstruct(functionName, nArgs, callCounter):
    returnAddress = f"{functionName}$ret.{callCounter}"
    pushRetAddr = f"@{returnAddress}\nD=A\n@SP\nA=M\nM=D\n@SP\nM=M+1\n"
    pushLCL = "@LCL\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n"
    pushARG = "@ARG\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n"
    pushTHIS = "@THIS\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n"
    pushTHAT = "@THAT\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n"
    popARG = f"@SP\nD=M\n@5\nD=D-A\n@{nArgs}\nD=D-A\n@ARG\nM=D\n"
    popLCL = "@SP\nD=M\n@LCL\nM=D\n"
    gotoF = f"@{functionName}\nD;JMP\n"
    label = f"({functionName}$ret.{callCounter})\n"
    callInstr = pushRetAddr + pushLCL + pushARG + pushTHIS + pushTHAT + popARG + popLCL + gotoF + label
    return callInstr

def returnInstruct():
    frame = "LCL"
    retAddr = f"@{frame}\nD=M\n@5\nD=D-A\nA=D\nD=M\n@R15\nM=D\n"
    selARGPop = "@SP\nA=M-1\nD=M\nM=0\n@ARG\nA=M\nM=D\n@SP\nM=M-1\n"
    spEqARG = "@ARG\nD=M\n@1\nD=D+A\n@SP\nM=D\n"
    popTHAT = f"@{frame}\nD=M\n@1\nD=D-A\nA=D\nD=M\n@THAT\nM=D\n"
    popTHIS = f"@{frame}\nD=M\n@2\nD=D-A\nA=D\nD=M\n@THIS\nM=D\n"
    popARG = f"@{frame}\nD=M\n@3\nD=D-A\nA=D\nD=M\n@ARG\nM=D\n"
    popLCL = f"@{frame}\nD=M\n@4\nD=D-A\nA=D\nD=M\n@LCL\nM=D\n"
    gotoRetAddr = "@R15\nA=M\nD;JMP\n"
    retInstruct = retAddr + selARGPop + spEqARG + popTHAT + popTHIS + popARG + popLCL + gotoRetAddr
    return retInstruct

def bootstrap(callCounter):
    bootstrapSP = "@256\nD=A\n@SP\nM=D\n"
    bootstrapCall = callInstruct("Sys.init", 0, callCounter)
    bootstrapInstruct = bootstrapSP + bootstrapCall
    return bootstrapInstruct

def fin():
    finInstruct = "@FIN\n0;JMP"
    return finInstruct

class CodeWriter:
    def __init__(self, outputFile):
        self.outputFile = outputFile
        self.filename = ""
        self.functionName = ""
        self.functionLoopLabelCounter = 0
        self.stopCounter = 0
        self.callCounter = 1

        bootstrapInstruct = bootstrap(self.callCounter)
        bootstrapInstruct = bootstrapInstruct.splitlines()
        self.outputFile.write("//bootstrap instructions\n")
        self.outputFile.writelines([item + "\n" for item in bootstrapInstruct])
    
    def writeArithmetic(self, command):
        popArith = str(popArithmetic())
        if command.startswith("add"):
            addInstruct = "D+M"
            addString = addSubAndOr(addInstruct)
            arithmeticAssemblyAdd = popArith + addString + "\n"
            arithmeticAssemblyAdd = arithmeticAssemblyAdd.splitlines()
            self.outputFile.write("//" + f"{command} " + "\n")
            self.outputFile.writelines([item + "\n" for item in arithmeticAssemblyAdd])

        if command.startswith("sub"):
            subInstruct = "M-D"
            subString = addSubAndOr(subInstruct)
            arithmeticAssemblySub = popArith + subString + "\n"
            arithmeticAssemblySub = arithmeticAssemblySub.splitlines()
            self.outputFile.write("//" + f"{command} " + "\n")
            self.outputFile.writelines([item + "\n" for item in arithmeticAssemblySub])

        if command.startswith("and"):
            andInstruct = "D&M"
            andString = addSubAndOr(andInstruct)
            arithmeticAssemblyAnd = popArith + andString + "\n"
            arithmeticAssemblyAnd = arithmeticAssemblyAnd.splitlines()
            self.outputFile.write("//" + f"{command} " + "\n")
            self.outputFile.writelines([item + "\n" for item in arithmeticAssemblyAnd])

        if command.startswith("or"):
            orInstruct = "D|M"
            orString = addSubAndOr(orInstruct)
            arithmeticAssemblyOr = popArith + orString + "\n"
            arithmeticAssemblyOr = arithmeticAssemblyOr.splitlines()
            self.outputFile.write("//" + f"{command} " + "\n")
            self.outputFile.writelines([item + "\n" for item in arithmeticAssemblyOr])

        if command.startswith("gt"):
            gtInstruct = "D;JLT"
            gtString = eqGtLt(gtInstruct)
            arithmeticAssemblyGt = popArith + gtString + "\n"
            arithmeticAssemblyGt = arithmeticAssemblyGt.splitlines()
            self.outputFile.write("//" + f"{command} " + "\n")
            self.outputFile.writelines([item + "\n" for item in arithmeticAssemblyGt])

        if command.startswith("lt"):
            ltInstruct = "D;JGT"
            ltString = eqGtLt(ltInstruct)
            arithmeticAssemblyLt = popArith + ltString + "\n"
            arithmeticAssemblyLt = arithmeticAssemblyLt.splitlines()
            self.outputFile.write("//" + f"{command} " + "\n")
            self.outputFile.writelines([item + "\n" for item in arithmeticAssemblyLt])

        if command.startswith("eq"):
            eqInstruct = "D;JEQ"
            eqString = eqGtLt(eqInstruct)
            arithmeticAssemblyEq = popArith + eqString + "\n"
            arithmeticAssemblyEq = arithmeticAssemblyEq.splitlines()
            self.outputFile.write("//" + f"{command} " + "\n")
            self.outputFile.writelines([item + "\n" for item in arithmeticAssemblyEq])

        if command.startswith("neg"):
            negInstruct = "-D"
            negString = negNot(negInstruct)
            arithmeticAssemblyNeg = negString + "\n"
            arithmeticAssemblyNeg = arithmeticAssemblyNeg.splitlines()
            self.outputFile.write("//" + f"{command} " + "\n")
            self.outputFile.writelines([item + "\n" for item in arithmeticAssemblyNeg])

        if command.startswith("not"):
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
            popStatInstruct = staticPush(self.filename, index)
            popStaticInstruct = popStatInstruct + "\n"
            popStaticInstruct = popStaticInstruct.splitlines()
            self.outputFile.write("//push " + f"{segment} " + f"{index} " + "\n")
            self.outputFile.writelines([item + "\n" for item in popStaticInstruct])

        if command == "C_POP" and segment == "static":
            pushStatInstruct = staticPop(self.filename, index)
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

    def setFileName(self, filename):
        self.filename = filename
        self.outputFile.write("\n//new file started\n")

    def writeLabel(self, label):
        functionName = self.functionName
        writeLabelInstruct = labelLabel(functionName, label)
        writeLabelInstruct = writeLabelInstruct.splitlines()
        self.outputFile.write(f"//label {label}\n")
        self.outputFile.writelines([item + "\n" for item in writeLabelInstruct])

    def writeGoto(self, label):
        functionName = self.functionName
        writeGotoInstruct = gotoLabel(functionName, label)
        writeGotoInstruct = writeGotoInstruct.splitlines()
        self.outputFile.write(f"//goto {label}\n")
        self.outputFile.writelines([item + "\n" for item in writeGotoInstruct])

    def writeIf(self, label):
        functionName = self.functionName
        writeIfInstruct = ifGotoLabel(functionName, label)
        writeIfInstruct = writeIfInstruct.splitlines()
        self.outputFile.write(f"//if-goto {label}\n")
        self.outputFile.writelines([item + "\n" for item in writeIfInstruct])

    def writeFunction(self, functionName, nVars):
        self.functionLoopLabelCounter += 1
        self.stopCounter += 1
        writeFuncInstruct = functionInstruct(functionName, nVars, self.functionLoopLabelCounter, self.stopCounter)
        writeFuncInstruct = writeFuncInstruct.splitlines()
        self.outputFile.write(f"//function {functionName}\n")
        self.outputFile.writelines([item + "\n" for item in writeFuncInstruct])

    def writeCall(self, functionName, nArgs):
        self.callCounter += 1
        writeCallInstruct = callInstruct(functionName, nArgs, self.callCounter)
        writeCallInstruct = writeCallInstruct.splitlines()
        self.outputFile.write(f"//call {functionName}\n")
        self.outputFile.writelines([item + "\n" for item in writeCallInstruct])

    def writeReturn(self):
        writeReturnInstruct = returnInstruct()
        writeReturnInstruct = writeReturnInstruct.splitlines()
        self.outputFile.write(f"//return\n")
        self.outputFile.writelines([item + "\n" for item in writeReturnInstruct])

    def close(self):
        print("Closed.")
        infiniteLoopInstruct = "(FIN)\n@FIN\n0;JMP"
        infiniteLoopInstruct = infiniteLoopInstruct.splitlines()
        self.outputFile.writelines([item + "\n" for item in infiniteLoopInstruct])
        self.outputFile.close()

if len(sys.argv) != 2:
    sys.exit(1)

directory = sys.argv[1]
files = [file for file in os.listdir(directory) if file.endswith('.vm')]
files = sorted(files, key=lambda x: (os.path.basename(x) != 'Sys.vm', x))
directory_name = os.path.basename(os.path.normpath(directory))
directory_path = os.path.join(directory, directory_name)
filestream = open(directory_path + ".asm","a")

def main():
    codeWriter = CodeWriter(filestream)

    for file_name in files:
        file_path = os.path.join(directory, file_name)
        codeWriter.setFileName(file_name)
        
        with open(file_path, 'r') as file:
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

                if commandType == "C_LABEL":
                    codeWriter.writeLabel(parser.arg1())

                if commandType == "C_GOTO":
                    codeWriter.writeGoto(parser.arg1())

                if commandType == "C_IF":
                    codeWriter.writeIf(parser.arg1())

                if commandType == "C_FUNCTION":
                    codeWriter.writeFunction(parser.arg1(), parser.arg2())

                if commandType == "C_CALL":
                    codeWriter.writeCall(parser.arg1(), parser.arg2())
                
                if commandType == "C_RETURN":
                    codeWriter.writeReturn()

    codeWriter.close()

if __name__ == "__main__":
    main()