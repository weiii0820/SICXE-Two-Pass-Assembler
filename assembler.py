op_table = [
    {"NAME" : "CLEAR", "FORMAT" : 2, "OPCODE" : "B4"},
    {"NAME" : "COMP",  "FORMAT" : 3, "OPCODE" : "28"},
    {"NAME" : "COMPR", "FORMAT" : 2, "OPCODE" : "A0"},
    {"NAME" : "J",     "FORMAT" : 3, "OPCODE" : "3C"},
    {"NAME" : "JEQ",   "FORMAT" : 3, "OPCODE" : "30"},
    {"NAME" : "JLT",   "FORMAT" : 3, "OPCODE" : "38"},
    {"NAME" : "JSUB",  "FORMAT" : 3, "OPCODE" : "48"},
    {"NAME" : "LDA",   "FORMAT" : 3, "OPCODE" : "00"},
    {"NAME" : "LDB",   "FORMAT" : 3, "OPCODE" : "68"},
    {"NAME" : "LDCH",  "FORMAT" : 3, "OPCODE" : "50"},
    {"NAME" : "LDT",   "FORMAT" : 3, "OPCODE" : "74"},
    {"NAME" : "STA",   "FORMAT" : 3, "OPCODE" : "0C"},
    {"NAME" : "STCH",  "FORMAT" : 3, "OPCODE" : "54"},
    {"NAME" : "STL",   "FORMAT" : 3, "OPCODE" : "14"},
    {"NAME" : "STX",   "FORMAT" : 3, "OPCODE" : "10"},
    {"NAME" : "TD",    "FORMAT" : 3, "OPCODE" : "E0"},
    {"NAME" : "TIX",   "FORMAT" : 3, "OPCODE" : "2C"},
    {"NAME" : "TIXR",  "FORMAT" : 2, "OPCODE" : "B8"},
    {"NAME" : "WD",    "FORMAT" : 3, "OPCODE" : "DC"},
    {"NAME" : "RD",    "FORMAT" : 3, "OPCODE" : "D8"},
    {"NAME" : "RSUB",  "FORMAT" : 3, "OPCODE" : "4C"}
]

register_table = {
    "A" : "0",
    "X" : "1",
    "L" : "2",
    "PC": "8",
    "SW": "9",
    "B" : "3",
    "S" : "4",
    "T" : "5",
    "F" : "6"
}

file_path = input("Please enter the file: ")
try:
    open(file_path, "r")
except FileNotFoundError:
    print(f"Error: The file '{file_path}' was not found.")
    exit(1)
except PermissionError:
    print(f"Error: Permission denied when trying to read '{file_path}'.")
    exit(1)
except Exception as e:
    print(f"An unexpected error occurred: {e}")
    exit(1)

file = open(file_path, "r")
code_name = ""
code_start_address = 0
code_end_address = 0
now_address = 0
symbol_table = []
op_list = [] 
base_label = "" 
end_label = ""

#pass 1
#find the "START"
for line in file:
    ori_element = line.split()
    element = line.upper().split() #把每一行的字串全部換成大寫，方便尋找
    if "START" in element:
        code_name = ori_element[0]
        code_start_address = int(element[2])
        now_address = code_start_address
        break
    else:
        print("START can't found")
        exit(1)

#將檔案指標移動到開頭來重新讀取
file.seek(0)

for line in file:
    ori_element = line.split()
    element = line.upper().split()
    #建立一個set來存放所有label，用來判斷有沒有重複
    symbol_set = {label["SYMBOL"] for label in symbol_table if "SYMBOL" in label} 

    #判斷assembler在讀到不同directive的處理方式
    if "BYTE" in element:
        #判斷如果BYTE前面沒有符號名稱
        if len(element) < 3 or element[0] == "BYTE":
            print("Error: Missing symbol before BYTE.")
            exit(1)
        symbol_name = element[0]

        #如果BYTE是字串的處理方式
        if element[2][0] == "C":
            str = ori_element[2][2:-1]
            ascii_str = ''.join([hex(ord(char))[2:].zfill(2).upper() for char in str])  #將字串轉換成十六進位的ascii碼並重新結合成一個新的字串
            if element[0] in symbol_set:
                print("Symbol has already existed")
                exit(1)
        
            symbol_table.append({"SYMBOL" : element[0], "ADDRESS" : now_address})
            op_list.append({"TEXT" : ascii_str, "FORMAT" : 0})
            now_address += len(str)
        
        #如果BYTE是十六進位整數的處理方式
        elif element[2][0] == "X":
            byte_hex = ori_element[2][2:-1]
            if element[0] in symbol_set:
                print("Symbol has already existed")
                exit(1)

            symbol_table.append({"SYMBOL" : element[0], "ADDRESS" : now_address})
            op_list.append({"TEXT" : byte_hex, "FORMAT" : 0})
            now_address += 1
        
        #如果BYTE是一般整數的處理方式
        else:
            if element[0] in symbol_set:
                print("Symbol has already existed")
                exit(1)
            
            try:
                byte_int = int(element[2])
            except ValueError:
                print("Error: Invalid value for BYTE.")
                exit(1)

            symbol_table.append({"SYMBOL" : element[0], "ADDRESS" : now_address})
            op_list.append({"TEXT" : format(byte_int, '02X'), "FORMAT" : 0})
            now_address += 1

    elif "WORD" in element:
        #判斷如果WORD前面沒有符號名稱
        if len(element) < 3 or element[0] == "WORD":
            print("Error: Missing symbol before WORD.")
            exit(1)
        symbol_name = element[0]

        if element[0] in symbol_set:
            print("Symbol has already existed")
            exit(1)
        
        try:
            word_value = int(element[2])
        except ValueError:
            print("Error: Invalid value for WORD.")
            exit(1)
        
        symbol_table.append({"SYMBOL" : element[0], "ADDRESS" : now_address})
        op_list.append({"TEXT" : format(word_value, '06X'), "FORMAT" : 0})
        now_address += 3

    elif "RESB" in element:
        #判斷如果RESB前面沒有符號名稱
        if len(element) < 3 or element[0] == "RESB":
            print("Error: Missing symbol before RESB.")
            exit(1)
        symbol_name = element[0]

        if element[0] in symbol_set:
            print("Symbol has already existed")
            exit(1)

        try:
            resb_value = int(element[2])  
            if resb_value <= 0: 
                raise ValueError("Value must be a positive integer.")
        except ValueError as e:
            print("Error: {e}")
            exit(1)
        
        symbol_table.append({"SYMBOL" : element[0], "ADDRESS" : now_address})
        op_list.append({"FORMAT" : -1})
        now_address += resb_value

    elif "RESW" in element:
        #判斷如果RESW前面沒有符號名稱
        if len(element) < 3 or element[0] == "RESW":
            print("Error: Missing symbol before RESW.")
            exit(1)
        symbol_name = element[0]

        if element[0] in symbol_set:
            print("Symbol has already existed")
            exit(1)
        
        try:
            resw_value = int(element[2])  
            if resw_value <= 0: 
                raise ValueError("Value must be a positive integer.")
        except ValueError as e:
            print(f"Error: {e}")
            exit(1)

        symbol_table.append({"SYMBOL" : element[0], "ADDRESS" : now_address})
        op_list.append({"FORMAT" : -1})
        now_address += 3*resw_value

    elif "BASE" in element:
        if len(element) < 2:
            print("Error: BASE directive missing parameter")
            exit(1)
        
        base_label = element[-1]

    elif "END" in element:
        code_end_address = now_address
        end_label = element[-1]
        break

    else:
        #判斷是format4還是其他
        if "+" in line:
            for opcode in op_table:
                if len(element) > 1 and element[1][1:] == opcode["NAME"] :
                    if element[0] in symbol_set:
                        print("Symbol has already existed")
                        exit(1)
                    
                    symbol_table.append({"SYMBOL" : element[0],"ADDRESS" : now_address})
                    op_list.append({"OP" : element[1], "OPCODE" : opcode["OPCODE"], "FORMAT" : 4, "DIRECTIVE" : ''.join(element[2:]), "ADDRESS" : now_address})
                    now_address += 4
                elif element[0][1:] == opcode["NAME"]:
                    op_list.append({"OP" : element[0], "OPCODE" : opcode["OPCODE"], "FORMAT" : 4, "DIRECTIVE" : ''.join(element[1:]), "ADDRESS" : now_address})
                    now_address += 4
        else:
            for opcode in op_table:
                if len(element) > 1 and element[1] == opcode["NAME"]:
                    if element[0] in symbol_set:
                        print("Symbol has already existed")
                        exit(1)
                    
                    format_value = opcode["FORMAT"]
                    symbol_table.append({"SYMBOL" : element[0],"ADDRESS" : now_address})
                    op_list.append({"OP" : element[1], "OPCODE" : opcode["OPCODE"], "FORMAT" : format_value, "DIRECTIVE" : ''.join(element[2:]), "ADDRESS" : now_address})
                    now_address += format_value
                elif element[0] == opcode["NAME"]:
                    format_value = opcode["FORMAT"]
                    op_list.append({"OP" : element[0], "OPCODE" : opcode["OPCODE"], "FORMAT" : format_value, "DIRECTIVE" : ''.join(element[1:]), "ADDRESS" : now_address})
                    now_address += format_value

print()
print("process name:", code_name)
print("process start address: 0x" + format(int(code_start_address), '06X'))
print("process end address: 0x" + format(int(code_end_address), '06X'))
print("process length:", code_end_address - code_start_address, "Bytes")

print()
print("SYMBOL\tADDRESS")
for label in symbol_table:
    print(label["SYMBOL"] + "\t" + format(label["ADDRESS"], '06X'))    

file.close()

#pass 2
file = open("output.txt", 'w')

#H record
if code_end_address - code_start_address > pow(2, 24):
    print("the size is too large")
    exit(0)
else:
    program_name = code_name[:6].ljust(6)
    start_address = format(int(code_start_address), '06X')
    length = format(int(code_end_address - code_start_address), '06X')
    h_record = "H" + program_name + start_address + length + "\n"
    file.write(h_record)
    print("\n" + h_record, end="")

#T record
record_objectcode = ""
record_start_address = next(label["ADDRESS"] for label in symbol_table if label["SYMBOL"] == end_label)
record_length = 0
base_address = next(label["ADDRESS"] for label in symbol_table if label["SYMBOL"] == base_label)

for opcode in op_list:
    #遇到RESW、RESB就先寫出
    if opcode["FORMAT"] == -1 and record_length > 0:
        t_record = "T" + format(record_start_address, '06X') + format(int(len(record_objectcode)/2), '02X') + record_objectcode + "\n"
        record_objectcode = ""
        record_start_address = -1
        record_length = 0
        file.write(t_record)
        print(t_record, end="")
    
    elif opcode["FORMAT"] != -1:
        if record_start_address == -1:
            record_start_address = opcode["ADDRESS"]
        
        now_objectcode = ""
        now_length = 0
        #BYTE、WORD
        if opcode["FORMAT"] == 0:
            now_objectcode = opcode["TEXT"]
        #format 2
        elif opcode["FORMAT"] == 2:
            now_length = 2
            regiester_name = opcode["DIRECTIVE"].split(",")
            #只有一個寄存器的情況
            if len(regiester_name) < 2:
                now_objectcode = opcode["OPCODE"] + register_table[regiester_name[0]] + "0"
            #有兩個寄存器的情況
            else:
                now_objectcode = opcode["OPCODE"] + register_table[regiester_name[0]] + register_table[regiester_name[1]]
        #format 3、format 4
        else:
            now_directive = opcode["DIRECTIVE"]
            #flag=[n, i, x, b, p, e]
            flag = ["1", "1", "0", "0", "0", "0"]
            if "@" in now_directive:
                flag[1] = "0" #n=1; i=0
                now_directive = now_directive[1:]
            if "#" in now_directive:
                flag[0] = "0" #n=0, i=1
                now_directive = now_directive[1:]
            if now_directive[-2:] == ",X":
                flag[2] = "1" #x=1
                now_directive = now_directive[:-2]
            
            #format 3
            if opcode["FORMAT"] == 3:
                now_length = 3
                now_opcode = ''.join(format(int(char, 16), '04b') for char in opcode["OPCODE"])[:-2]

                target_address = next((label["ADDRESS"] for label in symbol_table if label["SYMBOL"] == now_directive), -1)
                if target_address != -1:
                    current_address = opcode["ADDRESS"]
                    #PC-relative
                    if target_address - current_address - 3 <= 2047 and target_address - current_address - 3 >= -2048:
                        flag[4] = "1" #b=0, p=1
                        displacement = format((int(target_address - current_address - 3) & int("1"*12, 2)), '012b')
                        format3_objectcode = now_opcode + ''.join(char for char in flag) + displacement
                    #base-relative
                    elif target_address - base_address >= 0 and target_address - base_address <= 4095:
                        flag[3] = "1" #b=1, p=1
                        displacement = format((int(target_address - base_address) & int("1"*12, 2)), '012b')
                        format3_objectcode = now_opcode + ''.join(char for char in flag) + displacement
                else:
                    if len(now_directive) > 0:
                        displacement = format(int(now_directive), '012b')
                        format3_objectcode = now_opcode + ''.join(char for char in flag) + displacement
                    else:
                        displacement = format(0, '012b')
                        format3_objectcode = now_opcode + ''.join(char for char in flag) + displacement
                
                #將objectcode變成6個十六進位的數字字串儲存
                for i in range(0, 6):
                    now_objectcode = now_objectcode + hex(int(format3_objectcode[i * 4:i * 4 + 4], 2))[2:].upper()

            elif opcode["FORMAT"] == 4:
                flag[5] = "1"
                now_length = 4
                now_opcode = ''.join(format(int(char, 16), '04b') for char in opcode["OPCODE"])[:-2]

                format4_address = next((label["ADDRESS"] for label in symbol_table if label["SYMBOL"] == now_directive), -1)
                if format4_address != -1:
                    format4_objectcode = now_opcode + ''.join(char for char in flag) + format((int(format4_address) & int("1"*20, 2)), '020b')
                else:
                    format4_objectcode = now_opcode + ''.join(char for char in flag) + format(int(now_directive), '020b')

                #將objectcode變成8個十六進位的數字字串儲存
                for i in range(0, 8):
                    now_objectcode = now_objectcode + hex(int(format4_objectcode[i * 4:i * 4 + 4], 2))[2:].upper()

        #判斷record_length有沒有超過"1E"
        if record_length + now_length > 30:
            t_record = "T" + format(record_start_address, '06X') + format(int(len(record_objectcode)/2), '02X') + record_objectcode + "\n"
            record_length = now_length
            record_objectcode = now_objectcode
            record_start_address = opcode["ADDRESS"]
            file.write(t_record)
            print(t_record, end="")
        else:
            record_length = record_length + now_length
            record_objectcode = record_objectcode + now_objectcode

t_record = "T" + format(record_start_address, '06X') + format(int(len(record_objectcode)/2), '02X') + record_objectcode + "\n"
file.write(t_record)
print(t_record, end="")

#M record
for opcode in op_list:
    if opcode["FORMAT"] == 4:
        now_directive = opcode["DIRECTIVE"]
        if "#" in now_directive:
            continue
        else:
            modification_address = opcode["ADDRESS"] + 1
            modification_length = "05"
            m_record = "M" + format(modification_address, '06x') + modification_length + "\n"
            file.write(m_record)
            print(m_record, end="")

#E record
entry_address = format(next((label["ADDRESS"] for label in symbol_table if label["SYMBOL"] == end_label), None), '06x')
e_record = "E" + entry_address + "\n"
file.write(e_record)
print(e_record)

file.close()
print("Press Enter to quit.", end="")
input()