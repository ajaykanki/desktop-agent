from .sap_mappings import (
    Screen,
    GuiElement,
    Action,
    ElementType,
    CallInternalFunction,
    ActionType,
    PRESS_HEADER_BUTTON_ACTION,
)

# Create Sales Order VA01_SCREEN transaction screen:
VA01_INITIAL = Screen(
    name="VA01_INITIAL",
    elements={
        "order type": GuiElement(id=r"wnd[0]/usr/ctxtVBAK-AUART"),
        "sales organization": GuiElement(
            id=r"wnd[0]/usr/ctxtVBAK-VKORG",
        ),
        "distribution channel": GuiElement(
            id=r"wnd[0]/usr/ctxtVBAK-VTWEG",
        ),
        "division": GuiElement(id=r"wnd[0]/usr/ctxtVBAK-SPART"),
    },
)

VA01_OVERVIEW = Screen(
    name="VA01_OVERVIEW",
    elements={
        "sold to party": GuiElement(
            id=r"wnd[0]/usr/subSUBSCREEN_HEADER:SAPMV45A:4021/subPART-SUB:SAPMV45A:4701/ctxtKUAGV-KUNNR",
        ),
        "ship to party": GuiElement(
            id=r"wnd[0]/usr/subSUBSCREEN_HEADER:SAPMV45A:4021/subPART-SUB:SAPMV45A:4701/ctxtKUWEV-KUNNR",
        ),
        "po number": GuiElement(
            id=r"wnd[0]/usr/subSUBSCREEN_HEADER:SAPMV45A:4021/txtVBKD-BSTKD",
        ),
        "po date": GuiElement(
            id=r"wnd[0]/usr/subSUBSCREEN_HEADER:SAPMV45A:4021/ctxtVBKD-BSTDK",
        ),
    },
)

VA01_SALES = Screen(
    name="VA01_SALES",
    entry_point=[
        Action(
            type=ActionType.CLICK,
            target_id=r"wnd[0]/usr/tabsTAXI_TABSTRIP_OVERVIEW/tabpT\01",
        ),
    ],
    elements={
        "payment terms": GuiElement(
            id=r"wnd[0]/usr/tabsTAXI_TABSTRIP_OVERVIEW/tabpT\01/ssubSUBSCREEN_BODY:SAPMV45A:4400/ssubHEADER_FRAME:SAPMV45A:4440/ctxtVBKD-ZTERM"
        ),
        "incoterms 1": GuiElement(
            id=r"wnd[0]/usr/tabsTAXI_TABSTRIP_OVERVIEW/tabpT\01/ssubSUBSCREEN_BODY:SAPMV45A:4400/ssubHEADER_FRAME:SAPMV45A:4440/lblVBKD-INCO1"
        ),
        "incoterms 2": GuiElement(
            id=r"wnd[0]/usr/tabsTAXI_TABSTRIP_OVERVIEW/tabpT\01/ssubSUBSCREEN_BODY:SAPMV45A:4400/ssubHEADER_FRAME:SAPMV45A:4440/txtVBKD-INCO2"
        ),
    },
)

VA01_ITEM_OVERVIEW = Screen(
    name="VA01_ITEM_OVERVIEW",
    press_enter=False,
    entry_point=[
        Action(
            type=ActionType.CLICK,
            target_id=r"wnd[0]/usr/tabsTAXI_TABSTRIP_OVERVIEW/tabpT\02",
        ),
    ],
    elements={
        "table": GuiElement(
            type=ElementType.TABLE,
            id=r"wnd[0]/usr/tabsTAXI_TABSTRIP_OVERVIEW/tabpT\02/ssubSUBSCREEN_BODY:SAPMV45A:4401/subSUBSCREEN_TC:SAPMV45A:4900/tblSAPMV45ATCTRL_U_ERF_AUFTRAG",
        ),
        "select all": GuiElement(
            type=ElementType.BUTTON,
            id=r"wnd[0]/usr/tabsTAXI_TABSTRIP_OVERVIEW/tabpT\02/ssubSUBSCREEN_BODY:SAPMV45A:4401/subSUBSCREEN_TC:SAPMV45A:4900/subSUBSCREEN_BUTTONS:SAPMV45A:4050/btnBT_MKAL",
        ),
    },
)

VA01_FAST_DATA_ENTRY = Screen(
    name="VA01_FAST_DATA_ENTRY",
    press_enter=False,
    entry_point=[
        Action(
            type=ActionType.CLICK,
            target_id=r"wnd[0]/usr/tabsTAXI_TABSTRIP_OVERVIEW/tabpT\08",
        ),
    ],
    elements={
        "char. display": GuiElement(
            type=ElementType.TEXT,
            id=r"wnd[0]/usr/tabsTAXI_TABSTRIP_OVERVIEW/tabpT\08/ssubSUBSCREEN_BODY:SAPMV45A:7901/cmbRV45A-MUEBS",
        ),
        "table": GuiElement(
            type=ElementType.TABLE,
            id=r"wnd[0]/usr/tabsTAXI_TABSTRIP_OVERVIEW/tabpT\08/ssubSUBSCREEN_BODY:SAPMV45A:7901/subSUBSCREEN_TC:SAPMV45A:7905/tblSAPMV45ATCTRL_U_MILL_SE_KONFIG",
        ),
        "select all": GuiElement(
            type=ElementType.BUTTON,
            id=r"wnd[0]/usr/tabsTAXI_TABSTRIP_OVERVIEW/tabpT\08/ssubSUBSCREEN_BODY:SAPMV45A:7901/subSUBSCREEN_TC:SAPMV45A:7905/subSUBSCREEN_BUTTONS:SAPMV45A:4050/btnBT_MKAL",
        ),
    },
)


HEADER_SALES = Screen(
    name="HEADER_SALES",
    entry_point=[
        PRESS_HEADER_BUTTON_ACTION,
        Action(
            type=ActionType.CLICK,
            target_id=r"wnd[0]/usr/tabsTAXI_TABSTRIP_HEAD/tabpT\01",
        ),
    ],
    elements={
        "doc. currency": GuiElement(
            type=ElementType.TEXT,
            id=r"wnd[0]/usr/tabsTAXI_TABSTRIP_HEAD/tabpT\01/ssubSUBSCREEN_BODY:SAPMV45A:4301/ctxtVBAK-WAERK",
        )
    },
)

HEADER_PARTNERS = Screen(
    name="HEADER_PARTNERS",
    entry_point=[
        PRESS_HEADER_BUTTON_ACTION,
        Action(
            type=ActionType.CLICK,
            target_id=r"wnd[0]/usr/tabsTAXI_TABSTRIP_HEAD/tabpT\08",
        ),
    ],
    elements={
        "partner function": GuiElement(
            type=ElementType.TEXT,
            id=r"wnd[0]/usr/tabsTAXI_TABSTRIP_HEAD/tabpT\08/ssubSUBSCREEN_BODY:SAPMV45A:4352/subSUBSCREEN_PARTNER_OVERVIEW:SAPLV09C:1000/tblSAPLV09CGV_TC_PARTNER_OVERVIEW/cmbGVS_TC_DATA-REC-PARVW[0,4]",
        ),
        "partner": GuiElement(
            type=ElementType.TEXT,
            id=r"wnd[0]/usr/tabsTAXI_TABSTRIP_HEAD/tabpT\08/ssubSUBSCREEN_BODY:SAPMV45A:4352/subSUBSCREEN_PARTNER_OVERVIEW:SAPLV09C:1000/tblSAPLV09CGV_TC_PARTNER_OVERVIEW/ctxtGVS_TC_DATA-REC-PARTNER[1,4]",
        ),
    },
)

HEADER_TEXTS = Screen(
    name="HEADER_TEXTS",
    press_enter=False,
    entry_point=[
        PRESS_HEADER_BUTTON_ACTION,
        Action(
            type=ActionType.CLICK,
            target_id=r"wnd[0]/usr/tabsTAXI_TABSTRIP_HEAD/tabpT\09",
        ),
    ],
    elements={
        "click_notify_remiter": GuiElement(
            type=ElementType.SHELL,
            id=r"wnd[0]/usr/tabsTAXI_TABSTRIP_HEAD/tabpT\09/ssubSUBSCREEN_BODY:SAPMV45A:4152/subSUBSCREEN_TEXT:SAPLV70T:2100/cntlSPLITTER_CONTAINER/shellcont/shellcont/shell/shellcont[0]/shell",
            call_functions=[
                CallInternalFunction(func="selectItem", params=["Z041", "Column1"]),
                CallInternalFunction(
                    func="ensureVisibleHorizontalItem", params=["Z041", "Column1"]
                ),
                CallInternalFunction(
                    func="doubleClickItem", params=["Z041", "Column1"]
                ),
            ],
        ),
        "notify": GuiElement(
            id=r"wnd[0]/usr/tabsTAXI_TABSTRIP_HEAD/tabpT\09/ssubSUBSCREEN_BODY:SAPMV45A:4152/subSUBSCREEN_TEXT:SAPLV70T:2100/cntlSPLITTER_CONTAINER/shellcont/shellcont/shell/shellcont[1]/shell",  # Set the commission here
        ),
    },
)

HEADER_ADD_DATA_A = Screen(
    name="HEADER_ADD_DATA_A",
    entry_point=[
        PRESS_HEADER_BUTTON_ACTION,
        Action(
            type=ActionType.CLICK,
            target_id=r"wnd[0]/usr/tabsTAXI_TABSTRIP_HEAD/tabpT\12",
        ),
    ],
    elements={
        "channel type": GuiElement(
            type=ElementType.TEXT,
            id=r"wnd[0]/usr/tabsTAXI_TABSTRIP_HEAD/tabpT\12/ssubSUBSCREEN_BODY:SAPMV45A:4309/ctxtVBAK-ZECOM",
        ),
        "sub channel type": GuiElement(
            type=ElementType.TEXT,
            id=r"wnd[0]/usr/tabsTAXI_TABSTRIP_HEAD/tabpT\12/ssubSUBSCREEN_BODY:SAPMV45A:4309/ctxtVBAK-ZSCTYP",
        ),
        "order type": GuiElement(
            type=ElementType.TEXT,
            id=r"wnd[0]/usr/tabsTAXI_TABSTRIP_HEAD/tabpT\12/ssubSUBSCREEN_BODY:SAPMV45A:4309/cmbVBAK-ZORD_TYPE",
        ),
    },
)

HEADER_ADD_DATA_B = Screen(
    name="HEADER_ADD_DATA_B",
    entry_point=[
        PRESS_HEADER_BUTTON_ACTION,
        Action(
            type=ActionType.CLICK,
            target_id=r"wnd[0]/usr/tabsTAXI_TABSTRIP_HEAD/tabpT\13",
        ),
    ],
    elements={
        "window start date": GuiElement(
            id=r"wnd[0]/usr/tabsTAXI_TABSTRIP_HEAD/tabpT\13/ssubSUBSCREEN_BODY:SAPMV45A:4312/sub8309:SAPMV45A:8309/ctxtVBAK-ZZSD_STARTDT",
        ),
        "window cancel date": GuiElement(
            id=r"wnd[0]/usr/tabsTAXI_TABSTRIP_HEAD/tabpT\13/ssubSUBSCREEN_BODY:SAPMV45A:4312/sub8309:SAPMV45A:8309/ctxtVBAK-ZZSD_CANDT",
        ),
        "plan ex-factory date": GuiElement(
            id=r"wnd[0]/usr/tabsTAXI_TABSTRIP_HEAD/tabpT\13/ssubSUBSCREEN_BODY:SAPMV45A:4312/sub8309:SAPMV45A:8309/ctxtVBAK-ZZSD_EXFACDT",
        ),
        "plan handover date": GuiElement(
            id=r"wnd[0]/usr/tabsTAXI_TABSTRIP_HEAD/tabpT\13/ssubSUBSCREEN_BODY:SAPMV45A:4312/sub8309:SAPMV45A:8309/ctxtVBAK-ZZSD_HANODT",
        ),
        "port of shipment": GuiElement(
            id=r"wnd[0]/usr/tabsTAXI_TABSTRIP_HEAD/tabpT\13/ssubSUBSCREEN_BODY:SAPMV45A:4312/sub8309:SAPMV45A:8309/ctxtVBAK-ZZSD_POS",
        ),
        "final destination": GuiElement(
            id=r"wnd[0]/usr/tabsTAXI_TABSTRIP_HEAD/tabpT\13/ssubSUBSCREEN_BODY:SAPMV45A:4312/sub8309:SAPMV45A:8309/ctxtVBAK-ZZSD_FDEST",
        ),
        "country of destination": GuiElement(
            id=r"wnd[0]/usr/tabsTAXI_TABSTRIP_HEAD/tabpT\13/ssubSUBSCREEN_BODY:SAPMV45A:4312/sub8309:SAPMV45A:8309/txtVBAK-ZZSD_CFDEST",
        ),
        "port of discharge": GuiElement(
            id=r"wnd[0]/usr/tabsTAXI_TABSTRIP_HEAD/tabpT\13/ssubSUBSCREEN_BODY:SAPMV45A:4312/sub8309:SAPMV45A:8309/ctxtVBAK-ZZSD_POD",
        ),
        "stake holder": GuiElement(
            id=r"wnd[0]/usr/tabsTAXI_TABSTRIP_HEAD/tabpT\13/ssubSUBSCREEN_BODY:SAPMV45A:4312/sub8309:SAPMV45A:8309/ctxtVBAK-ZZSTAKE_HOLDER",
        ),
    },
)

DEFAULT_SCREEN_ORDER_TOWELS_RUGS = [
    "VA01_INITIAL",
    "VA01_OVERVIEW",
    "VA01_SALES",
    "VA01_FAST_DATA_ENTRY",
    "HEADER_SALES",
    "HEADER_PARTNERS",
    "HEADER_TEXTS",
    "HEADER_ADD_DATA_A",
    {"name": "HEADER_ADD_DATA_B", "post_actions": {"type": "BACK"}},
]

DEFAULT_SCREEN_ORDER_BEDSHEETS = [
    "VA01_INITIAL",
    "VA01_OVERVIEW",
    "VA01_SALES",
    "VA01_ITEM_OVERVIEW",
    "HEADER_SALES",
    "HEADER_PARTNERS",
    "HEADER_TEXTS",
    "HEADER_ADD_DATA_A",
    {"name": "HEADER_ADD_DATA_B", "post_actions": {"type": "BACK"}},
]


VA01_MAPPINGS = {name: value for name, value in locals().items() if name.isupper()}
