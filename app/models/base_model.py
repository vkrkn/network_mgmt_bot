import os

from peewee import *
from app import logger, APP_DIR, AppState


ENV_APP_STATE = AppState(int(os.getenv("APP_STATE", "1")))
logger.info(f'State is {ENV_APP_STATE}')
if AppState.PRODUCTION == ENV_APP_STATE:
    logger.info("Создание инстанса ДБ для продакшена")
    pass
else:
    logger.info("Создание инстанса ДБ для разработки")
    DB = SqliteDatabase(APP_DIR / os.path.sep.join(['databases', 'sqlite.db']))


class BaseModel(Model):
    class Meta:
        database = DB


class Role(BaseModel):
    name = TextField(null=False, index=True)

    class Meta:
        table_name = 'roles'

    def __str__(self):
        return self.name


class User(BaseModel):
    telegram_id = TextField(null=False, index=True)
    name = TextField(null=False)
    role = ForeignKeyField(Role, 'id', null=True, backref='users', on_delete='SET NULL', on_update='CASCADE')

    def has_access_admin(self):
        if self.role:
            return self.role.name == 'Admin'
        return False

    def has_access_operator(self):
        if self.role:
            return self.role.name == 'Admin' or self.role.name == 'Operator'
        return False

    def has_access_readonly(self):
        if self.role:
            return self.role.name == 'Admin' or self.role.name == 'Operator' or self.role.name == 'ReadOnly'
        return False


    class Meta:
        table_name = 'users'


class Zone(BaseModel):
    name = TextField()

    class Meta:
        table_name = 'zones'


class Switch(BaseModel):
    name = TextField(null=False, index=True)
    ip = TextField(null=False, index=True)
    model = TextField(null=True)
    zone = ForeignKeyField(Zone, 'id', null=False, backref="switches", on_delete="SET NULL")

    class Meta:
        table_name = 'switches'


class Port:
    number = int()
    is_up = bool()
    speed = str()
    mac_table = tuple()
    vlan = str()
    available_vlan = list() # те что действительно можно установить на порт
    allow_vlan = ('istv_pppoe', 'default', 'comnet_pppoe', 'tps_pppoe')

    def __init__(self,
                 number: int,
                 is_up: bool,
                 speed: int,
                 mac_table: tuple,
                 vlan: str,
                 available_vlan: list):
        self.number = number
        self.is_up = is_up
        self.speed = speed
        self.mac_table = mac_table
        self.vlan = vlan
        self.available_vlan = available_vlan
