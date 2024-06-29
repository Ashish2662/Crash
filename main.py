__author__='ASHISH SHARMA'

import asyncio, re, json
import os, datetime
import requests
import websockets

# To debug
to_file = False
csv_file_path = os.path.join(os.getcwd(), 'CrashData.csv')

# Variables
arry = ['1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1','1','1','1','1', '1']
# arry = []
amounts = {}    
amounts_num = {}
total = 0
total_amount = 0

# Logic ratio
times = 1.33

max_chances = 33
# Amount in INR
min_invest_cap = 20
max_invest_cap = 36000

# All time max crashed
all_time_max = 33.87

for i in range(max_chances):
    amounts.setdefault(i, int(min_invest_cap))
    amounts_num.setdefault(i+1, int(min_invest_cap))
    min_invest_cap *= times
    total_amount = sum(tuple(amounts.values()))
    if total_amount > max_invest_cap:
        amounts.popitem()
        amounts_num.popitem()
        total_amount = sum(tuple(amounts.values()))
        chances = i
        break
    
def send_telegram_message(message=''):
    bot_token = "1390663072:AAGaeij7DseLoyKGAwYKm1kRJuBzZ_vUyvA"
    chat_id = "-1002221973967"

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage?chat_id={chat_id}&text={message}"
    params = {
        "chat_id": chat_id,
        "text": message
    }
    # print(url)
    try:    
        response = requests.get(url, params=params)
        return response.json()
    except:
        # print('Sending err')
        pass

def check_and_msg_tel_func(arry, times_data, amounts, all_time_max, warning_no=16, invest=1, times_lessthan=4, msg_on_after_iters=6, next_iter_time=[9, 15, 18, 22, 25, 30, 32, 35, 40, 45], max_invest_cap=1000000):
    warning_exit = ''

    if float(times_data) <= times_lessthan:
        if len(arry) - msg_on_after_iters in amounts:
            invest = amounts[len(arry)- msg_on_after_iters]
            total = sum(tuple(amounts.values())[: len(arry) - (msg_on_after_iters - 1)])
            WinAmount = times_lessthan* invest - total
        else:
            invest = 1
            WinAmount = 'NA'
            if len(arry) >= chances: 
                total = sum(tuple(amounts.values())[: len(amounts)])
            else:
                total = 1


        if len(arry) == msg_on_after_iters - 3:
            send_telegram_message(message=f"[Ready], Open App and wait for Invest msg. | {times_data} |  Started at {msg_on_after_iters  + 1}th")
        
        elif len(arry) == msg_on_after_iters - 2:
            send_telegram_message(message=f"[Ready], Open App URGENT | {times_data} | Started at {msg_on_after_iters + 1}th")
        
        elif len(arry) == msg_on_after_iters - 1:
            send_telegram_message(message=f"[WELCOME], | {times_data} | Wait for invest.")
      

        elif len(arry) >= warning_no and len(arry) <= chances:
            exit_from = total/invest
            if len(arry) == warning_no:
                warning_exit = f'\nWARNING,\nFor current invest: Rs.{invest}, Safe exit at {exit_from:.2f}'
                send_telegram_message(message=warning_exit)
            else:
                warning_exit += f'\nSE:{exit_from:.2f}'
                
        if len(arry) - msg_on_after_iters == chances:
            send_telegram_message(message=f"[BK], Amount: {total} | Crashed: {str(times_data)} |\nStart at/Actual No.:{len(arry)- msg_on_after_iters + 1}/{len(arry)+1}\n chances over: {chances}")
        elif len(arry) - msg_on_after_iters >= chances + 1:
            send_telegram_message(message=f"[BK], \nLast crash: {str(times_data)}\nOld: {', '.join(arry)}\nStart at/Actual No.:{len(arry)- msg_on_after_iters + 1}/{len(arry)+1}\n")

        if len(arry) in next_iter_time:
            send_telegram_message(message = f'[EXCEED]: {len(arry)} times < {times_lessthan}x')
        
        if len(arry) >= msg_on_after_iters and len(arry) - msg_on_after_iters < chances :
            send_telegram_message(message=f"[Ready], \nLast crash: {str(times_data)}\nOld: {', '.join(arry)}\nStart at/Actual No.:{len(arry)- msg_on_after_iters + 1}/{len(arry)+1}\nNext Invest: {invest}\nTotal: {total} {warning_exit}")

        arry.append(str(times_data))

    else:
        # print(arry)
        if len(arry) - (msg_on_after_iters + 1) in amounts:
            invest = amounts[len(arry)- (msg_on_after_iters + 1 )]
        total = sum(tuple(amounts.values())[: len(arry) - (msg_on_after_iters)])
        WinAmount = times_lessthan* invest - total

        if float(times_data) > all_time_max:
            all_time_msg = f'\n[ATM]: {times_data}'
            all_time_max = float(times_data)
        else:
            all_time_msg = ''

        if bool(arry) and len(arry) < msg_on_after_iters and len(arry) > (msg_on_after_iters-3):
            send_telegram_message(message=f'[RESET], Before start crashed! | Crashed: {str(times_data)} {all_time_msg}')
        
        elif bool(arry) and len(arry) > msg_on_after_iters and WinAmount>1:
            send_telegram_message(message=f"[RESET], \n| Crashed: {str(times_data)} |\nExit at: {invest} | Total: {total}\nProfit: Rs. {WinAmount} {all_time_msg}") 
        arry = []
    
    return arry, all_time_max

async def connect_to_websocket(uri, message1, message2, arry, all_time_max, i):  
    async with websockets.connect(uri) as websocket:
        await websocket.send(message1)
        await websocket.send(message2)
        check_hour_flag = 0
        print(f"Sent: {message1}")
        print(f"Sent: {message2}")

        while True:
            check_hour = datetime.datetime.now().strftime("%H")

            if int(check_hour) != check_hour_flag:
                send_telegram_message(message=f'[RUNNING] Automation working fine!')
                check_hour_flag = int(check_hour)
            
            try:
                response = await websocket.recv()

            except (websockets.exceptions.ConnectionClosed, asyncio.TimeoutError, Exception) as e:
                send_telegram_message(message=f'[SKIP] Err Frame({i}) Reconnecting...')                 
                return arry, all_time_max

            try:
                global amounts, total, to_file, max_invest_cap
                if '"target":"OnCrash"' in response:
                    response = re.sub(r'[^\x20-\x7E]', '', response)
                    payload = json.loads(response)
                    # func_call = payload['arguments'][0]['l']
                    times = payload['arguments'][0]['f']

                    # ts = payload['arguments'][0]['ts']
                    # print(times)
                    if to_file:
                        current_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") 
                        csv_data = f"{float(times):.2f},{current_date}\n"
                        # print(f'{float(times):.2f} : {current_date}')
                        with open(csv_file_path, 'a') as file:
                            file.write(csv_data)
                    arry, all_time_max = check_and_msg_tel_func(arry=arry, times_data=times, amounts=amounts, all_time_max=all_time_max, max_invest_cap=max_invest_cap)
                    
            except Exception as e:
                send_telegram_message(message=f'[FAILED] Error logic: {str(e)}')
                return arry, all_time_max

if __name__=='__main__':
    if to_file:
        try:
            with open(csv_file_path, 'r') as file:
                data = file.read()
        except:
            with open(csv_file_path, 'w+') as file:
                file.write('Times,Date\n')
    # print(amounts_num)
    send_telegram_message(message=f'Amounts: {amounts_num}\nTotal amount: Rs.{total_amount}')
    
    uri = "wss://1xbet.com/games-frame/sockets/crash?whence=50&fcountry=71&ref=1&gr=70&appGuid=00000000-0000-0000-0000-000000000000&lng=en"

    message1 = '{"protocol":"json","version":1}'
    message2 = '{"arguments":[{"activity":30,"currency":99}],"invocationId":"31","target":"Guest","type":1}'

    for i in range(1000):
        try:
            arry, all_time_max = asyncio.get_event_loop().run_until_complete(connect_to_websocket(uri, message1, message2, arry, all_time_max, i))
        except Exception as e:
            send_telegram_message(message=f'[FAILED] Main Error: {str(e)} _ {i}')

    print('-Exit code 0')
