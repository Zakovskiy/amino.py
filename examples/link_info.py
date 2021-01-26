# /Zakovskiy/amino.py/
# get info by thread link

from amino import Client

Amino = Client("email", "password");

link 		   = input("Link on thread: ");

info 		   = Amino.get_from_code(link)["linkInfoV2"]["extensions"]["linkInfo"];

community_id   = info["ndcId"];
thread_id      = info["objectId"];

print(f"Community id: {community_id}");
print(f"Thread id: {thread_id}");