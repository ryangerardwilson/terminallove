***
STEP I - SET UP THE .ENV
***

1. Rename .env.example to .env
2. Set up your open AI API key, MYSQL db connection, and primary credit card coefficient. This coefficient is meant to assume an interest penalty on any purchase made on your credit card, so as to keep a track of your total due and outstanding amount against your credit card - even if you don't have access to a realtime statement. For instance, you are only able to pay 60% of your total due each month, you may intuitively set up a higher interest coefficient of 1.5. Which means that 100 bucks spent on your credit card would be estimated as 150 bucks incurred, as you are spending despite your inability to fully pay off your credit card. On the other hand, if you are able to pay off your credit card bill each month, you can set up an interest coefficient of 1.1. This is meant to be an "intuitive" estimate.
3. You may leave the DEFAULT_DEBT_ID_FOR_PRIMARY_CREDIT_CARD empty for now, and set it after the rest of the installation process.
4. If you use Google Cloud MYSQL, add your server's/ machine's IP address to Google CLoud SQL's permitted addresses.
5. Dont worry about creating your db and schema yet. We will do it in Step III.

***
STEP II - INSTALL HOMEBREW
***

# Homebrew should be installed as a user with sudo access, not as the root user. Add smoochiekisses as the User (or something/someone more aesthetic-sounding), and Enter 100SmoochieKisses (or something/someone more aesthetic-sounding) as the full name. Keep the same password as the vm password.

sudo adduser smoochiekisses 

# Gives smoochiekisses sudo access
usermod -aG sudo smoochiekisses 

# If the user has been created, it should appear in this list
cut -d: -f1 /etc/passwd

# Login as the user to install homebrew
su - smoochiekisses

***
STEP III - INSTALL PYTHON AND MYSQL VIA HOMWBREW, AND MAKE THESE INSTALLATIONS ACCESSIBLE SYSTEM WIDE
***
PYTHON PACKAGES NEEDED
[/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"] Intalls homebrew
[brew install python3] installs python3
[brew install mysql] installs mysql
[nano ~/.zshrc] copy-paste this into the file - [export PATH="/home/linuxbrew/.linuxbrew/bin:$PATH"]. This will ensure that brew installed packages are your global packages
[source ~/.zshrc]
[sudo ln -sf /home/linuxbrew/.linuxbrew/bin/python3 /usr/local/bin/python3]
[sudo ln -sf /home/linuxbrew/.linuxbrew/bin/python3/bin/pip3 /usr/local/bin/pip3]
[sudo reboot]
[which python3] Confirm if the homebrew installed version of python is your default python interpreter
[mysql -h YOUR_DB_HOST_IP -u YOUR_DB_USERNAME -p] Open the MYSQL command line to the terminal
[CREATE DATABASE your_database_name;] create the database of the bot
[USE your_database_name;] Select that database, and then use the below commands to create the necessary tables

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

***
STEP IV - INSTALL PYTHON PACKAGES VIA PIP
***
[
pip3 install termcolor
pip3 install tabulate
pip3 install pandas
pip3 install aiohttp
pip3 install mysql-connector-python
pip3 install python-dotenv
pip3 install plotext
]


***
STEP V - NAME YOUR BOT AND MAKE THE BOT EXECUTABLE SYSTEM WIDE
***
INITIATION:
[pwd] get the path to directory and copy it
[chmod +x main.py] make main.py executable
[sudo ln -s /path/to/your/script/main.py /usr/local/bin/rgw] create a symbolic link to the path of main.py. For instance - [sudo ln -s /Users/ryangerardwilson/Apps/ubuntubot/main.py /usr/local/bin/rgw]. YOu can replace rgw with the name of your bot. For instance [sudo ln -s /Users/elonmusk/Apps/ubuntubot/main.py /usr/local/bin/twit]


***
STEP VI - STORE SSH KEYS IN FILES/SSH, AND SET PERMISSIONS FOR SSH KEYS
***
The bot is designed to ssh you into any virtual machine of your choice, with the --vm flag.
[chmod 600 /home/smoochiekisses/Desktop/apps/ubuntubot/files/ssh/*] Dont forget to specify the correct path to your ssh folder





