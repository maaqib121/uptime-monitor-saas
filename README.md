# Domain Watcher – Uptime & Landing Page Monitoring SaaS

**Domain Watcher** is a SaaS platform built with Django and Django REST Framework that allows users to monitor the uptime status of their domains’ landing pages and receive alerts via email and SMS. Users connect their Google Analytics account, fetch the top 100 landing pages per domain, and subscribe to monitor their uptime in real time.

## 🚀 Features
- User registration, authentication, and organization (team) management
- Domain and landing page management
- Google Analytics integration to fetch top 100 landing pages
- Subscription-based billing via Stripe (monthly/yearly per domain or landing page)
- Uptime monitoring with email and SMS alerts
- Invite teammates to manage domains
- Multi-tenant support
- Historical logs of uptime and downtime

## ⚙️ Tech Stack
- **Backend:** Django, Django REST Framework
- **Auth:** JWT-based authentication with organization-level multi-tenancy
- **Payments:** Stripe API (recurring billing)
- **Notifications:** Twilio (SMS), email
- **Analytics:** Google Analytics API
- **Database:** PostgreSQL
- **Background Jobs:** Celery with Redis (optional)

## 🛠️ Setup Instructions
1. **Clone the repo**  
   `git clone https://github.com/your-username/domain-watcher.git && cd domain-watcher`

2. **Create & activate virtualenv**  
   `python3 -m venv env && source env/bin/activate`  
   _(On Windows: `env\Scripts\activate`)_

3. **Install dependencies**  
   `pip install -r requirements.txt`

4. **Configure environment variables**  
   Copy `.env.sample` to `.env` and fill in required keys

5. **Apply database migrations**  
`python manage.py migrate`

6. **Run the server**  
`python manage.py runserver`


## 🚀 Postman
Import `uptime-monitor-saas.postman_collection.json` to Postman for documentati

## 🚀 Deployment
Deploy on AWS, Azure, or GCP using your preferred tools. Make sure to configure environment variables, disable DEBUG, and use production-ready database/queues.


## 💬 Questions?
Feel free to open an issue or contact us.
