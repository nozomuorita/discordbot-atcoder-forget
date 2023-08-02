# インストールした discord.py を読み込む
import discord
import time
import json
import requests
import datetime
import pandas as pd
import random

def get_json(user):
    url2 = 'https://kenkoooo.com/atcoder/resources/problem-models.json'
    session2 = requests.Session()
    data2 = session2.get(url2)
    json_data2 = json.loads(data2.text)
    url = f"https://kenkoooo.com/atcoder/atcoder-api/v3/user/submissions?user={user}&from_second=1560046356"
    session = requests.Session()
    data = session.get(url)
    json_data = json.loads(data.text)
    return json_data, json_data2


def get_diff(json_data2):
    diff = pd.DataFrame()
    contest_list = []
    diff_list = []
    err = [] # unvaliable

    for i in list(json_data2.keys()):
        tmp = json_data2[i]

        if 'difficulty' in list(tmp.keys()):
            contest_list.append(i)
            diff_list.append(tmp['difficulty'])
        else:
            err.append(i)

    diff['contest_id'] = contest_list
    diff['diff'] = diff_list
    return diff

def get_submission(json_data):
    df = pd.DataFrame()
    epoch_second = []
    contest_id = []
    problem_id = []
    dist_second = []
    now = int(time.time())

    for i in range(len(json_data)):
        data = json_data[i]
        epoch_second.append(data['epoch_second'])
        contest_id.append(data['contest_id'])
        problem_id.append(data['problem_id'])
        dist_second.append(now - data['epoch_second'])

    df['epoch_second'] = epoch_second
    df['contest_id'] = contest_id
    df['problem_id'] = problem_id
    df['dist'] = dist_second
    return df

def get_url(df, diff, d):
    month = 60*60*24*30

    month_ago = df[df['dist']>month]
    base = diff.copy()
    # ひとまず、マージする
    base = base.merge(month_ago, left_on='contest_id', right_on='problem_id', how='inner')
    c = -100
    base = base[base['diff']>d]
    base = base.reset_index(drop=True)
    # 1か月以上前のものからランダムに指定し、urlを返す
    rand = random.randint(0, len(base))
    c = base.loc[rand, 'problem_id']


    if c != -100:
        var1 = c[:-2]
        url = f'https://atcoder.jp/contests/{var1}/tasks/{c}'
        return url
    else:
        return 'error: 提出数が足りません,精進してください'

# 自分のBotのアクセストークンに置き換えてください
TOKEN = 'input token'
CHANNELID = 'input channel id'

# 接続に必要なオブジェクトを生成
intents = discord.Intents.all()  # Intentsオブジェクトを生成
intents.messages = True
client = discord.Client(intents=intents)

#起動時に動作する処理
@client.event
async def on_ready():
    # 起動したらターミナルにログイン通知が表示される
    print('ログインしました')


# メッセージ受信時に動作する処理
@client.event
async def on_message(message):

    args = message.content.split()
    print(args)
    user = args[0]
    d = int(args[1])

    json_data, json_data2 = get_json(user)
    diff = get_diff(json_data2)
    df = get_submission(json_data)
    url = get_url(df, diff, d)

    # print(message)
    print(message.content, 0)
    print(user, 0)
    print(d, 1)
    await message.channel.send(url)

# Botの起動とDiscordサーバーへの接続
client.run(TOKEN)