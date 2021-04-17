# Recipe CLI Application

## Getting Started

This application uses a CLI in order to issue commands through the client. The user provides a JSON file as input, that specifies the request that they would like to make in addition to the relevant parameters that can be seen in our report. 

Sample json files are included as boilerplate to aid the user in making requests.

 and the commands performed on the database via this API interface. Sample JSON inputs are shown in the testing plan, where we go through every functionality of the client and server to confirm correctness of operations.

### Running the application

Running our application is very simple, you just need to enter the command below, replacing json_file with a correct json file.
```
python3 client.py --infile json_file.json
```

To connect to a database, you must define the connection parameters in a  ``
config.py
`` file 