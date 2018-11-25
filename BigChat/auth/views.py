# from django.shortcuts import render

# Create your views here.
import requests, json, datetime
# , uuid

# from django.db import IntegrityError
# from django.core import serializers
# from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.http import HttpResponse, JsonResponse
from django.views.generic import View
from Contact.models import Profile, Contact
# from django.db import connection

# from . import models
from .models import Users

def index(request):
    return HttpResponse("Auth POST")


class Authenticate(View):
    # model = models.Users
    @classmethod
    def get(self, request):
        return JsonResponse(processAuthRequest(request))
    # @classmethod
    # def post(self, request):
    #     return JsonResponse(processAuthRequest(request))

class updateUserToken(View):

    @classmethod
    def post(self, request):

        status = processUpdateTokenRequest(request)
        if status is True:
            return HttpResponse("updateUserToken GET")
        else:
            return JsonResponse(status)


def processAuthRequest(request):
     name = request.GET.get("name")
     email = request.GET.get("email")
     app_id = request.GET.get("app_id")
     token = request.GET.get("token")
     authType = request.GET.get("authType")

     status = auth(name, email, app_id, token, authType)

     if 'success' in status:
         # print ("auth success")
         return checkForNewUser(email, token)
     else:
         # print ("auth fail")
         return status



def processUpdateTokenRequest(request):
    name = request.POST.get("name")
    email = request.POST.get("email")
    app_id = request.POST.get("app_id")
    old_token = request.POST.get("old_token")
    new_token = request.POST.get("new_token")
    authType = request.POST.get("authType")

    if old_token is None:
         return {'error': 'Cannot process with no old token'}
    if new_token is None:
         return {'error': 'Cannot process with no new token'}

    return updateToken(name, email, app_id, old_token, new_token, authType)


def auth(name, email, app_id, token, authType):

     # name can be null, not mandatory...
     #  if name is None:
        #  return { 'error' : 'Cannot process with no name' }

     # print (name)
     # print (email)
     # print (app_id)
     # print (token)
     # print (authType)

     if email is None:
         return { 'error' : 'Cannot process with no email' }

     # Can be obtained from the access token
     #  if app_id is None:
        #  return JsonResponse( { 'error' : 'Cannot process with no app_id' } )

     if token is None:
         return {'error': 'Cannot process with no token'}

     if authType is None:
         return {'error': 'Cannot process with no authType'}


     try:

         if authType == "google":
             url = "https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=" + token
             req = requests.post(url)

             jsonReq = json.loads(req.text)

             if 'error' in jsonReq:
                 return jsonReq

             f = open('auth/google_key.json')
             googleKey = json.load(f)

             f = open('auth/google_key.json.old')
             googleKeyOld = json.load(f)

             if 'issued_to' in jsonReq and 'email' in jsonReq and 'KEY' in googleKey and 'KEY' in googleKeyOld:
                 if (jsonReq['issued_to'] == googleKeyOld['KEY'] or jsonReq['issued_to'] == googleKey['KEY']) and jsonReq['email'] == email:
                     return {"success": "BigChat true"}
                 else:
                     return {"error": "BigChat false"}
             else:
                 return {"error": "Missing data from Google's API..."}

             # Success Message Example
             #  {
             #     "issued_to": "KEY",
             #     "audience": "KEY",
             #     "user_id": "user.id",
             #     "scope": "https://www.googleapis.com/auth/plus.me https://www.googleapis.com/auth/userinfo.profile https://www.googleapis.com/auth/userinfo.email",
             #     "expires_in": 3389,
             #     "email": "cpen321.bigchat@gmail.com",
             #     "verified_email": true,
             #     "access_type": "online"
             # }

             # Error Message Example
             # {
             #      "error": "invalid_token",
             #      "error_description": "Invalid Value"
             # }

         elif authType == "facebook":
             url = "https://graph.facebook.com/me/?fields=name,id,email&access_token=" + token
             req = requests.get(url)

             url = "https://graph.facebook.com/app/?access_token=" + token
             req_app_id = requests.get(url)

             jsonReq = json.loads(req.text)
             jsonReq_app_id = json.loads(req_app_id.text)

             # print(jsonReq)
             # print(jsonReq_app_id)

             # TODO: Remove
             #  return {"success": "BigChat true"}


             if 'error' in jsonReq:
                 return {"error": jsonReq['error']['message'] }

             if 'error' in jsonReq_app_id:
                 return {"error": jsonReq_app_id['error']['message'] }

             # print ("Test0")
             f = open('auth/facebook_key.json')
             facebookKey = json.load(f)

             f = open('auth/facebook_key.json.old')
             facebookKeyOld = json.load(f)
             # print ("Test1")
             jsonReq['email'] = jsonReq['email'].replace("\u0040", "@")

             # print("Facebook auth 1")
             if 'id' in jsonReq_app_id and 'KEY' in facebookKey and 'email' in jsonReq and 'KEY' in facebookKeyOld:
                 if (jsonReq_app_id['id'] == facebookKey['KEY'] or jsonReq_app_id['id'] == facebookKeyOld['KEY']) and jsonReq['email'] == email:
                     return {"success": "BigChat true"}
                 else:
                     return {"error": "BigChat false"}
             else:
                 return {"error": "Missing data from Facebook's API..."}

            # Success Message Examples
            # {
            #    "name": "Harminder Kandola",
            #    "id": "USER_ID",
            #    "email": "harminderk\u0040hotmail.ca"
            # }

            #  {
            #    "link": "https://www.facebook.com/games/?app_id=KEY",
            #     "name": "BigChat",
            #    "id": "KEY"
            # }

            # Error Message Example
            # {"error":{"message":"Expected 1 '.' in the input between the postcard and the payload","type":"OAuthException","code":190,"fbtrace_id":"GYHrVZqj0Ne"}}

         else:
             return {'error': "Authenticate GET - Invalid Authentication Type."}

     except Exception as e:
         # print (e)
         return {"error": "Caught an exception..."}


# Checks and adds new users
def checkForNewUser(email, token):

    user_exists = findUser(email, token)

    if user_exists == False:
        # print ("adding new user...")
        return addUser(email, token)
    else:
        return {"success": "user exists", "newUser": 0}


def findUser(email, token):

    # Get Users...
     try:
         # Throws an expection if zero or more than one found
         # print ("finding user...")
         user = Users.objects.get(email=email)
         user.token = token
         user.save()
         # print ("updated token...")
         return True
     except Exception as e:
         # print("Caught an exp in findUser")
         # print (e)
         return False




def updateToken(name, email, app_id, old_token, new_token, authType):
    # Get Users...
     try:
         status = auth(name, email, app_id, new_token, authType)
         if 'error' in status:
             return status
         user = Users.objects.get(email=email)
         user.token = new_token
         user.save()
         return {'status': "Succesfully updated token"}
     except Exception:
        return {'error': "Failed to update token. User not found."}


def addUser(email, token):
    # Adds Users...
     try:
         # Adding the user entry
         # print ( "user: ")
         user = Users(email=email, token=token)
         user.save()
         # print ( "user: ")

         user_id = user.user_id
         # user.chat_list_id = "chat_list_" + str(user_id)
         user.save()

         # i = open('Contact/defaultImg.json')
         # print("opened")
         # print(i['image'])
         # img = json.load(i)
         # prinf("load")
         # print(img['image'])
         # print(defaultImg['image'])
         profile = Profile(email=email, name=email, profile_img_str=defaultImg['image'])
         profile.save()

         contact = Contact(user_id=user_id, friend_id=[], date_added=datetime.datetime.now())
         contact.save()
         # print (user.chat_list_id)
         # Creating the chat list table
         # cursor = connection.cursor()
         # cursor.execute("CREATE TABLE "+ user.chat_list_id +" ( id SERIAL, chat_id text NOT NULL, message text DEFAULT NULL, message_type integer DEFAULT NULL, date_added TIMESTAMP DEFAULT NULL, date_modified TIMESTAMP DEFAULT NULL, flag integer DEFAULT 0, name text DEFAULT NULL, PRIMARY KEY(id))", [user.chat_list_id])

         return {'success': "Succesfully added new user","newUser": 1}

     except Exception as exp:
         # print (exp)
         return {'error': "Failed to add user."}


defaultImg = {
    "image": "%2F9j%2F4AAQSkZJRgABAQAASABIAAD%2F4QBYRXhpZgAATU0AKgAAAAgAAgESAAMAAAABAAEAAIdpAAQAAAABAAAAJgAAAAAAA6ABAAMAAAABAAEAAKACAAQAAAABAAABLKADAAQAAAABAAABLAAAAAD%2F7QA4UGhvdG9zaG9wIDMuMAA4QklNBAQAAAAAAAA4QklNBCUAAAAAABDUHYzZjwCyBOmACZjs%2BEJ%2B%2F8AAEQgBLAEsAwEiAAIRAQMRAf%2FEAB8AAAEFAQEBAQEBAAAAAAAAAAABAgMEBQYHCAkKC%2F%2FEALUQAAIBAwMCBAMFBQQEAAABfQECAwAEEQUSITFBBhNRYQcicRQygZGhCCNCscEVUtHwJDNicoIJChYXGBkaJSYnKCkqNDU2Nzg5OkNERUZHSElKU1RVVldYWVpjZGVmZ2hpanN0dXZ3eHl6g4SFhoeIiYqSk5SVlpeYmZqio6Slpqeoqaqys7S1tre4ubrCw8TFxsfIycrS09TV1tfY2drh4uPk5ebn6Onq8fLz9PX29%2Fj5%2Bv%2FEAB8BAAMBAQEBAQEBAQEAAAAAAAABAgMEBQYHCAkKC%2F%2FEALURAAIBAgQEAwQHBQQEAAECdwABAgMRBAUhMQYSQVEHYXETIjKBCBRCkaGxwQkjM1LwFWJy0QoWJDThJfEXGBkaJicoKSo1Njc4OTpDREVGR0hJSlNUVVZXWFlaY2RlZmdoaWpzdHV2d3h5eoKDhIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uLj5OXm5%2Bjp6vLz9PX29%2Fj5%2Bv%2FbAEMAAgICAgICAwICAwQDAwMEBQQEBAQFBwUFBQUFBwgHBwcHBwcICAgICAgICAoKCgoKCgsLCwsLDQ0NDQ0NDQ0NDf%2FbAEMBAgICAwMDBgMDBg0JBwkNDQ0NDQ0NDQ0NDQ0NDQ0NDQ0NDQ0NDQ0NDQ0NDQ0NDQ0NDQ0NDQ0NDQ0NDQ0NDQ0NDf%2FdAAQAE%2F%2FaAAwDAQACEQMRAD8A%2FRSiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigD%2F9D9FKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKAP%2F0f0UooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooA%2F%2FS%2FRSiiigAooooAKKKKACiiigAooooAKKKKACiiigAoqe1tbm9nS1s4nmmkOFRBlifpXrGifCLVLrE2tzrZxnB8uPDyH2J%2B6P1oA8gp8cckp2xIzn0UE%2Fyr6u0z4d%2BFNMAIsxcyDHz3B8w%2Fkfl%2FSuwgtba2XbbRJEPRFCj9KAPi9dH1dxuSxumHqIXP%2FstRS6dqMGTPazx46742X%2BYFfblFAHwv3wevpRX2je6DomoqUvrGCYHu0Yz%2BeM15%2Fq3wk0G7BfTJJLGTsM%2BZH%2BTcj86APm6iuy1%2FwACeIfDytPcwia2U%2F6%2BE7lA%2FwBodV%2FEYrjaACiiigAooooAKKKKACiiigAooooAKKKKACiiigD%2F0%2F0UooooAKKKKACiiigAooooAKKKKACiiigArtPCfgnU%2FFMvmJ%2B4skbElww%2FMIP4m%2FQd6u%2BBPBMvie7%2B1XgKadA37xhwZWH8Cn%2BZ7fWvqC1tbeyt47W0jWKGJQqIowABQBj6D4Z0fw5biDTYArEfPK3Mjn3b%2Bg4rfoooAKKKKACiiigAooooAQgMCrDIPBB715T4u%2BGNjqqvfaGFtLz7xj6RSfh%2FCfcceter0UAfEN7ZXenXMlnexNDNEcMjDkH%2FAD3qrX1p4x8G2XimzPAivolPkT%2F%2Byt6qf07e%2FwAq31ldabdy2N7GYpoWKup7H%2FA9qAKtFFFABRRRQAUUUUAFFFFABRRRQAUUUUAf%2F9T9FKKKKACiiigAooooAKKKKACiiigAre8N6Dc%2BI9Wh0y3yAx3SyYyI4x1b%2Bg96wa%2BnPhh4dTSdDXU5V%2F0rUAHJP8MX8C%2Fj1P1oA7%2FTtPtNKsYdPskEcMChVH9T6k9SfWrtFFABRRRQAUUUUAFFFFABRRRQAUUUUAFeWfEvwgus2B1mxT%2FTbRcsFHMsQ6j3K9R%2BIr1OjrwaAPheiu5%2BIPh5PD2vuluMW10PPiH93J%2BZfwPT2IrhqACiiigAooooAKKKKACiiigAooooA%2F%2FV%2FRSiiigAooooAKKKKACiiigAooooA2fD2lnWdbstMHSeVQ%2Fsg5Y%2FkDX2aiJGixxgKqAKoHQAdBXzj8IbFbjxBcXrDItbc7f96Q4%2FkDX0hQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAeZ%2FFXSBf%2BGzfIuZbBxID32N8rD%2BR%2FCvmOvtvUbNNQ0%2B5sZBlbiJ4zn%2FaBFfEzo0btG33kJU%2FUcUANooooAKKKKACiiigAooooAKKKKAP%2F9b9FKKKKACiiigAooooAKKKKACiiigD334MQgWep3GOWliTP%2B6pP%2Fs1e11438GmB0nUV7i5Un6FB%2FhXslABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAV8Y%2BI4Rb%2BINSgAwEuphj%2FgRr7Or458XMG8U6sy8g3cv%2FoRoA52iiigAooooAKKKKACiiigAooooA%2F%2FX%2FRSiiigAooooAKKKKACiiigAooooA9w%2BDF2BLqliepEUo%2FDcp%2FmK94r5W%2BGmpjTvFlujnCXatbt9W5X%2FAMeAr6poAKKKKACiiigAooooAKKKKACiiigAooooAKKKKAEJABJ6CvibU7n7ZqV3d%2F8APaeST8GYmvrbxfqY0nw3f3ucMIWROcfO%2FwAq%2Fqa%2BO6ACiiigAooooAKKKKACiiigAooooA%2F%2F0P0UooooAKKKKACiiigAooooAKKKKAJYJ5LaeO5hO2SJ1dCOzKcivs3Q9Ui1rSLXVIuBcRhiOu1ujD8DkV8W17J8KPE%2F2S7bw7ePiG5Je3z0WXuv%2FAh%2Bo96APoSiiigAooooAKKKKACiiigAooooAKKKKACiis7VtTtdG06fUrxtsUCFj6k9gPcngUAeOfGDW%2BLXw%2FEev%2BkTYP1CA%2FqfyrwutLV9Uuta1KfU7xsyzuWPoB0Cj2A4rNoAKKKKACiiigAooooAKKKKACiiigD%2F0f0UooooAKKKKACiiigAooooAKKKKACno7xOssbFHQhlYcEEcgimUUAfVPgPxjF4lsBb3LBdQt1AlX%2B%2BBwHH17%2Bhrv6%2BJNP1C80q8iv7CQxTwnKsP1BHcHuK%2BnvBvjqw8TQrbzlbfUEHzwk4D46smeo9uooA72iiigAooooAKKKKACiiigAooqKeeG2iee4dY44xuZ3OFAHck0APZlRS7kKqjJJ4AA7mvmP4ieMv%2BEivBp9g5%2Fs%2B2bgjpLION30HRfzq%2FwCO%2FiI%2Bsh9I0Vilj92WXo03sPRP1NeTUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAf%2F0v0UooooAKKKKACiiigAooooAKKKKACiiigAp8ckkMiywsySIQyspwQR0II712nhrwFrniTE6J9ltDj9%2FKCAw%2F2B1b%2BXvXvHh74feH9A2zCL7XdD%2FltOAxB%2F2V6L%2FP3oAwvAXiXxZqccdvq2nyTW%2BBtvTiPjtkNjf9V5r1agAAYFFABRRRQAUUUUAFFFFAFPULi4tLOS4tbZruVBlYUIUsfqxAFfLnjPxP4l1e5Npq8cljCpytptKgehbPLn36elfV9UdQ0zT9VgNtqNvHcRt%2FC65%2FI9QfpQB8S0V7r4h%2BES%2FPc%2BHJsd%2Fs0x4%2Biv%2FQ%2FnXit7Y3mnXDWl%2FC8EydUkGD9fce9AFSiiigAooooAKKKKACiiigAooooAKKKKAP%2FT%2FRSiiigAooooAKKKKACiiigAoorQ0vS77Wb2PT9OiMs0nQDoAOpJ7AetAFa1tbi9uEtbSNpppDtREGWJ%2BlfQPhD4X2tgE1DxCFuLnhlg6xRnr8395v0%2BtdX4Q8F2Hha2DgCa%2BkH72cjn%2FdX0X9T3rtaAEVVVQqgAAYAHAApaKKACiiigAooooAKKKKACiiigAooooAKw9d8OaT4itTbanCHx9yQcSIfVW%2Fp0rcooA%2BTvFvgfU%2FC8hlObiyY4SdR0z0Dj%2BE%2Foa4ivuOeCG5heC4RZI5AVZGGQQexBr5w8d%2FD2XQy%2Bq6OjSWHV06tB%2FUp79u9AHldFFFABRRRQAUUUUAFFFFABRRRQB%2F%2FU%2FRSiiigAooooAKKKKACiilAJOByTwBQBasLG61O8isLKMyzzMFRR6n19AO5r6t8HeEbTwrYeWuJLuYAzzY6n%2B6v%2ByO351h%2FDrwaugWI1K%2FjH9oXKgkEcwxnoo9Cerfl2r0ygAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACmsqupRwGVgQQRkEHsadRQB80fEHwK2gynVtMUnT5W%2BZR1hc9v909j26V5dX3Dc20F5byWt1GssUqlXRhkEHtXyd408KzeFtVMABa0my9vIe691J%2FvL%2BvWgDj6KKKACiiigAooooAKKKKAP%2FV%2FRSiiigAooooAKKKKACvWfhd4UGqX39u3qZtbN8RKejzDn8l6%2FWvNdL0251fUbfTLQZluHCD0HqT7AcmvsfSNLttG0230y1GI4EC5%2FvHux9yeaANKiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigArnPFPh638S6RLp02Fk%2B%2FDJ%2FckHQ%2FQ9D7V0dFAHw%2Fd2s9jdS2d0uyaBzG6nsynBqvXuPxa8NbTH4ltFGDtiuQPX%2BF%2F6H8K8OoAKKKKACiiigAooooA%2F%2F9b9FKKKKACiiigAooqa3glup47WBS0kzqiAd2Y4FAHt%2FwAIdAXbceIp1ycmCDI6Y%2B%2B348D869zrL0XTItG0q10yH7tvGqE4xlv4j%2BJya1KACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooApalYW%2BqWE%2Bn3S7orhCjD69%2FqOor4z1TT5tK1G5024%2FwBZbSNGT64PB%2FEc19s18%2B%2FF%2FRPIvrbXYV%2BS4XyZcD%2BNOVJPuvH4UAeM0UUUAFFFFABRRRQB%2F9f9FKKKKACiiigAr0f4XaT%2FAGl4mS5kXdFYoZjnpvPyp%2Bpz%2BFecV9G%2FCDTfs%2Bh3GosPmu5iAf8AYiGB%2BpNAHrdFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFcl440n%2B2fDN7bKu6WNPOi%2FwB%2BPn9RkfjXW0hAIIPINAHwxRW14j07%2ByddvtPxhYZ3C%2F7hOV%2FQisWgAooooAKKKKAP%2F9D9FKKKKACiiigAr7G8I2P9neGtOtMYZbdGb%2Fecbj%2Bpr5EsLc3d9bWo%2FwCW0yR%2F99MBX22iqiKijAUAAewoAdRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQB80fFux%2BzeJkulGFurdWJ9WQlT%2BmK8ur334zWoaz029A5SWSIn2cAj%2FwBBrwKgAooooAKKKKAP%2F9H9FKKKKACiiigDp%2FBcH2jxZpUZGR9pVz%2FwDLf0r7Br5Q%2BG6hvGVhnt5h%2FHY1fV9ABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQB5l8WYPN8JmTGTDcxP9M5X%2BtfMlfVvxKUN4Nvs9vLI%2Bu9a%2BUqACiiigAooooA%2F9k%3D"

}

