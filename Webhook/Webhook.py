import requests
import json
import sys
from flask import Flask, request, abort
 
class WXWork_SMS :
 
    # Markdown
    def send_msg_markdown(self,paramDic) :
        headers = {"Content-Type" : "text/plain"}
        send_url = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=f198b262-1507-41b7-8951-55f18511e78a"
        send_data = {}
        paramDic['user'] = user
        paramDic['eventOpr'] = eventOpr
        paramDic['ticketNum'] = ticketNum
        paramDic['summary'] = summary
        paramDic['linkFin'] = linkFin
        paramDic['statusFrom'] = statusFrom
        paramDic['comment'] = statusTo
        if paramDic['case'] == 0:
            send_data = {
                "msgtype": "markdown",
                "markdown": {
                    "content": "# **"+paramDic['user']+" "+paramDic['eventOpr']+" **<font color=\"warning\">**"+paramDic['ticketNum']+"**</font>\n" +  #title, # and words must there be a space
                        "#### **请相关同事注意，及时跟进！**\n" +  # bold：**words to be bolded**
                        "> ["+paramDic['summary']+"]("+paramDic['linkFin']+") \n"   # reference：> referenced words# green：info、grey：#comment、orange：warning#color
                }
            }
        elif paramDic['case'] == 1:
            send_data = {
                "msgtype": "markdown",
                "markdown": {
                    "content": "# **"+paramDic['user']+" "+paramDic['eventOpr']+" **<font color=\"warning\">**"+paramDic['ticketNum']+" from "+paramDic['statusFrom']
                    +" to "+paramDic['statusTo']+"**</font>\n" +
                        "#### **请相关同事注意，及时跟进！**\n" +
                        "> ["+paramDic['summary']+"]("+paramDic['linkFin']+") \n"
                }
            }
        elif paramDic['case'] == 2:
            send_data = {
                "msgtype": "markdown",
                "markdown": {
                    "content": "# **"+paramDic['user']+" "+paramDic['eventOpr']+" **<font color=\"warning\">**"+paramDic['ticketNum']+"**</font>\n"
                }
            }
        elif paramDic['case'] == 3:
            send_data = {
                "msgtype": "markdown",
                "markdown": {
                    "content": "# **"+paramDic['user']+" "+paramDic['eventOpr']+" a comment in ticket **<font color=\"warning\">**"+paramDic['ticketNum']+"**</font>\n" +
                        "#### **请相关同事注意，及时跟进！**\n" +
                        "> "+paramDic['comment']+"\n"
                }
            }
        else :
            send_data = {
                "msgtype": "markdown",
                "markdown": {
                    "content": "# **"+paramDic['user']+" "+paramDic['eventOpr']+" a comment in ticket **<font color=\"warning\">**"+paramDic['ticketNum']+"**</font>\n"
                }
            }
        
        res = requests.post(url = send_url, headers = headers, json = send_data)
        print(res.text)
 
app = Flask(__name__)

@app.route('/',methods=['POST'])
def welcome():
    return 'A simple webhook listener!'


@app.route('/webhook',methods=['POST'])
def webhook():
    print("\n\nReceived Webhook Notification")
    sys.stdout.flush()
    if request.method == 'POST':
        print(request.json)
        data = request.json
        eventOpr = data['webhookEvent']
        statusFrom = ''
        statusTo = ''
        if 'changelog' in data:
            statusFrom = data['changelog'][0]['items'][0]['fromString']
            statusTo = data['changelog']['items']['toString']
        user = data['user']['displayName']
        ticketNum = data['issue']['key']
        summary = data['issue']['fields']['summary']
        linkRaw = data['issue']['self']
        linkPrf,suf = linkRaw.split('rest',1)
        linkFin = linkPrf+"browse/"+ticketNum
        paramDic = {}
        if eventOpr.find("issue_") != -1:
            event,opr = eventOpr.split('_',1)
            if event.find("create") != -1:
                paramDic['case'] = 0
            elif event.find("update") != -1:
                paramDic['case'] = 1
            else :
                paramDic['case'] = 2
        else:
            event,opr = eventOpr.split('_',1)
            eventOpr = opr
            if event.find("delete") != -1:
                paramDic['case'] = 4
            else :
                paramDic['case'] = 3
        paramDic['user'] = user
        paramDic['eventOpr'] = eventOpr
        paramDic['ticketNum'] = ticketNum
        paramDic['summary'] = summary
        paramDic['linkFin'] = linkFin
        paramDic['statusFrom'] = statusFrom
        paramDic['statusTo'] = statusTo
        paramDic['comment'] = data['comment']['body']
        sms = WXWork_SMS()
        sms.send_msg_markdown(paramDic)
        return '',200
    else:
        abort(400)
if __name__ == '__main__':
    app.run(debug=True)
