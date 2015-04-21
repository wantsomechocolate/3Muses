import stripe, os

stripe.api_key = os.environ['STRIPE_SECRET']

charge=stripe.Charge.retrieve("ch_15p7j2BJewwJxtz7OUKzgdSP")
