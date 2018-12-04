"""
export FLASK_ENV=development
export FLASK_APP=informer:app
flask run
"""


"""
ngrok http 127.0.0.1:5000 -subdomain=vziks -region=eu

curl "http://127.0.0.1:5000/errors" -H "Content-Type: application/json" -d "{\"id\": \"1\" ,\"email\" : \"mail@mail.ru\",\"type\" : \"subscribe\"}"

https://api.telegram.org/bot<id>/setWebhook?url=https://vziks.eu.ngrok.io/bot/

"""
curl -i -X POST \
   -H "Content-Type:application/json" \
   -H "X-Viber-Auth-Token:<id>" \
   -d \
'{
   "url":"https://vziks.eu.ngrok.io/bot/",
   "event_types":[
      "failed",
      "conversation_started"
   ]
}' \
 'https://chatapi.viber.com/pa/set_webhook'
"""