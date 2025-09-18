from dataclasses import dataclass


@dataclass
class SAPConfig:
    username: str
    password: str
    connection_name: str = "340 PRD"
    exec_path: str = r"C:\Program Files (x86)\SAP\FrontEnd\SAPgui\saplogon.exe"
    window_title: str = "SAP Logon 770"
