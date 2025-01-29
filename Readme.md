## Prova Body-Fields amb Postman
1. Executa l'aplicació: `uvicorn main:app --reload`
2. Obre Postman i envia un POST a `http://localhost:8000/items/`
3. Prova diferents valors per veure les validacions.
## Prova Body-Nested Models amb Swagger
1. Obre Swagger UI a `http://localhost:8000/docs`
2. Prova l'endpoint `/users/` amb dades niades.