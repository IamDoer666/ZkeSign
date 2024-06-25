import requests
from lxml import etree
import os

class Sign:
    def __init__(self) -> None:
        self.username=os.environ.get("username")
        self.password = os.environ.get("password")
        self.serect = os.environ.get("serect")
        self.headers={
            "accept": "application/json, text/javascript, */*; q=0.01",
            "accept-language": "zh-CN,zh;q=0.9",
            "cache-control": "no-cache",
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "origin": "https://kbzyz.com",
            "pragma": "no-cache",
            "priority": "u=1, i",
            "referer": "https://kbzyz.com/",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
            "x-requested-with": "XMLHttpRequest"
        }
        self.session=requests.Session()
    # 进行账户登录      
    def login(self):
        url="https://kbzyz.com/wp-admin/admin-ajax.php"
        data = {
        "action": "user_login",
        "username": self.username,
        "password": self.password,
        "rememberme": "1"
    }   
    # 首先进行账号登录
        res = self.session.post(url=url,headers=self.headers,data=data)
        return res.json()
    
     # 定义pushplus消息发送功能
    def sendMsg(self,content):
        data={
        "token":self.serect,
        "title":"资料网签到消息",
        "content":content,
        "channel":"wechat",
        "template":"html"
        }
        res=requests.post("http://www.pushplus.plus/send",data=data).json()
        if(res["code"]==200):
            print("发送成功")
        else:
            print("发送失败")
    
    # 进入签到页面,获取用户的账号余额信息
    def get_account(self):
        userres=self.session.get('https://kbzyz.com/user',headers=self.headers)
        tree = etree.HTML(userres.text)
        user_name=tree.xpath('//*[@id="post-form"]/div/div[2]/div/input')[0].get("value")
        # 获取认证密钥
        nonce=tree.xpath('//*[@id="save-userinfo"]')[0].get("data-nonce")
        # 金币余额
        pre_balance = tree.xpath('//span[contains(@class,"badge-warning-lighten")]/text()')[0]
        # 累计消费
        pre_accuassume=tree.xpath('//span[contains(@class,"badge-primary-lighten")]/text()')[0]
        return {"user_name":user_name,"nonce":nonce,"pre_balance":pre_balance,"pre_accuassume":pre_accuassume}
    # 进行用户签到
    def sign(self):
        # 首先获取签到前的用户信息
        user_detail=self.get_account()
        print(user_detail)
        # 进行签到
        sign_url="https://kbzyz.com/wp-admin/admin-ajax.php"
        user_msg={
            "action": "user_qiandao",
            "nonce": user_detail["nonce"]
            }
        res=self.session.post(url=sign_url,data=user_msg).json()
        
        now_balance=self.get_account()["pre_balance"]
        content=f'''<h3>签到前余额:<span style="color:#eb4d4b;">{user_detail["pre_balance"]}</span></h3>
        <h3>签到前消费额<span style="color:#eb4d4b;">{user_detail["pre_accuassume"]}</span></h3>
        <hr/>
        <h2>{res['msg']}</h2>
        <h3>当前余额:<span style="color:#7ed6df;">{now_balance}</span></h3>'''
        self.sendMsg(content=content)
    
    # 判断用户是否登录成功，成功则进行签到，否则发送登录失败信息
    def analy_login(self,res):
        if res["status"]=="0":
            self.sendMsg("账号密码错误")
        else:
            self.sign()

    def exec(self):
       login_res=self.login()
       self.analy_login(login_res)


if __name__=="__main__":
    sign=Sign()
    sign.exec()




