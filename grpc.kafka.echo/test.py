import json

message_list = []

print("message num: ")
n = int(input())

for i in range(1, n+1):
    message = {
        "message":  f"test message{i}"
    }
    message_list.append(message)

json_messages = json.dumps(message_list, indent=4)

with open('messages.json', 'w') as file:
    file.write(json_messages)
