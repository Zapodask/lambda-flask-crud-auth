# Lambda flask crud auth

## AWS lambda + api gateway crud em flask com autenticação jwt e dynamoDB

## Setup

1. Configure o arquivo .env

2. Utilize o template.yaml no cloudformation

3. Navegue até a pasta scripts e rode o comando
```
    python update.py
```

## Routes

| Route | Method | Body | Need auth |
| ------ | ------ | ------ | ------ |
| users/ | GET | No | Yes |
| users/ | POST | username, password, password_confirmation | No |
| users/{username} | GET | No | Yes |
| users/{username} | DELETE | No | Yes |
| login | POST | username, password | No |
| change-password | PUT | new_password, new_password_confirmation | yes |


## License

MIT
