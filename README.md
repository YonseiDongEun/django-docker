# 서버 설치시

- .env.example을 .env로 바꿔야함
- .env의 DJANGO_ALLOWED_HOSTS에 서버의 ip주소를 넣어야 함

- 도커 구동
docker-compose up --build -d
docker-compose exec web mysql -u root -p db2020 < db2020.sql 

docker-compose exec db sh -c 'mysql -uroot -p${MYSQL_ROOT_PASSWORD} < /app/db2020.sql '



# 유저 생성
python manage.py shell
```python
from app.models import User, UserSubmitter, UserEvaluator, UserAdmin
user = User(name='admin', role='A', is_staff=True, is_superuser=True)
user.set_password('db2020')
user.save()
UserSubmitter(user=user).save()
UserEvaluator(user=user).save()
UserAdmin(user=user).save()
```


