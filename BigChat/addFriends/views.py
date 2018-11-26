# from django.shortcuts import render
import datetime, json

from django.http import HttpResponse, JsonResponse, QueryDict

from django.views.generic import View

from auth.models import Users, ChatList
from Contact.models import Contact
from addFriends.models import FriendRequest, chatMember

def index(request):
    return HttpResponse("AddFriends Index")


class FriendRequests(View):

    @classmethod
    def get(self, request):
        return JsonResponse(getFriendRequests(request))
    @classmethod
    def post(self, request):
        return JsonResponse(friendController(request, "sendAdd"))
    @classmethod
    def delete(self, request):
        return JsonResponse(friendController(request, "remove"))
    @classmethod
    def put(self, request):
        return JsonResponse(friendController(request, "add"))

def getFriendRequests(request):
    token = request.GET.get("token")
    # print ("GET")
    try:
        # print ("looking for user: " + token)
        user = Users.objects.get(token=token)
        # print ("user found")
        friendRequests = None
        if not FriendRequest.objects.filter(user_id=user.user_id).exists():
            friendRequests = FriendRequest(user_id=user.user_id)
            friendRequests.save()
        else:
            friendRequests = FriendRequest.objects.get(user_id=user.user_id)

        friendRequests_status = {"success": 200, "sent": [], "recieved": []}

        # print (friendRequests)
        # print (user)
        if friendRequests.friend_requests_emails_sent is not None:
            for i in friendRequests.friend_requests_emails_sent:
                friendRequests_status["sent"].append(i)

        if friendRequests.friend_requests_emails_recieved is not None:
            for i in friendRequests.friend_requests_emails_recieved:
                friendRequests_status["recieved"].append(i)

        # print (friendRequests_status)
        return friendRequests_status
    except Exception as e:
        # print (e)
        return {"error": "User or FriendRequests not found"}



def friendController(request, requestType):
     token = None
     email = None
     friendEmail = None

     token = request.GET.get("token")
     email = request.GET.get("email")
     friendEmail = request.GET.get("friendEmail")

     if token is None:
         if requestType is "sendAdd":
              token = request.POST.get("token")
              email = request.POST.get("email")
              friendEmail = request.POST.get("friendEmail")
              # token = request.GET.get("token")
              # email = request.GET.get("email")
              # friendEmail = request.GET.get("friendEmail")
         else:
             try:
                 jsonObj = json.loads(request.body)
                 token = jsonObj['token']
                 email = jsonObj['email']
                 friendEmail = jsonObj['friendEmail']
             except Exception as e:
                 print(e)
                 return {"error" : "Failed to parse data"}
     # print ("OTHERS")
     # print (token)
     # print(email)
     # print(friendEmail)
     
     try:
         # print ("Inside TRY")
         user = Users.objects.get(email=email, token=token)
         friend = Users.objects.get(email=friendEmail)
         # print ("Got users...")

         user_id = user.user_id
         friend_id = friend.user_id
         # print ("Got ids...")

         if not Contact.objects.filter(user_id=user_id).exists():
             contacts = Contact(user_id=user_id, date_added= datetime.datetime.now())
             contacts.save()

         if not Contact.objects.filter(user_id=friend_id).exists():
             contactsFriend = Contact(user_id=friend_id, date_added= datetime.datetime.now())
             contactsFriend.save()

         contacts = Contact.objects.get(user_id=user_id)
         contactsFriend = Contact.objects.get(user_id=friend_id)
         # print ("Got contacts")

         if not FriendRequest.objects.filter(user_id=user_id).exists():
             friendRequests = FriendRequest(user_id=user_id)
             friendRequests.save()

         if not FriendRequest.objects.filter(user_id=friend_id).exists():
             friend_friendRequests = FriendRequest(user_id=friend_id)
             friend_friendRequests.save()

         friendRequests = FriendRequest.objects.get(user_id=user_id)
         friend_friendRequests = FriendRequest.objects.get(user_id=friend_id)

         # print ("Got data...")

         if requestType == "add":
             # print ("Adding...")
             try:
                 if friendEmail in friendRequests.friend_requests_emails_recieved and email in friend_friendRequests.friend_requests_emails_sent:
                     addFriend(contacts, friend_id)
                     addFriend(contactsFriend, user_id)
                     # create new chat with 2 members
                     chatmem = chatMember(member_id=[user_id,friend_id], date_added= datetime.datetime.now())
                     chatmem.save()

                     cm = chatMember.objects.filter(member_id__contains=[user_id, friend_id]).filter(member_id__len=2).order_by('-date_added')[:1]
                     cm = cm[0]
                     # print(chatmem.id)
                     chatId = "chat_table_" + str(cm.id)
                     # add each other to chatlist
                     chatlist =  ChatList(user_id= user_id, chat_id=chatId, message="New Friend!", message_type=1, flag=1, name=friend.user_name, date_added=datetime.datetime.now(), date_modified=datetime.datetime.now())
                     chatlist.save()
                     # print(chatId)
                     chatlist =  ChatList(user_id= friend_id, chat_id=chatId, message="New Friend!", message_type=1, flag=1, name=user.user_name, date_added=datetime.datetime.now(), date_modified=datetime.datetime.now())
                     chatlist.save()
                     friendRequests.friend_requests_emails_recieved.remove(friendEmail)
                     friend_friendRequests.friend_requests_emails_sent.remove(email)

                 else:
                     return {"error": "Trying to add user who doesn't want to add you..."}
             except Exception as e:
                 # print(e)
                 return {"error": "FriendRequests entry does not exist for one or both of the users in question."}
         elif requestType == "remove":
             # print ("Removing...")
             cm1 = chatMember.objects.filter(member_id=[user_id,friend_id])
             cm2 = chatMember.objects.filter(member_id=[friend_id,user_id])

             for i in cm1:
                 ChatList.objects.filter(chat_id="chat_table_"+str(i.id)).delete()

             for i in cm2:
                 ChatList.objects.filter(chat_id="chat_table_"+str(i.id)).delete()
             # TODO: remove chat history or keep it?
             removeFriend(contacts, friend_id)
             removeFriend(contactsFriend, user_id)
             friendRequests.friend_requests_emails_recieved.remove(friendEmail)
             friend_friendRequests.friend_requests_emails_sent.remove(email)

         elif requestType == "sendAdd":
             # print ("Sending add...")

             # print ("Checking if they exist...")
             if not FriendRequest.objects.filter(user_id=user_id).exists():
                 # print("creating friend request...")
                 friendRequests = FriendRequest(user_id=user_id)
                 friendRequests.save()

             if not FriendRequest.objects.filter(user_id=friend_id).exists():
                 # print("creating friend request...")
                 friend_friendRequests = FriendRequest(user_id=friend_id)
                 friend_friendRequests.save()

             # print ("Created requests if null")
             if friendRequests.friend_requests_emails_sent:
                 if friendEmail not in friendRequests.friend_requests_emails_sent:
                     friendRequests.friend_requests_emails_sent.append(friendEmail)
             else:
                 friendRequests.friend_requests_emails_sent = [friendEmail]

             if friend_friendRequests.friend_requests_emails_recieved:
                 if email not in friend_friendRequests.friend_requests_emails_recieved:
                     friend_friendRequests.friend_requests_emails_recieved.append(email)
             else:
                 friend_friendRequests.friend_requests_emails_recieved = [email]

         else:
             raise Exception()

         friendRequests.save()
         friend_friendRequests.save()
         contacts.save()
         contactsFriend.save()

         return {"success" : 200}
     except Exception as e:
         print (e)
         return {"error" : "Failed to modify contacts"}

def addFriend(contacts, friend_id):
     # NULL check
     if contacts.friend_id:
         if friend_id not in contacts.friend_id:
             contacts.friend_id.append(friend_id)
             contacts.save()
     else:
         contacts.friend_id = [friend_id]
         contacts.save()


def removeFriend(contacts, friend_id):
     # NULL check
     if contacts.friend_id and friend_id in contacts.friend_id:
         contacts.friend_id.remove(friend_id)
         contacts.save()
