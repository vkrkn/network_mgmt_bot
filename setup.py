
from app.models.base_model import *

DB.create_tables([Role, User, Switch, Zone])

Role.create(name='Admin')
Role.create(name='Operator')
Role.create(name='ReadOnly')
Role.create(name='Blocked')
zone = Zone.get_or_create(name="Первая зона")[0]
Switch.create(name="25-11", ip="192.168.184.84", model="3028", zone=zone)
