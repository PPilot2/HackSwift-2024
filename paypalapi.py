from flask import Flask, request, redirect
import paypalrestsdk
from paypalrestsdk import Payment

app = Flask(__name__)

# Set up PayPal API credentials
paypalrestsdk.configure({
    "mode": "sandbox",  # Change to "live" for production
    "client_id": "AVX6BvepwVhN2dKIg4yvE20E-bTSwHyG2NiPjtbq5-yIWlYpIeWQ3qsEdP8t_K4Sj8PtVOa2_HrOdY54",
    "client_secret": "EHg1Xyzsm_Bhbtqmcigd1C9VN1EACmwQQxtk3deAdZX14FrADIVaqmlnOj9mDrwPh0J5ZLl2dWRTjQ5M" 
})

# Define a function to create a Payment with variable amount
def create_payment(amount):
    payment = Payment({
        "intent": "sale",
        "payer": {
            "payment_method": "paypal"
        },
        "transactions": [{
            "amount": {
                "total": "{:.2f}".format(amount),  # Format amount to two decimal places
                "currency": "USD"
            }
        }],
        "redirect_urls": {
            "return_url": "http://example.com/your_redirect_url",
            "cancel_url": "http://example.com/your_cancel_url"
        }
    })
    return payment

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Get amount from the form
        amount = float(request.form['amount'])  # Assuming the form field is named 'amount'
        
        # Create Payment with the specified amount
        payment = create_payment(amount)
        
        # Create Payment
        if payment.create():
            # Redirect the user to payment approval url
            for link in payment.links:
                if link.method == "REDIRECT":
                    redirect_url = link.href
                    return redirect(redirect_url)
        else:
            error_message = payment.error
            return f"Error creating payment: {error_message}"

    # Render the form for users to input the amount
    return '''
        <form method="post">
            <label for="amount">Amount:</label><br>
            <input type="text" id="amount" name="amount"><br>
            <input type="submit" value="Submit">
        </form>
    '''

if __name__ == '__main__':
    app.run(debug=True)
