import json,os,re
import numpy as np

# 解析i18n.json
with open(".\\i18n.json","r",encoding="utf-8") as f:
    json_data = json.loads(f.read())

# 扫描目录然后存储到字典中
# name : path
paths = dict()
def recursive_listdir(path):
    global paths
    for i in os.scandir(path):
        if i.is_dir():
            recursive_listdir(i)
        if i.is_file():
            # 初始化
            if paths.get(i.name) == None:
                paths[i.name] = []
            paths[i.name].append(i.path)

recursive_listdir('.\\game')
np.set_printoptions(threshold=np.inf)
print(paths)
print("\n\n\n\n")

# 读取游戏文件内容, 返回字符串
def read_file(path_of_input_file:str) -> str:
    with open(path_of_input_file,"r",encoding="utf-8") as f:
        return f.read()

# 写入文件
def write_file(text:str,path_of_output_file:str):
    with open(path_of_output_file,"w",encoding="utf-8") as f:
        f.write(text)

# 模糊搜索文字内容并替换
def replace_string_fuzzy(text: str, search_text: str, replace_text: str, pos, pN) -> str:
    if pN != None and pN != "":
        # 找到 pN 标识的位置
        temp = re.search(":: "+pN+" \[.+\]",text)
        if temp == None:
            temp = re.search(":: "+pN+"\n",text)
        if temp == None:
            temp = re.search(":: "+pN+"\[.+\]",text)

        pN_pos = text.find(temp.group())
        # 计算出从 pN 到下一个\n的位置
        while text[pN_pos]!= "\n":
            pN_pos += 1

        if pN_pos == -1:
            return "ERROR in find pN"
        # 计算位置
        real_pos = pN_pos + pos
    else:
        # 直接使用 pos 值
        real_pos = int(pos)
    
    start_pos = real_pos - 10
    end_pos = real_pos + len(search_text) + 30
    if start_pos < 0:
        start_pos = 0
    sub_text = text[start_pos:end_pos]
    if sub_text.find(search_text) == -1:
        return "ERROR"
    
    new_text = text[:start_pos] + sub_text.replace(search_text, replace_text, 1) + text[end_pos:]
    return new_text

offset = 0
last_file_name = ""
last_pN = None

for TypeBOutputText in json_data["typeB"]["TypeBOutputText"]:
    if last_file_name == "":
        last_file_name = TypeBOutputText["fileName"]
    if last_file_name != TypeBOutputText["fileName"]:
        offset = 0
        last_file_name = TypeBOutputText["fileName"]
    if last_pN == None:
        last_pN = TypeBOutputText.get("pN")
    if last_pN != TypeBOutputText.get("pN"):
        offset = 0

    file = paths[TypeBOutputText["fileName"]][0]
    all_pN = ""
    if TypeBOutputText.get("pN") != None:
        # 找到含有 pN 标识的文件
        for i in paths[TypeBOutputText["fileName"]]:
            temp_context = read_file(i)
            all_pN_match = re.search(":: "+TypeBOutputText["pN"]+" \[.+\]",temp_context)
            if all_pN_match != None:
                all_pN = all_pN_match.group()
                file = i
                break
            else:
                continue
    
    context = read_file(file)
    original_length = len(context)
    new_context = replace_string_fuzzy(context, TypeBOutputText["f"], TypeBOutputText["t"], TypeBOutputText["pos"] + offset, all_pN)
    print(file)
    if new_context == "ERROR":
        print("ERROR")
        exit(-1)
    # 计算偏移量
    offset += len(new_context) - original_length
    write_file(new_context, file)

offset = 0
last_file_name = ""
last_pN = None

for TypeBInputStoryScript in json_data["typeB"]["TypeBInputStoryScript"]:
    # 和 TypeBOutputText 一样
    if last_file_name == "":
        last_file_name = TypeBInputStoryScript["fileName"]
    if last_file_name != TypeBInputStoryScript["fileName"]:
        offset = 0
        last_file_name = TypeBInputStoryScript["fileName"]

    if last_pN == None:
        last_pN = TypeBInputStoryScript.get("pN")
    if last_pN != TypeBInputStoryScript.get("pN"):
        last_pN = TypeBInputStoryScript.get("pN")
        offset = 0

    file = paths[TypeBInputStoryScript["fileName"]][0]
    all_pN = TypeBInputStoryScript.get("pN")
    if TypeBInputStoryScript.get("pN") != None:
        # 找到含有 pN 标识的文件
        for i in paths[TypeBInputStoryScript["fileName"]]:
            temp_context = read_file(i)
            all_pN_match = re.search(":: "+TypeBInputStoryScript["pN"]+" \[.+\]",temp_context)
            if all_pN_match == None:
                all_pN_match = re.search(":: "+TypeBInputStoryScript["pN"]+"\n",temp_context)
            if all_pN_match != None:
                all_pN = all_pN_match.group()
                file = i
                break
            else:
                continue
    
    context = read_file(file)
    original_length = len(context)
    new_context = replace_string_fuzzy(context, TypeBInputStoryScript["f"], TypeBInputStoryScript["t"], TypeBInputStoryScript["pos"] + offset, TypeBInputStoryScript.get("pN"))
    print(file)
    if new_context == "ERROR":
        print("ERROR")
        exit(-1)
    # 计算偏移量
    offset += len(new_context) - original_length
    write_file(new_context, file)