
# import json
#
# with open("D:\PYc\Re\info.json", 'r', encoding='utf-8') as f:
#
#    ret_dic = json.load(f)
#
#    for i in range(len(ret_dic)):
#       #print(ret_dic[i]['score'])
#       if ret_dic[i]['score']==10 :
#          filename = 'D:\\PYc\\Re\\test_text.txt'
#          with open(filename, 'a') as file_object:
#             file_object.write("4\n")
#       elif ret_dic[i]['score']==8 :
#          filename = 'D:\\PYc\\Re\\test_text.txt'
#          with open(filename, 'a') as file_object:
#             file_object.write("3\n")
#       elif ret_dic[i]['score']==6 :
#          filename = 'D:\\PYc\\Re\\test_text.txt'
#          with open(filename, 'a') as file_object:
#             file_object.write("2\n")
#       elif ret_dic[i]['score']==4 :
#          filename = 'D:\\PYc\\Re\\test_text.txt'
#          with open(filename, 'a') as file_object:
#             file_object.write("1\n")
#       elif ret_dic[i]['score']==2 :
#          filename = 'D:\\PYc\\Re\\test_text.txt'
#          with open(filename, 'a') as file_object:
#             file_object.write("0\n")

import numpy as np
import pandas as pd

txt = np.loadtxt('D:/PYc/Re/test_text.txt')
txtDF = pd.DataFrame(txt)
txtDF.to_csv('D:/PYc/Re/test_text.csv', index=False)