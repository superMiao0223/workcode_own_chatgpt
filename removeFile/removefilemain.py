import shutil,os,openpyxl
import time


class copyFile(object):
    def __init__(self):
        self.excelpath = '配音文件.xlsx'
        self.basefilename = 'targetfile_output'
        self.targetfilename = 'targetfile1'

    def readexcel(self):
        wb = openpyxl.load_workbook(self.excelpath)
        ws = wb.active
        fileDict = {}
        for rowinfo in ws.iter_rows(min_row=2):
            basevalue1 = rowinfo[0].value
            basekey = rowinfo[2].value
            basevalue2List = rowinfo[3].value.split(",") if rowinfo[3].value != None else None
            if basevalue2List != None:
                for basevalue2 in basevalue2List:
                    try:
                        fileDict[basekey].append(str(basevalue1) + '-' + basevalue2)
                    except:
                        fileDict[basekey] = [str(basevalue1) + '-' + basevalue2]
        # print(fileDict)
        return fileDict
    def createtartgetmainfile(self):
        if not os.path.exists(self.targetfilename):
            os.mkdir(self.targetfilename)
    def copyfile(self):
        self.createtartgetmainfile()
        #获取base文件夹下的配音文件

        #listfilename = os.listdir(self.basefilename) #适用于单文件夹
        #print(listfilename)
        listfilename = []
        for root,dirs,files in os.walk(self.basefilename):
            for filebase in files:
                listfilename.append(root+'/'+filebase)
        #获取excel文件内容并输出成字典格式
        fileDict = self.readexcel()
        #获取目标文件夹及对应base文件夹的文件名
        for targetfilepath, basename in fileDict.items():
            print(str(self.targetfilename) + '/' + str(targetfilepath))
            tgfilepath = str(self.targetfilename) + '/' + str(targetfilepath)
            #若文件夹不存在则自己创建
            if not os.path.exists(tgfilepath):
                os.mkdir(tgfilepath)
            #准备复制文件内容
            for basename1 in basename:
                for basefilename2 in listfilename:
                    if basename1[basename1.find("-")+1:] in basefilename2:
                        try:
                            shutil.copy(basefilename2, tgfilepath + '/' + basename1 + '.wav')
                        except Exception as e:
                            print(e)
    # shutil.copy(basefilename+'/'+listfilename[1],targetfilename+'/'+'abc.wav')
    def remove_file(self):
        listfilename = os.listdir(self.basefilename)
        for filename1 in listfilename:
            ftList = filename1.split("-")
            if not os.path.exists(self.targetfilename + '/' + ftList[0][:5]):
                os.mkdir(self.targetfilename + '/' + ftList[0])
            try:
                shutil.move(self.basefilename + '/' + filename1, self.targetfilename + '/' + ftList[0] + '/' + filename1)
            except Exception as e:
                print(e)
    def removedir(self):
        for root, dirs, files in os.walk(self.targetfilename):
            # print(root,files)
            if len(files) == 0:
                # print(root)
                shutil.rmtree(root)
        # print(root)
    def checkFileIntegrity(self):
        # 获取excel文件内容并输出成字典格式
        fileDict = self.readexcel()
        print(fileDict)
        """
        获取文件夹下所有文件，并比对excel文件中少了哪些
        """
        for root, dirs, files in os.walk(self.targetfilename):
            # print(root,dirs,files)
            if root == self.targetfilename:
                pass
            else:
                for filename in fileDict[int(root[root.find("/")+1:])]:
                    # print(filename[:-4])
                    # print(fileDict[int(root[root.find("/")+1:])])
                    try:
                        if filename+".wav" not in files:
                            print(root,filename)
                    except Exception as e:
                        print(f"出错了,报错内容：\n{e}")

if __name__ == "__main__":
    # copyFile().copyfile()
    # copyFile().removedir()
    copyFile().checkFileIntegrity()