from .sap_config import SAPConfig
from .vkey import VKey
from .utils import launch_process
import win32com.client as win32

common_mapping = {
    "username": "wnd[0]/usr/txtRSYST-BNAME",
    "password": "wnd[0]/usr/pwdRSYST-BCODE",
    "tcode": "wnd[0]/tbar[0]/okcd",
}


class SAPGui:
    def __init__(self, config: SAPConfig):
        self.config = config
        self.connection_name = config.connection_name
        self.window_title = config.window_title
        self.sap_app = None
        self.connection = None
        self.session = None
        self.exec_path = config.exec_path

    def init(self):
        self.launch_sap()
        self._connect_to_engine()
        self.open_connection(self.connection_name)
        self.get_element("wnd[0]").maximize()

    def launch_sap(self):
        return launch_process(self.exec_path, self.window_title)

    def open_connection(self, connection_name: str):
        if not self.sap_app:
            self._connect_to_engine()

        try:
            self.connection = self.sap_app.Children(0)
            if self.connection.Description == connection_name:
                self.session = self.connection.Children(0)
                print("Existing connection found!")
                return True

            raise ValueError(f"SAP Connection {self.connection_name} not found")
        except Exception as e:
            # This would mean that the connection is not open, so open new one.
            print(f"Existing connection not found, opening new one: {e}")

        try:
            self.connection = self.sap_app.OpenConnection(connection_name, True)
        except Exception as e:
            print(f"Error opening connection: {e}")
            raise ValueError(
                f"Cannot open connection {connection_name}. Please check connection name"
            )

        self.session = self.connection.Children(0)
        return True

    def _connect_to_engine(self):
        try:
            sap_gui = win32.GetObject("SAPGUI")
            self.sap_app = sap_gui.GetScriptingEngine
            return sap_gui
        except Exception as e:
            print(f"Error connecting to SAP GUI: {e}")
            raise Exception("SAP Logon is not running.")

    # TODO: Screenshot
    def _raise_if_error(self):
        message = self.get_status_bar_msg()
        if message.get("type") == "E":
            raise ValueError(message.get("text"))

    def get_status_bar_msg(self):
        try:
            status_bar = self.session.findById("wnd[0]/sbar")
            return {
                "text": status_bar.text,
                "type": status_bar.MessageType,
                "id": status_bar.MessageId,
                "number": status_bar.MessageNumber,
            }
        except Exception as e:
            print(f"Error getting status bar: {e}")
            return None

    def get_document_number(self):
        msg = self.get_status_bar_msg()
        return msg["text"].split(" ")[3]

    def send_key(self, key: VKey, window: int = 0):
        try:
            self.session.findById(f"wnd[{window}]").sendVKey(key.value)
            if key == VKey.ENTER:
                self._raise_if_error()
        except Exception as e:
            print(f"Error sending vkey: {e}")
            raise RuntimeError("Error sending vkey")

    def get_element(self, element_id: str):
        try:
            return self.session.findById(element_id)
        except Exception as e:
            self._raise_if_error()
            raise RuntimeError(f"Error getting element {element_id}: Error: {e}")

    def set_value(self, element_id: str, value: any):
        try:
            element = self.get_element(element_id)
            element.text = str(value)
        except Exception as e:
            self._raise_if_error()
            raise ValueError(
                f"Error setting sap element value: {element_id}. Error: {e}"
            )

    def get_value(self, element_id: str):
        try:
            element = self.get_element(element_id)
            return str(element.text)
        except Exception as e:
            self._raise_if_error()
            raise ValueError(
                f"Error getting sap element value: {element_id}. Error: {e}"
            )

    def login(self, username: str, password: str):
        self.set_value(common_mapping["username"], username)
        self.set_value(common_mapping["password"], password)
        self.send_key(VKey.ENTER)

    def start_transaction(self, tcode: str, new_transaction: bool = True):
        if new_transaction:
            self.session.StartTransaction(tcode)
            self._raise_if_error
            return True

        self.session.SendCommand(tcode)
        self._raise_if_error()
        return True

    def click_element(self, element_id: str):
        # TODO: handle select() for tab element type
        try:
            self.get_element(element_id).press()
        except Exception as e:
            self._raise_if_error()
            raise ValueError(f"Error clicking sap element: {element_id}. Error: {e}")

    def get_selected_tab(self, tab_id: str):
        return self.get_element(tab_id).SelectedTab.text.lower()

    def select_tab(self, tab_strip: str, tab_index: int):
        """Selects a tab by its index in the tab strip only if it is not already selected"""
        selected_tab = self.get_selected_tab(tab_strip)
        tab_id = f"{tab_strip}/tabpT\\{str(tab_index).zfill(2)}"
        target_tab = self.get_element(tab_id)
        if selected_tab != target_tab.text.lower():
            target_tab.select()

    def select_from_list(self, element_id: str, label: str):
        combobox = self.get_element(element_id)
        key = None
        for entry in combobox.entries:
            if entry.value.lower() == label.lower():
                key = entry.key
                break

        if not key:
            raise ValueError(f"Label '{label}' not found in combobox '{element_id}'")

        combobox.key = key
        return True
