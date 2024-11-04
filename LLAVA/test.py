from llava_chatbot import chatbot

print("Starting chat")
ans = chatbot.start_new_chat(img_path="https://images.unsplash.com/photo-1686577353812-6cbc7fce384b?q=80&w=1887&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
                             prompt="Would the fish depicted in the image float if thrown in water? Think step by step.")

print("First question answered")
print(ans)

ans = chatbot.continue_chat("What material could be used to make a fish sculpture that floats on water?")

print("Second question answered")
print(ans)
