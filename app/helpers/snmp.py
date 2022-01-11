from app.models.base_model import Port


def is_switch_up(sw_ip: str) -> bool:
    pass


def get_port_state(sw_ip: str, port: int) -> (bool, Port):
    port = Port(port, True, 10000, ('121:21:', '121:33:44'), 'istv_pppoe', ['istv_pppoe', 'default'])
    return False, port


def set_vlan_on_port(sw_ip: str, port: int, vlan: str) -> (bool, Port):
    port = Port(port, True, 10000, ('121:21:', '121:33:44'), 'istv_pppoe', ['istv_pppoe', 'default'])
    return False, port