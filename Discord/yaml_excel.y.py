import json

import yaml,pandas


class yamlExcelTrans():
    def __init__(self):
        self.configPath = 'conf/dcFpDev.yaml'
        with open(self.configPath, "r", encoding="utf-8-sig") as f:
            self.yamlConfig = yaml.safe_load(f)
            self.hitText = self.yamlConfig.get("hitText")
    def yamlToExcel(self):

        df = pandas.DataFrame.from_dict(self.hitText)
        print(df.to_dict())
        # df_t = df.transpose()
        # df_t.to_excel('src/transYaml.xlsx')

    def excelToYaml(self):
        df = pandas.read_excel('src/transYaml.xlsx',index_col=0)
        df_d = df.transpose().to_dict()
        yamlFile = open('src/output.yaml','w')
        yaml.dump(df_d,yamlFile,allow_unicode=True)


if __name__ == "__main__":
    yamlExcelTrans().yamlToExcel()
    yamlExcelTrans().excelToYaml()