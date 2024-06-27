__author__='ASHISH SHARMA'

import asyncio, re, json
import os, datetime
import requests
import websockets

csv_file_path = os.path.join(os.getcwd(), 'CrashData.csv')
arry = []
amounts = {}
total = 0
start = 20
times = 1.32
chances = 26
# a = {0: 20, 1: 26, 2: 35, 3: 47, 4: 62, 5: 83, 6: 110, 7: 147, 8: 195, 9: 260, 10: 346, 11: 460, 12: 612, 13: 814, 14: 1083, 15: 1441, 16: 1917, 17: 2549, 18: 3391, 19: 4510, 20: 5998, 21: 7978, 22: 10611}

for i in range(chances):
    total_amount = sum(tuple(amounts.values()))
    if total_amount > 36000:
        break
    amounts.setdefault(i, int(start))
    start *= times

def send_telegram_message(message=''):
    bot_token = "1390663072:AAGaeij7DseLoyKGAwYKm1kRJuBzZ_vUyvA"
    chat_id = "-1002221973967"

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage?chat_id={chat_id}&text={message}"
    params = {
        "chat_id": chat_id,
        "text": message
    }
    # print(url)
    response = requests.get(url, params=params)
    return response.json()

def check_and_msg_tel_func(arry, times_data, amounts, warning_no=16, invest=0, times_lessthan=5, msg_on_after_iters=5, next_iter_time=[9, 15, 18, 22, 25, 30, 35, 40, 45]):
    # print(arry, times_data, type(times_data))
    if len(arry) + msg_on_after_iters == chances:
           total = sum(tuple(amounts.values())[: len(arry) - msg_on_after_iters + 1])
           send_telegram_message(message=f"[BK], Amount: {total}")

    if float(times_data) >= times_lessthan:
        if len(arry) > msg_on_after_iters:
           arry.append(str(times_data))
           invest = amounts[len(arry)- msg_on_after_iters]
           total = sum(tuple(amounts.values())[: len(arry) - msg_on_after_iters + 1])
           WinAmount = int(times_lessthan*amounts[len(arry)- msg_on_after_iters + 1]) - int(total)
           send_telegram_message(message=f"[RESET], \nExit at: {invest}\nTotal: {total}\nProfit: Rs. {WinAmount}") 
        arry = []

    else:
        arry.append(str(times_data))
        if len(arry) >= msg_on_after_iters:
            invest = amounts[len(arry)- msg_on_after_iters]
            total = sum(tuple(amounts.values())[: len(arry) - msg_on_after_iters + 1])
            warning_exit = ''
            if len(arry) >= warning_no:
                exit_from = total/invest
                warning_exit = f'\nWARNING,\nFor current invest: Rs.{invest}, Safe exit at {exit_from:.2f}'

            if len(arry) >= msg_on_after_iters + 2:
                send_telegram_message(message=f"[Ready], \nCurrent: {str(times_data)}\nOld: {', '.join(arry)}\nStart at/Actual No.:{len(arry)- msg_on_after_iters + 1}/{len(arry)}\nInvest: {invest}\nTotal: {total} {warning_exit}")
            else:
                send_telegram_message(message=f"[Ready], Open App and wait for msg")

            if len(arry) in next_iter_time:
                send_telegram_message(message = f'[MAX]: {len(arry)} times < {times_lessthan}x')
    return arry

async def connect_to_websocket(uri, message1, message2):
     
    async with websockets.connect(uri) as websocket:
        await websocket.send(message1)
        await websocket.send(message2)
        print(f"Sent: {message1}")
        print(f"Sent: {message2}")

        while True:
            response = await websocket.recv()
            # print(response)
            try:
                global arry, amounts, total
                if '"target":"OnCrash"' in response:
                    response = re.sub(r'[^\x20-\x7E]', '', response)
                    payload = json.loads(response)
                    func_call = payload['arguments'][0]['l']
                    times = payload['arguments'][0]['f']
                    # ts = payload['arguments'][0]['ts']
                    # print(times)

                    current_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")  
                    csv_data = f"{float(times):.2f},{func_call},{current_date}\n"
                    # print(f'{float(times):.2f} : {current_date}')
                    with open(csv_file_path, 'a') as file:
                        file.write(csv_data)
                    arry = check_and_msg_tel_func(arry=arry, times_data=times, amounts=amounts)
                    
            except Exception as e:
                print('Error processing WebSocket frame:', e)

if __name__=='__main__':
    try:
        with open(csv_file_path, 'r') as file:
            data = file.read()
    except:
        with open(csv_file_path, 'w+') as file:
            file.write('Times,func_Call,Date\n')
    # print(amounts)
    uri = "wss://1xbet.com/games-frame/sockets/crash?whence=50&fcountry=71&ref=1&gr=70&appGuid=00000000-0000-0000-0000-000000000000&lng=en"

    message1 = '{"protocol":"json","version":1}'
    message2 = '{"arguments":[{"activity":30,"currency":99}],"invocationId":"31","target":"Guest","type":1}'

    asyncio.get_event_loop().run_until_complete(connect_to_websocket(uri, message1, message2))
