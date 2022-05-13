1. SETUP:
   - Navigate to project in console
   - Create virtual environment 
   - You will need MySQL Community Server:
       - Create MySQL schema with the desired database name
       - Create db_config.py file in the project root containing your database configuration
   - Execute the following command to install project requirements:
       - pip install -r requirements.txt
   - Execute the following commands to initialize the database tables:
       - python
       - from app import db
       - db.create_all()
       - exit()
   - Run the app by executing the following command:
       - python run.py


2. OpenAPI SwaggerHub Documentation Link:
    - https://app.swaggerhub.com/apis-docs/jamak/KAPPA-openAPI/0.1


3. LIBRARIES USED:
   - FLASK: SQLAlchemy, Marshmallow, CORS, Bcrypt
   - JWT, statistics, datetime


4. MYSQL DATABASE TABLES:
   - user
   - transaction
   - listing


5. FUNCTIONALITY:
   - Check the exchange rates
   - Check the following statistics and insights into the buy and sell exchange rates:
       1. Standard Deviation
       2. Weekly and 3-day Average
       3. Trend
       4. All time volume
       5. Daily volume
   - Check graphs that show the evolution of the exchange rates over the course of all time, where each datapoint represents the opening value of the exchange rate every day
   - The ability to record a new transaction that has already happened for it to factor into the new rates
   - Seeing a record of past transactions which were added when logged in as user
   - Facilitate peer to peer transactions