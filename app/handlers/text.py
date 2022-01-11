from telebot.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

from app import bot, Message
import re

from app.helpers import snmp
from app.models.base_model import Switch, Port


class MarkupButtons:
    reload = "🔄 Обновить"
    configure = "⚙️ Сменить VLAN"
    back = "🔙 Назад"


class Text:
    reg_ip = re.compile(r'(\d{1,3}\.){3}\d{1,3}')

    succ_exist_sw = '''
<b>Коммутатор: {name}</b>
 
ip: <b>{ip}</b>
Модель: <b>{model}</b>
Состояние: <b>{state}</b> 🟢

Введите порт, цифрой от 1 до 24:
    '''
    port_state = '''
Коммутатор: <b>{sw_name}</b>

Номер порта: <b>{port_num}</b>
Состояние: <b>{port_state}</b>
Скорость: <b>{port_speed}</b>
VLAN: <b>{port_vlan}</b>
Изученные MAC:
<b>{mac_table}</b>  
    '''
    help_for_readonly_users = '''
Для выбора коммутатора, введите его название либо ip-адрес. 
Пример: <b>10.102.170.97</b> либо <b>6-39</b>
        '''
    err__select_menu = '''
👇👇👇 Выберите действие из меню, расположеного ниже.    
    '''
    set_vlan = '''
👇👇👇 Выберите VLAN из меню, расположеного ниже.   
    '''
    set_vlan_success = '''
VLAN <b>{vlan}</b> успешно установлен. 
    '''
    err__not_exist_sw = '''
🗿  Коммутатор <b>{err_name_or_ip}</b> не найден. Проверьте ввод и повторите ещё раз.
    '''
    err__message_is_long = '''
😵 Слишком много символов
    '''
    err__not_exist_port = '''
🤷🏿‍♂️ Неправильно. Введите порт, цифрой от 1 до 24:
    '''
    err__conn_is_lose = '''
🙊 Пропало соединение с коммутатором.    
    '''
    err__set_vlan = '''
При изменении VLAN произошла ошибка. Сообщите о ней: @vkrkn    
    '''
    err__select_vlan = '''
👇👇👇 Выберите VLAN из меню, расположеного ниже    
    '''


@bot.message_handler(content_types=['text'])
def text_handler(message: Message):
    if not bot.app_user.has_access_readonly():
        # нет роли с правами readonly
        return

    # :TODO сделать через мидлвар
    if len(message.text) > 25:
        bot.send_message(
            bot.app_user.telegram_id,
            Text.err__message_is_long
        )
        return

    if Text.reg_ip.match(message.text) is not None:
        ip_addr = Text.reg_ip.match(message.text).group()
        sw = Switch.get_or_none(ip=ip_addr)
    else:
        sw = Switch.get_or_none(name=str(message.text).strip())

    if sw is None:
        bot.send_message(
            bot.app_user.telegram_id,
            Text.err__not_exist_sw.format(err_name_or_ip=message.text),
            reply_markup=ReplyKeyboardRemove()
        )
        return

    sw_state = snmp.is_switch_up(sw.ip)

    bot.send_message(
        bot.app_user.telegram_id,
        Text.succ_exist_sw.format(
            name=sw.name,
            ip=sw.ip,
            model=sw.model,
            zone=sw.zone.name,
            state="UP 🟢" if sw_state else "DOWN 🔴"
        ),
        reply_markup=ReplyKeyboardMarkup(True, True).add(KeyboardButton(MarkupButtons.back))
    )

    bot.register_next_step_handler(message, get_switches_port, sw)


def get_switches_port(message: Message, sw: Switch):
    if message.text == MarkupButtons.back:
        bot.send_message(
            bot.app_user.telegram_id,
            Text.help_for_readonly_users,
            reply_markup=ReplyKeyboardRemove()
        )
        return

    if not str(message.text).strip().isdigit():
        bot.send_message(
            bot.app_user.telegram_id,
            Text.err__not_exist_port,
            reply_markup=ReplyKeyboardMarkup(True, True).add(KeyboardButton(MarkupButtons.back))
        )
        bot.register_next_step_handler(message, get_switches_port, sw)
        return

    port = int(message.text)
    if (port < 1) or (port > 24):
        bot.send_message(
            bot.app_user.telegram_id,
            Text.err__not_exist_port,
            reply_markup=ReplyKeyboardMarkup(True, True).add(KeyboardButton(MarkupButtons.back))
        )
        bot.register_next_step_handler(message, get_switches_port, sw)
        return

    err, port_state = snmp.get_port_state(sw.ip, port)
    if err:
        bot.send_message(
            bot.app_user.telegram_id,
            Text.err__conn_is_lose
        )
        return

    markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, selective=True)

    if bot.app_user.has_access_operator():
        markup.add(KeyboardButton(MarkupButtons.configure))

    markup.add(KeyboardButton(MarkupButtons.reload), KeyboardButton(MarkupButtons.back))

    bot.send_message(
        bot.app_user.telegram_id,
        Text.port_state.format(
            sw_name=sw.name,
            port_num=port_state.number,
            port_state="UP 🟢" if port_state.is_up else "DOWN 🔴",
            port_speed=port_state.speed,
            port_vlan=port_state.vlan,
            mac_table="\n".join(port_state.mac_table)
        ),
        reply_markup=markup
    )

    bot.register_next_step_handler(message, get_action_for_port, sw, port_state)


def get_action_for_port(message: Message, sw: Switch, port: Port):
    if message.text == MarkupButtons.back:
        bot.send_message(
            bot.app_user.telegram_id,
            Text.succ_exist_sw.format(
                name=sw.name, ip=sw.ip, model=sw.model, zone=sw.zone.name, state="UP"
            ),
            reply_markup=ReplyKeyboardMarkup(True, True).add(KeyboardButton(MarkupButtons.back))
        )
        bot.register_next_step_handler(message, get_switches_port, sw)
    elif message.text == MarkupButtons.reload:
        err, port_state = snmp.get_port_state(sw.ip, port.number)
        if err:
            bot.send_message(
                bot.app_user.telegram_id,
                Text.err__conn_is_lose
            )
            return

        markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, selective=True)

        if bot.app_user.has_access_operator():
            markup.add(KeyboardButton(MarkupButtons.configure))

        markup.add(KeyboardButton(MarkupButtons.reload), KeyboardButton(MarkupButtons.back))

        bot.send_message(
            bot.app_user.telegram_id,
            Text.port_state.format(
                sw_name=sw.name,
                port_num=port_state.number,
                port_state="UP 🟢" if port_state.is_up else "DOWN 🔴",
                port_speed=port_state.speed,
                port_vlan=port_state.vlan,
                mac_table="\n".join(port_state.mac_table)
            ),
            reply_markup=markup
        )
        bot.register_next_step_handler(message, get_action_for_port, sw, port_state)
    elif message.text == MarkupButtons.configure:
        markup = ReplyKeyboardMarkup(True, False)
        for vlan in port.available_vlan:
            markup.add(KeyboardButton(vlan))

        markup.add(KeyboardButton(MarkupButtons.back))
        bot.send_message(
            bot.app_user.telegram_id,
            Text.set_vlan,
            reply_markup=markup
        )
        bot.register_next_step_handler(message, set_vlan_on_port, sw, port)
    else:
        bot.send_message(
            bot.app_user.telegram_id,
            Text.err__select_menu
        )

        bot.register_next_step_handler(message, get_action_for_port, sw, port)


def set_vlan_on_port(message: Message, sw: Switch, port: Port):
    if message.text == MarkupButtons.back:
        err, port_state = snmp.get_port_state(sw.ip, port.number)
        if err:
            bot.send_message(
                bot.app_user.telegram_id,
                Text.err__conn_is_lose
            )
            return

        markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, selective=True)

        if bot.app_user.has_access_operator():
            markup.add(KeyboardButton(MarkupButtons.configure))

        markup.add(KeyboardButton(MarkupButtons.reload), KeyboardButton(MarkupButtons.back))

        bot.send_message(
            bot.app_user.telegram_id,
            Text.port_state.format(
                sw_name=sw.name,
                port_num=port_state.number,
                port_state="UP 🟢" if port_state.is_up else "DOWN 🔴",
                port_speed=port_state.speed,
                port_vlan=port_state.vlan,
                mac_table="\n".join(port_state.mac_table)
            ),
            reply_markup=markup
        )

        bot.register_next_step_handler(message, get_action_for_port, sw, port_state)
    elif message.text in port.available_vlan:
        err, port_state = snmp.set_vlan_on_port(sw.ip, port.number, message.text)
        if err:
            bot.send_message(
                bot.app_user.telegram_id,
                Text.err__set_vlan,
                reply_markup=ReplyKeyboardRemove()
            )
            return

        bot.send_message(
            bot.app_user.telegram_id,
            Text.set_vlan_success.format(vlan=port_state.vlan),
            reply_markup=ReplyKeyboardRemove()
        )
    else:
        bot.send_message(
            bot.app_user.telegram_id,
            Text.err__select_vlan
        )
        bot.register_next_step_handler(message, set_vlan_on_port, sw, port)


