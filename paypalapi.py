import paypalrestsdk
from paypalrestsdk import Payment

# Set up PayPal API credentials
paypalrestsdk.configure({
    "mode": "sandbox",  # Change to "live" for production
    "client_id": "AVX6BvepwVhN2dKIg4yvE20E-bTSwHyG2NiPjtbq5-yIWlYpIeWQ3qsEdP8t_K4Sj8PtVOa2_HrOdY54",
    "client_secret": "EHg1Xyzsm_Bhbtqmcigd1C9VN1EACmwQQxtk3deAdZX14FrADIVaqmlnOj9mDrwPh0J5ZLl2dWRTjQ5M" 
})

# Create Payment object
payment = Payment({
    "intent": "sale",
    "payer": {
        "payment_method": "paypal"
    },
    "transactions": [{
        "amount": {
            "total": "10.00",
            "currency": "USD"
        }
    }],
    "redirect_urls": {
        "return_url": "http://example.com/your_redirect_url",
        "cancel_url": "http://example.com/your_cancel_url"
    }
})

# Create Payment
if payment.create():
    print("Payment created successfully")
    # Redirect the user to payment approval url
    for link in payment.links:
        if link.method == "REDIRECT":
            redirect_url = link.href
            print("Redirect for approval: %s" % (redirect_url))
else:
    print(payment.error)
