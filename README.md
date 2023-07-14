# STEP I - SET UP THE .ENV

1. Rename .env.example to .env
2. Set up your open AI API key, MYSQL db connection, and primary credit card coefficient. This coefficient is meant to assume an interest penalty on any purchase made on your credit card, so as to keep a track of your total due and outstanding amount against your credit card - even if you don't have access to a realtime statement. For instance, you are only able to pay 60% of your total due each month, you may intuitively set up a higher interest coefficient of 1.5. Which means that 100 bucks spent on your credit card would be estimated as 150 bucks incurred, as you are spending despite your inability to fully pay off your credit card. On the other hand, if you are able to pay off your credit card bill each month, you can set up an interest coefficient of 1.1. This is meant to be an "intuitive" estimate.
3. You may leave the DEFAULT_DEBT_ID_FOR_PRIMARY_CREDIT_CARD empty for now, and set it after the rest of the installation process.
4. If you use Google Cloud MYSQL, add your server's/ machine's IP address to Google CLoud SQL's permitted addresses.
5. Dont worry about creating your db and schema yet. We will do it in Step III.


# STEP II - INSTALL HOMEBREW

Homebrew should be installed as a user with sudo access, not as the root user. Add smoochiekisses as the User (or something/someone more aesthetic-sounding), and Enter 100SmoochieKisses (or something/someone more aesthetic-sounding) as the full name. Keep the same password as the vm password.

    sudo adduser smoochiekisses 

Gives smoochiekisses sudo access

    usermod -aG sudo smoochiekisses 

If the user has been created, it should appear in this list

    cut -d: -f1 /etc/passwd

Login as the user to install homebrew

    su - smoochiekisses

Install Homebrew

    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# STEP III - INSTALL PYTHON AND MYSQL VIA HOMWBREW, AND MAKE THESE INSTALLATIONS ACCESSIBLE SYSTEM WIDE

Install the python3 via homebrew. We will be hooking the bot onto the interpreter of this installation of python.

    brew install python3

Install mysql

    brew install mysql

Copy the below path

    export PATH="/home/linuxbrew/.linuxbrew/bin:$PATH"

Paste it into the .zshrc file. This will ensure that brew installed packages global.

    nano ~/.zshrc

Invoke the zshrc file

    source ~/.zshrc   

Make the brew installed python and pip packages your main python interpreter

    sudo ln -sf /home/linuxbrew/.linuxbrew/bin/python3 /usr/local/bin/python3
    
    sudo ln -sf /home/linuxbrew/.linuxbrew/bin/python3/bin/pip3 /usr/local/bin/pip3

Reboot the system

    sudo reboot

Confirm if the homebrew installed version of python is your default python interpreter

    which python3

Open the MYSQL command line to your database and create the database of the bot using the below commands:

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


# STEP IV - INSTALL PYTHON PACKAGES VIA PIP


    pip3 install termcolor tabulate pandas aiohttp mysql-connector-python python-dotenv plotext

# STEP V - NAME YOUR BOT AND MAKE THE BOT EXECUTABLE SYSTEM WIDE

Get the path to the directory in which you cloned this git repo

    pwd

Inside the directory, make the main.py file executable

    chmod +x main.py

Create a symbolic link, and name your bot. Feel free to replace rgw (my initials) with anything you fancy

    sudo ln -s /path/to/your/script/main.py /usr/local/bin/rgw 

# STEP VI (OPTIONAL) - STORE SSH KEYS IN FILES/SSH, AND SET PERMISSIONS FOR SSH KEYS

The bot is designed to ssh you into any virtual machine of your choice, with the --vm flag.

    chmod 600 path_to_the_directory/files/ssh/*] Dont forget to specify the correct path to your ssh folder


