# -*- coding: utf-8 -*-
"""
@Time    : 2023-03-24 16:22
@Author  : lulongji
@File    : get_L2_code.py
@Function:
@Version :V1
"""
import os
import requests
import json
import datetime
import csv

headers = {
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36 Edg/111.0.1661.44"}

json_name = 'data/315cc_data.json'  # 下载数据路径
start_time = datetime.datetime.now()

#输入要保存数据的path，并返回该地址
def get_l2_code(folder_name, file_name):
    uid_nums = 0
    path = folder_name + '/' + file_name
    #原网址 http://www.315cc.com.cn/html/exposure.html?v=20230210
    # 包含json数据的请求网址
    url = 'http://weixin.jshcsoft.com/weixin_zgxfz/ASHX/ZGXFZAPI.ashx'

    with open(path, 'w', newline='') as fp:
        table_title = ['BG_Code']
        writer = csv.DictWriter(fp, fieldnames=table_title)

        for pageno in range(1, 68): #1-556   共555页6654条信息   每页100条只需67页
            data = {
                'callback': 'successcallback',
                'DoType': 'GetRevealedSheets',
                'BG_Industry': '',
                'pagesize': '100',   # 原始每页有12条二级数据    可直接设置成100  设置太高会报500
                'pageno': f'{pageno}',
                '_': ''
            }
            response = requests.get(url, headers=headers, data=data) #数据直接是json格式的内容
            if response.status_code==200:
                response=response.text[len('successcallback('):-1]
                response = json.loads(response) #将json数据转化成python数据格式 方便取出内容
            else:
                print("获取相应失败！")
                break
            #打印辅助信息
            mid_time = datetime.datetime.now()
            print(f"*******第{pageno}页******* 耗时：{mid_time - start_time}" )
            # print(response['Rows'])

            for row in range(len(response['Rows'])):  #从每一页中取出二级页面的拼接id
                BG_Code = response['Rows'][row]['BG_Code']
                writer.writerow({"BG_Code": BG_Code})
                uid_nums+=1
    print('获取并写入BG_Code成功')
    return uid_nums

def get_datas(uid_file_path,folder_name,file_name):
    data_nums=0
    with open(uid_file_path,'r') as f :
        bg_codes = f.readlines()
    json_name = folder_name + '/' + file_name
    with open(json_name, 'w', encoding='utf-8') as f:
        f.write('{"rows": [')  # 输出格式 json数据格式的处理

        for index,bg_code in enumerate(bg_codes):
            Comp_Info_url = f'http://weixin.jshcsoft.com/weixin_zgxfz/ASHX/ZGXFZAPI.ashx?&callback=successcallback&bgCode={bg_code}&openID=&DoType=GetAppealDetails'
            Comp_process_url = f'http://weixin.jshcsoft.com/weixin_zgxfz/ASHX/ZGXFZAPI.ashx?&callback=successcallback&bgCode={bg_code}&DoType=GetAppealSheetsProcess'

            Complaint_Info = requests.get(Comp_Info_url, headers=headers).text[len('successcallback('):-1]
            Complaint_Prog = requests.get(Comp_process_url, headers=headers).text[len('successcallback(['):-2]

            f.write(Complaint_Info + ',')
            f.write(Complaint_Prog + ',')

            data_nums += 1
            mid_time = datetime.datetime.now()
            print(f"第{index + 1}条数据写入成功，还剩{len(bg_codes)-index-1},耗时：{mid_time - start_time}")

        f.write('{"全部打印完成！":"总共数据条数：%d"}]}' % (data_nums))

        print('全部打印完成！')

if __name__ == '__main__':
    folder_name= './data1'
    file_name='/BG_Code.csv'
    path = folder_name + '/' + file_name

    if not os.path.exists(path):
        os.makedirs(folder_name)
        get_l2_code(folder_name,file_name)


    get_datas(path,folder_name,'315cc_json_data.json')

'''
总结：练习了函数定义，文件创建 相互之间调用
#本版本可以实现是否已保存一级页面的数据，但是还不能判断二级页面是否保存完整
'''

