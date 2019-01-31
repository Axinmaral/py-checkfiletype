import os, sys, json
#from tabulate import tabulate
#from collections import Counter
try:
    from tabulate import tabulate
    from collections import Counter 
    print('已检测到tabulate模块           ok')
    #break
except:
    print('检测到未安装tabulate模块,现在开始安装......')
    os.system('pip install tabulate')
try:
    from collections import Counter 
    print('已检测到collections模块           ok')
    #break
except:
    print('检测到未安装collections模块,现在开始安装......')
    os.system('pip install collections')    

class FileExtChecker:    
    typeList = {}
    keyLens = []

    def __init__(self, path:str, filename:str):
        self.filename = filename 
        self.fullname = os.path.join(path, filename)
        self.name, self.extName = os.path.splitext(filename)
        self.extName = self.extName[1:].lower()
        self.realtype = self._realtype()
    
    def check(self):
        return (self.filename, self.realtype, not self.extName == self.realtype)
        
    
    def _realtype(self)->str:
        with open(self.fullname, 'rb') as fp:
            self.bins = fp.read(max(self.keyLens))
            for l in self.keyLens:
                realtype = self.typeList.get(self.bins[:l], 'unknown')
                if realtype != 'unknown':
                    break
        return realtype

def typeListFromJson(json_file):
    with open(json_file, 'r') as jf:
        json_str = jf.read()
        json_dict= json.loads(json_str)
        FileExtChecker.typeList = {bytes.fromhex(key) : value for key, value in json_dict.items()}
        typeList_len_count = Counter(map(len, FileExtChecker.typeList.keys()))
        FileExtChecker.keyLens = [k[0] for k in sorted(typeList_len_count.items(), key=lambda x:x[1], reverse=True)]

def process_path(inputpath):
    if os.path.isdir(inputpath): # 若输入的是文件夹路径
        folder_path = inputpath
        files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
        sub_dirs = [d for d in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, d))]

        file_objs = [FileExtChecker(folder_path, filename) 
                     for filename in files]
        result = [f.check() for f in file_objs]
        for dirs in sub_dirs:
            result.append(('--  子目录：'+ os.path.join(inputpath, dirs), '-------','------------'))
            result += process_path(os.path.join(inputpath, dirs))
        return result
    elif os.path.isfile(inputpath): # 若输入的是文件路径
        file_path = inputpath
        file_obj = [FileExtChecker(*os.path.split(file_path))]
        result = [f.check() for f in file_obj]
        return result


def rst_output(path,result:list):
    print('路径:{0}'.format(path))
    out = [(r[0], r[1], '\u2754') if r[1] == 'unknown' 
                                  else (r[0], r[1], '\u2b55') 
                                        if r[2] else (r[0], r[1], ' ') 
            for r in result]
    print(tabulate(out, headers=['文件名', '实际扩展名', '扩展名是否可能被修改']))


if __name__ == '__main__':
    try:
        inputpath = sys.argv[1]
    except IndexError:
        print('Welcome!，欢迎你使用文件扫描工具……')
        inputpath=input('请输入要扫描的文件夹路径：')

    typeListFromJson('typeList.json')
    inputpath = inputpath.strip() # 去除前后空格
    if os.path.exists(inputpath):
        result = process_path(inputpath)
        rst_output(inputpath, result)
    else:
        print("输入的文件夹/文件路径有误！")
