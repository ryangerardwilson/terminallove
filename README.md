# INTRODUCTION

An 'almost non-opiniated' open and free MVC architecture to create your own AI bot:
1. MODEL your data any way you like. Default set up includes finance, goal, time and run management CRUD modules.
2. VIEW is the GNU-LINUX Ubuntu terminal
3. CONTROLLER is a Function Calling AI Vendor. Default set up includes OpenAI integration 

# EXAMPLE USAGE

The bot is designed with an MVC framework, that leverages OpenAI function calling as the controller, to make it more responsive to user inputs. For instance, the rgw commnad (these are my initials, you can name it whatever you want. see installation section), followed by an organic user input can perform CRUD operations on the database:

***
FINANCE MODULE
***
    
```
    rgw "add expense - spent INR 500 on coffee"
    rgw "add expense - spent INR 700 on Dining yesterday"
    rgw "update expense - update expense id 5 - the cost was INR 450"
    rgw "delete expense id 5"
    rgw "show me my expenses"
    rgw "show me my expenses in the last 46 to 78 days"
    rgw "show me my expenses in the last 46 to 78 days cumulatively"
    rgw "show me my expenses in the last 46 to 78 days cumulatively and exlcude debt"
    rgw "show me my expenses line chart in the last 46 to 78 days"
    rgw "show me my expenses line chart in the last 46 to 78 days cumulatively"
    rgw "show me my expenses line chart in the last 46 to 78 days cumulatively and exclude debt"
```

***
RUNS MODULE
***

```
    rgw "log run - pre run weight is 205.7 lbs, post run weight is 202.3 lbs, temperature is 88 F, distance is 2.67, fat burn zone is 22 mins, cardio zone is 1 min"
    rgw "update run id 14 - distance is 3.6"
    rgw "delete run id 14"
    rgw "show me my runs"
    rgw "show me my running weight line chart"
    rgw "show me my running fat burn zone line chart"
    rgw "show me my running fat burn zone line chart for the last 14 to 37 days"
    rgw "show me my running fat burn zone line chart for the last 14 to 37 days cumulatively"    
    rgw "show me my running distance line chart"
    rgw "show me my running distance line chart for the last 14 to 37 days"
    rgw "show me my running distance line chart for the last 14 to 37 days cumulatively"
```

***
GOALS
***

```
    rgw "add goal - run a half-marathon by December"
    rgw "add action against goal id 2 - persist with low heart rate training for 3 months"
    rgw "show me my goals"
    rgw "show me my actions"
    rgw "show me my timesheet"
    rgw "show me my timesheet of yesterday"
    rgw "mark action ids 2, 3, 7 done"
    rgw "mark action ids 7, 8, 9 done yesterday"
    rgw "show me my actions against goal id 3"
    rgw "delete goal id 2"
    rgw "delete action id 5"
    rgw "update goal id 2 - run a marathon"
    rgw "show me my timesheet line chart"
    rgw "show me my timesheet line chart for the last 37 to 45 days"
```

***
TIME
***

```
    rgw "show me my events"
    rgw "add event - Lunch with Elon Musk on January 1, 2030"
    rgw "update event id 34 - Breakfast with Elon Musk on January 1, 2025"
    rgw "delete event id 30"
```

***
HARDCODED HELPERS
***

These helpers have been hardcoded (instead of being routed via the OpenAI controller for security purposes, as they interact with senstive data).

List all helpers

```
    rgw --l
```

Update the bot by pulling the latest version from this git repo

```
    rgw --update
```

Reset the conversation history of the bot

```
    rgw --reset
```

Display your passwords, and add, update, delete passwords

```
    rgw --p
    rgw --p:create
    rgw --p:update
    rgw --p:delete
```

Display your databases + add, update, delete databases credentials, get the schema of your databases, and tunnel into your databases

```
    rgw --db
    rgw --db:create
    rgw --db:update
    rgw --db:delete
    rgw --db:schema --id n
    rgw --db --id n
```

Display your virtual machines, add, update, delete virtual machine login credentials, and tunnel into your virtual machines (note: in case you use SSH keys to tunnel in, see step 7 of the installation process below)   

```
    rgw --vm
    rgw --vm:create
    rgw --vm:update
    rgw --vm:delete
    rgw --vm --id n
```

# INSTALLATION

***
STEP I - SET UP THE .ENV
***

1. Rename .env.example to .env.
2. In the .env file, add your OpenAI API key, MySQL database (DB) connection details, and credit card coefficient. This coefficient helps estimate a penalty on any purchase made on your credit card to keep track of your total due and outstanding amount.
3. You may leave the DEFAULT_DEBT_ID_FOR_PRIMARY_CREDIT_CARD field empty for now, and set it later. This field is required by the default finance module, and helps keep track of how much debt piles up in the main credit card you use.
4. If you're using Google Cloud MySQL, add your server's/machine's IP address to Google Cloud SQL's allowed addresses.

***
STEP III - INSTALL PYTHON AND MYSQL
***

1. Install mysql and python

```
    sudo apt-get update
    sudo apt-get install python3
    sudo apt-get install mysql-server
```

2. Use MySQL command-line to create your bot's database and tables using the provided commands. The below set up works well with the default functions of in services/modules. Feel free to make it your own.

```
    mysql -h YOUR_DB_HOST_IP -u YOUR_DB_USERNAME -p    
    CREATE DATABASE your_database_name;
    USE your_database_name;
    CREATE TABLE actions (
        id INT AUTO_INCREMENT PRIMARY KEY,
        goal_id INT,
        action VARCHAR(255) NOT NULL,
        deadline DATE,
        is_active TINYINT(1) DEFAULT 1,
        FOREIGN KEY (goal_id) REFERENCES goals(id)
    );

    CREATE TABLE debt_payments (
        id INT AUTO_INCREMENT PRIMARY KEY,
        debt_id INT,
        date DATE NOT NULL,
        amount DECIMAL(19,2) NOT NULL,
        currency VARCHAR(10),
        FOREIGN KEY (debt_id) REFERENCES debts(id)
    );

    CREATE TABLE debt_status_logs (
        id INT AUTO_INCREMENT PRIMARY KEY,
        debt_id INT,
        total_amount DECIMAL(19,2),
        outstanding DECIMAL(19,2),
        status_date DATE,
        FOREIGN KEY (debt_id) REFERENCES debts(id)
    );

    CREATE TABLE debts (
        id INT AUTO_INCREMENT PRIMARY KEY,
        source VARCHAR(50) NOT NULL,
        total_amount DECIMAL(19,2) NOT NULL,
        outstanding DECIMAL(19,2) NOT NULL,
        interest_rate DECIMAL(5,2),
        currency VARCHAR(10)
    );

    CREATE TABLE events (
        id INT AUTO_INCREMENT PRIMARY KEY,
        event VARCHAR(255) NOT NULL,
        date DATE NOT NULL,
        time TIME NOT NULL
    );

    CREATE TABLE expenses (
        id INT AUTO_INCREMENT PRIMARY KEY,
        value DECIMAL(10,2),
        expense_date DATE,
        currency VARCHAR(20) DEFAULT 'INR',
        particulars VARCHAR(255),
        debt_id INT,
        is_debt_repayment TINYINT(1) DEFAULT 0,
        is_earmarked_for_debt_repayment TINYINT(1) DEFAULT 0,
        FOREIGN KEY (debt_id) REFERENCES debts(id)
    );

    CREATE TABLE goals (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        date DATE NOT NULL
    );

    CREATE TABLE mysql_databases (
        id INT AUTO_INCREMENT PRIMARY KEY,
        description VARCHAR(255),
        command VARCHAR(255),
        password VARCHAR(255)
    );

    CREATE TABLE passwords (
        id INT AUTO_INCREMENT PRIMARY KEY,
        service VARCHAR(255),
        username VARCHAR(255),
        password VARCHAR(255),
        comments TEXT
    );

    CREATE TABLE reasons (
        id INT AUTO_INCREMENT PRIMARY KEY,
        goal_id INT,
        reason VARCHAR(255) NOT NULL,
        FOREIGN KEY (goal_id) REFERENCES goals(id)
    );

    CREATE TABLE relational_databases (
        id INT AUTO_INCREMENT PRIMARY KEY,
        description VARCHAR(255),
        mysql_connect_command VARCHAR(255),
        password VARCHAR(255)
    );

    CREATE TABLE runs (
        id INT AUTO_INCREMENT PRIMARY KEY,
        pre_run_weight_lbs FLOAT DEFAULT 0,
        post_run_weight_lbs FLOAT DEFAULT 0,
        fat_burn_zone_minutes FLOAT DEFAULT 0,
        cardio_zone_minutes FLOAT DEFAULT 0,
        peak_zone_minutes FLOAT DEFAULT 0,
        distance_covered_kms FLOAT DEFAULT 0,
        date DATE,
        temperature_in_f FLOAT
    );

    CREATE TABLE timesheets (
        id INT AUTO_INCREMENT PRIMARY KEY,
        action_id INT,
        date DATE,
        FOREIGN KEY (action_id) REFERENCES actions(id)
    );

    CREATE TABLE virtual_machines (
        id INT AUTO_INCREMENT PRIMARY KEY,
        description VARCHAR(255),
        command VARCHAR(255),
        password VARCHAR(255)
    );
```

***
STEP IV - CREATE A VIRTUAL ENVIRONMENT AND INSTALL PYTHON PACKAGES VIA PIP
***

```
    python3 -m venv botvenv
    source botvenv/bin/activate
    pip3 install termcolor tabulate pandas aiohttp mysql-connector-python python-dotenv plotext
    deactivate
```

***
STEP V - NAME YOUR BOT AND MAKE THE BOT EXECUTABLE SYSTEM WIDE
***

1. Update the init.sh files to contain the absolute paths to the init.sh and main.py files.
2. Make the init.sh and main.py files executable.
3. Create a symbolic link for init.sh and name your bot.
    
```
    pwd    
    chmod +x init.sh
    chmod +x main.py
    sudo ln -s /path/to/your/script/init.sh /usr/local/bin/rgw 
```

***
STEP VI (OPTIONAL) - STORE SSH KEYS IN FILES/SSH, AND SET PERMISSIONS FOR SSH KEYS
***

```
    chmod 600 path_to_the_directory/files/ssh/* 
```
