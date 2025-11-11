# Team Manager

A Flask-based user management and internal operations system for small teams or companies.  
Features include task tracking, attendance, time-off requests, internal messaging, and paystub generation.

Initial set up for db sample data: 
`Typical Development Flow the first time`
'Enter this commands on terminal in the below order'
'flask db init' → 'flask db migrate -m "your comment eg intial setup"' → 'flask db upgrade'

After wards can run commands for below reasons
`flask db init` → once per project

`flask db migrate` → whenever models change

`flask db upgrade` → whenever you want to apply those changes

`flask init-db` to initialize the database with admin user, tun this first time.




