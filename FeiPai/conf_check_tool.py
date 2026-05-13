import pandas as pd
import openpyxl
from colorama import Fore, Back, Style, init

init(autoreset=True)

class conf_check():

    def __init__(self):
        conf_path_base = ""   # 原始需求文件地址
        conf_path_base_create = ""  # 根据原始需求文件生成的配置表
        conf_path_complete = ""  # 包体配置表的文件地址

    # 读原始文件，并生成对应的文件，返回对应文件名称
    def read_base_file(self):
        pass

    # 读游戏配置表并进行比较
    def read_complete_file_check(self,file1, file2, key_column=None):
        """
            比较两个Excel文件并在控制台高亮显示差异
            :param file1: 第一个Excel文件路径
            :param file2: 第二个Excel文件路径
            :param key_column: 用作比较关键字的列名
            """
        # 读取Excel文件
        df1 = pd.read_excel(file1)
        df2 = pd.read_excel(file2)

        # 检查列是否一致
        if list(df1.columns) != list(df2.columns):
            print(Fore.RED + "错误: 两个Excel文件的列不匹配!")
            print(f"文件1列: {list(df1.columns)}")
            print(f"文件2列: {list(df2.columns)}")
            return

        # 如果有指定关键列，则设置索引
        if key_column:
            if key_column not in df1.columns:
                print(Fore.RED + f"错误: 关键列 '{key_column}' 不存在!")
                return
            df1 = df1.set_index(key_column)
            df2 = df2.set_index(key_column)

        # 找出新增/删除的行
        only_in_file1 = df1.index.difference(df2.index)
        only_in_file2 = df2.index.difference(df1.index)

        # 打印新增/删除的行
        if not only_in_file1.empty:
            print(Fore.YELLOW + "\n仅在第一个文件中存在的行:")
            print(Fore.CYAN + str(df1.loc[only_in_file1]))

        if not only_in_file2.empty:
            print(Fore.YELLOW + "\n仅在第二个文件中存在的行:")
            print(Fore.CYAN + str(df2.loc[only_in_file2]))

        # 比较共同的行
        common_rows = df1.index.intersection(df2.index)
        if not common_rows.empty:
            print(Fore.YELLOW + "\n两个文件中共有的行(差异部分高亮显示):")

            # 比较每个共同行
            for idx in common_rows:
                row1 = df1.loc[idx]
                row2 = df2.loc[idx]

                if not row1.equals(row2):
                    print(Fore.GREEN + f"\n差异行 (ID/索引: {idx}):")

                    # 比较每个单元格
                    for col in df1.columns:
                        val1 = row1[col]
                        val2 = row2[col]

                        if pd.isna(val1) and pd.isna(val2):
                            continue
                        elif val1 != val2:
                            print(f"  {col}: ", end="")
                            print(Back.RED + f"{val1}", end="")
                            print(" → ", end="")
                            print(Back.GREEN + f"{val2}")
                        else:
                            print(f"  {col}: {val1}")

        print(Style.RESET_ALL)

    def main(self):
        pass


if __name__ == "__main__":
    file1 = "file1.xlsx"
    file2 = "file2.xlsx"

    print(Fore.BLUE + f"\n比较文件: {file1} 和 {file2}")
    conf_check().read_complete_file_check(file1, file2, key_column="ID")
