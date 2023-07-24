from django.conf import settings
import stripe


def get_or_create_stripe_customer(user):
    if not user.company.stripe_customer_id:
        stripe_customer = stripe.Customer.create(
            name=user.company.name,
            email=user.email,
            metadata={'company_id': user.company.id, 'user_id': user.id}
        )
        user.company.set_stripe_customer_id(stripe_customer.id)
    else:
        stripe_customer = stripe.Customer.retrieve(user.company.stripe_customer_id)
    return stripe_customer


def create_stripe_subscription(customer, price, domain, user):
    stripe_subscription = stripe.Subscription.create(
        customer=customer.id,
        off_session=True,
        payment_behavior='default_incomplete',
        items=[{'price': price.stripe_price_id}],
        expand=['latest_invoice.payment_intent'],
        metadata={'company_id': user.company.id, 'domain': domain.id, 'user_id': user.id}
    )
    domain.set_stripe_subscription_id(stripe_subscription.id)
    return stripe_subscription, True


def update_stripe_subscription(customer, price, domain, user):
    stripe_subscription = stripe.Subscription.retrieve(domain.stripe_subscription_id)
    if stripe_subscription.status == 'incomplete':
        stripe.Subscription.delete(stripe_subscription.id)
        stripe_subscription = create_stripe_subscription(customer, price, user)
        is_created = True
    else:
        stripe_subscription = stripe.Subscription.modify(
            stripe_subscription.id,
            cancel_at_period_end=False,
            proration_behavior='always_invoice',
            items=[{'id': stripe_subscription['items']['data'][0].id, 'price': price.stripe_price_id}],
            metadata={'company_id': user.company.id, 'domain_id': domain.id, 'user_id': user.id}
        )
        is_created = False

    return stripe_subscription, is_created
