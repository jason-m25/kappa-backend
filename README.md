SETUP:
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
