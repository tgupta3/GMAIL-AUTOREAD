# Auto mark GMAIL messages as read
Mark messages in GMAIL as read at 2:00 UTC everyday.


## Getting Started

Get started by cloning the respository and adding a secret.yml file with the following contents

```
default: &default
  <<: *default
  KMS_KEY: "CiphertextBlob"
  KMS_ARN: "ARN of the KMS Key"
```

### Prerequisites

What things you need to install the software and how to install them
Requires the following things:
1. [Serverless framework] (https://serverless.com/framework/docs/getting-started/)
2. Google OAuth Libraries
```
pip install google-api-python-client
```
3. [Node 6+] (https://nodejs.org/en/download/)

### Installing

```
git clone https://github.com/tgupta3/GMAIL-AUTOREAD
```
Make sure to add the secret.yml

## Deployment

Deploy it using the serverless framework
```
serverless deploy --verbose
```

## Authors

* **Tushar Gupta** - *Initial work* - [tgupta3](https://github.com/tgupta3)


