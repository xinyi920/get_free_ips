"""
本代码根据CSDN中yk 坤帝的代码进行改进
_*_ encoding:utf-8_*_
Time:2021-5-28
Author:歆逸
"""

# 导包
import requests
from lxml import etree
import time
import os


# 定义获取免费ip类
class get_free_ip(object):
    """
    这里将起始与终止页加入，方便之后在其他代码中代入，而不用显示输入起始页与终止页；
    若不想，可手动输入将这里的self.begin_page和self.end_page注释掉，将下面的判断的改为begin_page和end_page
    然后将下方的
     else:
        print("输入有误，请重新输入，将会在5s后返回重新输入界面")
        time.sleep(5)
        return self.get_and_save_ip()
    这些行代码注释回来即可
    """
    # 初始化参数值
    def __init__(self, begin_page, end_page):
        self.proxies_list = []
        self.new_list = []
        self.can_use = []                       # 能用的ip存放
        self.proxies = {}                       # 爬取能用的ip存储地
        self.begin_page = begin_page            # 爬取起始页
        self.end_page = end_page                # 终止页
        self.get_and_save_ip()
        """
        进入获取并保存ip方法，后面也同样返回下一个执行的方法，让其自动进行，而不用在调用的时候调用多个方法
        直接实例化对象，然后在将对象的proxies直接赋值到相应的变量即可
        """

    def get_and_save_ip(self):  # 获取并保存ip
        proxy_dict = {}
        # begin_page = int(input("请输入起始页:"))
        # end_page = int(input("请输入结束页（包括结束页内的ip）:"))
        if self.end_page >= self.begin_page:            # 逻辑判断 起始页必须小于等于终止页
            # print("正在获取ip...")
            for page in range(self.begin_page, self.end_page + 1):  # 该网站总共有4054页数据，可根据自己需求设置页数
                time.sleep(1)                   # 爬取完一页后等待1秒后继续爬取
                # print(f'===============正在爬取第{page}页数据================')
                # 可变换目标url
                url = f'https://www.kuaidaili.com/free/inha/{page}/'
                # 伪装代理头来请求浏览器去获取数据
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.193 Safari/537.36'
                }
                # proxies = {
                #     'http': 'http:114.99.252.40',
                #     'http': 'http:175.166.91.88'
                # }
                # 请求浏览器获取响应
                response = requests.get(url, headers=headers)
                response.encoding = response.apparent_encoding

                page_text = response.text

                # 将HTML字符串转化为Element对象
                tree = etree.HTML(page_text)

                # 利用xpath提取对应字符串
                trs = tree.xpath('//*[@id="list"]/table/tbody/tr')

                # 遍历取值
                for tr in trs:
                    ip_num = tr.xpath('./td[1]/text()')[0]
                    ip_port = tr.xpath('./td[2]/text()')[0]

                    ip_proxy = ip_num + ':' + ip_port
                    # print(ip_proxy)
                    # 判断是http还是https
                    if tr.xpath('./td[4]/text()')[0] == 'HTTP':  # 若是http头，则以http头添加
                        proxy_dict = {
                            'http': 'http://' + ip_proxy,
                        }
                    if tr.xpath('./td[4]/text()')[0] == 'HTTPS':  # 若是https头，则以https头添加
                        proxy_dict = {
                            'https': 'https://' + ip_proxy,
                        }
                    self.proxies_list.append(proxy_dict)
                    # print('保存成功:', proxy_dict)
            # print("获取完成")
            # print(f'共获取了{len(self.proxies_list)}个ip')
            # print(self.proxies_list)
            return self.check_ip()
        # else:
        #     print("输入有误，请重新输入，将会在5s后返回重新输入界面")
        #     time.sleep(5)
        #     return self.get_and_save_ip()
        # # 这里的else适合上方的手动输入起始和终止页，而不适合在类中，否则输错起始和终止页数将会陷入死循环

    # 用来检查代理IP是否可用，用访问百度方法来查看访问码
    def check_ip(self):
        time.sleep(1)
        # can_use = []
        for ip in self.proxies_list:
            try:
                response = requests.get(url='https://www.baidu.com', proxies=ip, timeout=0.1)
                if response.status_code == 200:
                    self.can_use.append(ip)
            except EnvironmentError:
                # print('当前的代理:', ip, '请求超时，检测不合格')
                pass
            else:
                # print('当前的代理:', ip, '检测合格')
                for i in ip.values():
                    with open("代理ip.txt", "a+") as f:
                        f.write(i + '\n')       # \n 换行处理
                        f.close()
        # return self.can_use
        # print('\n===========================检测完成===================================')
        # print(f'共有{len(self.can_use)}个ip可以使用')
        return self.read_and_write()

    # 读取文件并将文件内容写入列表之后删除文件
    def read_and_write(self):
        with open('代理ip.txt', 'r') as f:
            data = f.readlines()
            f.close()
        for http in data:
            self.new_list.append(http)
        for i in range(len(self.new_list)):
            self.new_list[i] = self.new_list[i].strip()
        file = '代理ip.txt'
        if os.path.exists(file):  # 如果文件存在
            os.remove(file)  # 则删除
        else:
            print(f'no such file:{file}')
        # print(new_list)
        return self.write_into_proxies()

    # 将IP添加到代理池中
    def write_into_proxies(self):
        for j in range(len(self.new_list)):
            self.proxies[f'http{j+1}'] = self.new_list[j - 1]
        # print(self.proxies)
        print(f'共有{len(self.proxies)}个ip加入代理池中')
        return self.proxies


"""
这里使用pass跳过，方便之后的导包；
若想在这里检测只需将pass注释掉然后把下方代码注释回来即可
注意检测完成后将代码注释回原来的样子
"""
if __name__ == '__main__':
    pass
    # a = get_free_ip(1, 1)
    # proxies = a.proxies
    # print(proxies)
