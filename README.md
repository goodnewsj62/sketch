# **SKETCH**
***An online art gallery***

currently under dev

## **To Start Up**
- create a virtual enviroment
- install the project dependencies
``` 
(virtualenv)$ pip install -r requirements.txt
```
- next create a db \"for this i used postgresql"
```
$sudo su - postgres

#psql

=#create database sketch;
=#create user suser with password 'suser';
=#alter user suser set client_encoding to 'utf8';
=#alter user suser set default_transaction_isolation to 'read committed';

=#alter user suser set timezone to 'UTC'
=#grant all privileges on database sketch to suser;
```

- setup .env
- Then run the flask application

```
(virtualenv)$flask run
```

### Components
- **Authentication**
    
    - login
    - signup
    - forgot password
    - 