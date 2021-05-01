from flask import Flask
from flask import request
from datetime import datetime
from datetime import timezone

import smtplib, ssl
import sqlite3

app = Flask(__name__)

@app.route('/')
def index():
    """Home Route"""
    return 'Welcome to Email Scheduler'

@app.route('/notifs/scheduleEmail',methods=['POST'])
def schedule_mail():
    """Get post data and store it in database"""
    data = request.get_json()
    formatted_datetime = datetime.strptime(data['sendAt'], '%Y-%m-%dT%H:%M:%SZ')
    sql_cursor = database_config()
    with sql_cursor as conn:
        conn.execute("INSERT INTO email_schedule (email,subject,template,sendAt,status) VALUES (?,?,?,?,?)",
                  (data['email'],data['subject'],data['template'],formatted_datetime,'PENDING'))
    sql_cursor.commit()    
    return 'Data Has been Saved!'

@app.route("/send_mail")
def send_mail():
    """This api is trigerred by the cron. all the pending ones and fetched and marked as completed"""
    try:
        conn = database_config()
        cur = conn.cursor()
        cur.execute("SELECT eid,email,subject,template from email_schedule where strftime('%Y-%m-%d %H:%M:%S', datetime('now')) > sendAt  and  status = 'PENDING';")
        rows = cur.fetchall()
        for row in rows:
            print(row)
            email_func(row[1],row[2],row[3])
            update_status(row[0],'DONE')
    except Exception as e:
        update_status(eid,'FAILED')
    return "Emails have been sent"

def update_status(eid,status):
    """ Update the database with the required status"""
    sql = ''' UPDATE email_schedule
              SET status = ?
              WHERE eid = ?'''
    conn = database_config()
    cur = conn.cursor()
    print(eid)
    cur.execute(sql, (status,eid,))
    conn.commit()

def email_func(receiver_email,subject,template):
    """email functionality for sending emails"""
    return "Email Sent"
    port = 465
    smtp_server = "smtp.gmail.com"
    sender_email = "my@gmail.com"  
    password = input("Type your password and press enter: ")
    message = 'Subject: {}\n\n{}'.format(subject, template)
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message)

def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by the db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Exception as e:
        print(e)
    return conn

def database_config():
    """Database connection"""
    database = r"emailschema.db"
    conn = create_connection(database)
    print(conn)
    return conn 


if __name__ == '__main__':
  app.run(debug=True)