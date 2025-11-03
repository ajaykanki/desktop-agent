from desktop_agent.worker.tasks.sap.sap_mappings import (
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
    elements=[
        GuiElement(name="order type", id=r"wnd[0]/usr/ctxtVBAK-AUART"),
        GuiElement(
            name="sales organization",
            id=r"wnd[0]/usr/ctxtVBAK-VKORG",
        ),
        GuiElement(
            name="distribution channel",
            id=r"wnd[0]/usr/ctxtVBAK-VTWEG",
        ),
        GuiElement(name="division", id=r"wnd[0]/usr/ctxtVBAK-SPART"),
    ],
)

VA01_OVERVIEW = Screen(
    name="VA01_OVERVIEW",
    elements=[
        GuiElement(
            name="sold to party",
            id=r"wnd[0]/usr/subSUBSCREEN_HEADER:SAPMV45A:4021/subPART-SUB:SAPMV45A:4701/ctxtKUAGV-KUNNR",
        ),
        GuiElement(
            name="ship to party",
            id=r"wnd[0]/usr/subSUBSCREEN_HEADER:SAPMV45A:4021/subPART-SUB:SAPMV45A:4701/ctxtKUWEV-KUNNR",
        ),
        GuiElement(
            name="po number",
            id=r"wnd[0]/usr/subSUBSCREEN_HEADER:SAPMV45A:4021/txtVBKD-BSTKD",
        ),
        GuiElement(
            name="po date",
            id=r"wnd[0]/usr/subSUBSCREEN_HEADER:SAPMV45A:4021/ctxtVBKD-BSTDK",
        ),
    ],
)

VA01_SALES = Screen(
    name="VA01_SALES",
    entry_point=[
        Action(
            type=ActionType.CLICK,
            target_id=r"wnd[0]/usr/tabsTAXI_TABSTRIP_OVERVIEW/tabpT\01",
        ),
    ],
    elements=[
        GuiElement(
            name="payment terms",
            id=r"wnd[0]/usr/tabsTAXI_TABSTRIP_OVERVIEW/tabpT\01/ssubSUBSCREEN_BODY:SAPMV45A:4400/ssubHEADER_FRAME:SAPMV45A:4440/ctxtVBKD-ZTERM",
        ),
        GuiElement(
            name="incoterms 1",
            id=r"wnd[0]/usr/tabsTAXI_TABSTRIP_OVERVIEW/tabpT\01/ssubSUBSCREEN_BODY:SAPMV45A:4400/ssubHEADER_FRAME:SAPMV45A:4440/lblVBKD-INCO1",
        ),
        GuiElement(
            name="incoterms 2",
            id=r"wnd[0]/usr/tabsTAXI_TABSTRIP_OVERVIEW/tabpT\01/ssubSUBSCREEN_BODY:SAPMV45A:4400/ssubHEADER_FRAME:SAPMV45A:4440/txtVBKD-INCO2",
        ),
    ],
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
    elements=[
        GuiElement(
            name="table",
            type=ElementType.TABLE,
            id=r"wnd[0]/usr/tabsTAXI_TABSTRIP_OVERVIEW/tabpT\02/ssubSUBSCREEN_BODY:SAPMV45A:4401/subSUBSCREEN_TC:SAPMV45A:4900/tblSAPMV45ATCTRL_U_ERF_AUFTRAG",
        ),
        GuiElement(
            name="select all",
            type=ElementType.BUTTON,
            id=r"wnd[0]/usr/tabsTAXI_TABSTRIP_OVERVIEW/tabpT\02/ssubSUBSCREEN_BODY:SAPMV45A:4401/subSUBSCREEN_TC:SAPMV45A:4900/subSUBSCREEN_BUTTONS:SAPMV45A:4050/btnBT_MKAL",
        ),
    ],
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
    elements=[
        GuiElement(
            name="char. display",
            id=r"wnd[0]/usr/tabsTAXI_TABSTRIP_OVERVIEW/tabpT\08/ssubSUBSCREEN_BODY:SAPMV45A:7901/cmbRV45A-MUEBS",
            type=ElementType.COMBOBOX,
        ),
        GuiElement(
            name="table",
            id=r"wnd[0]/usr/tabsTAXI_TABSTRIP_OVERVIEW/tabpT\08/ssubSUBSCREEN_BODY:SAPMV45A:7901/subSUBSCREEN_TC:SAPMV45A:7905/tblSAPMV45ATCTRL_U_MILL_SE_KONFIG",
            type=ElementType.TABLE,
        ),
        GuiElement(
            name="select all",
            type=ElementType.BUTTON,
            id=r"wnd[0]/usr/tabsTAXI_TABSTRIP_OVERVIEW/tabpT\08/ssubSUBSCREEN_BODY:SAPMV45A:7901/subSUBSCREEN_TC:SAPMV45A:7905/subSUBSCREEN_BUTTONS:SAPMV45A:4050/btnBT_MKAL",
        ),
    ],
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
    elements=[
        GuiElement(
            name="doc. currency",
            id=r"wnd[0]/usr/tabsTAXI_TABSTRIP_HEAD/tabpT\01/ssubSUBSCREEN_BODY:SAPMV45A:4301/ctxtVBAK-WAERK",
        ),
    ],
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
    elements=[
        GuiElement(
            name="partner function",
            type=ElementType.COMBOBOX,
            id=r"wnd[0]/usr/tabsTAXI_TABSTRIP_HEAD/tabpT\08/ssubSUBSCREEN_BODY:SAPMV45A:4352/subSUBSCREEN_PARTNER_OVERVIEW:SAPLV09C:1000/tblSAPLV09CGV_TC_PARTNER_OVERVIEW/cmbGVS_TC_DATA-REC-PARVW[0,4]",
        ),
        GuiElement(
            name="partner",
            type=ElementType.TEXT,
            id=r"wnd[0]/usr/tabsTAXI_TABSTRIP_HEAD/tabpT\08/ssubSUBSCREEN_BODY:SAPMV45A:4352/subSUBSCREEN_PARTNER_OVERVIEW:SAPLV09C:1000/tblSAPLV09CGV_TC_PARTNER_OVERVIEW/ctxtGVS_TC_DATA-REC-PARTNER[1,4]",
        ),
    ],
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
    elements=[
        GuiElement(
            name="click_notify_remiter",
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
        ),  # Select Notify/Remitter here in Column1,
        GuiElement(
            name="notify",
            id=r"wnd[0]/usr/tabsTAXI_TABSTRIP_HEAD/tabpT\09/ssubSUBSCREEN_BODY:SAPMV45A:4152/subSUBSCREEN_TEXT:SAPLV70T:2100/cntlSPLITTER_CONTAINER/shellcont/shellcont/shell/shellcont[1]/shell",  # Set the commission here
        ),
    ],
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
    elements=[
        GuiElement(
            name="channel type",
            id=r"wnd[0]/usr/tabsTAXI_TABSTRIP_HEAD/tabpT\12/ssubSUBSCREEN_BODY:SAPMV45A:4309/ctxtVBAK-ZECOM",
        ),
        GuiElement(
            name="sub channel type",
            id=r"wnd[0]/usr/tabsTAXI_TABSTRIP_HEAD/tabpT\12/ssubSUBSCREEN_BODY:SAPMV45A:4309/ctxtVBAK-ZSCTYP",
        ),
        GuiElement(
            name="order type",
            type=ElementType.COMBOBOX,
            id=r"wnd[0]/usr/tabsTAXI_TABSTRIP_HEAD/tabpT\12/ssubSUBSCREEN_BODY:SAPMV45A:4309/cmbVBAK-ZORD_TYPE",
        ),
    ],
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
    elements=[
        GuiElement(
            name="window start date",
            id=r"wnd[0]/usr/tabsTAXI_TABSTRIP_HEAD/tabpT\13/ssubSUBSCREEN_BODY:SAPMV45A:4312/sub8309:SAPMV45A:8309/ctxtVBAK-ZZSD_STARTDT",
        ),
        GuiElement(
            name="window cancel date",
            id=r"wnd[0]/usr/tabsTAXI_TABSTRIP_HEAD/tabpT\13/ssubSUBSCREEN_BODY:SAPMV45A:4312/sub8309:SAPMV45A:8309/ctxtVBAK-ZZSD_CANDT",
        ),
        GuiElement(
            name="plan ex-factory date",
            id=r"wnd[0]/usr/tabsTAXI_TABSTRIP_HEAD/tabpT\13/ssubSUBSCREEN_BODY:SAPMV45A:4312/sub8309:SAPMV45A:8309/ctxtVBAK-ZZSD_EXFACDT",
        ),
        GuiElement(
            name="plan handover date",
            id=r"wnd[0]/usr/tabsTAXI_TABSTRIP_HEAD/tabpT\13/ssubSUBSCREEN_BODY:SAPMV45A:4312/sub8309:SAPMV45A:8309/ctxtVBAK-ZZSD_HANODT",
        ),
        GuiElement(
            name="port of shipment",
            id=r"wnd[0]/usr/tabsTAXI_TABSTRIP_HEAD/tabpT\13/ssubSUBSCREEN_BODY:SAPMV45A:4312/sub8309:SAPMV45A:8309/ctxtVBAK-ZZSD_POS",
        ),
        GuiElement(
            name="final destination",
            id=r"wnd[0]/usr/tabsTAXI_TABSTRIP_HEAD/tabpT\13/ssubSUBSCREEN_BODY:SAPMV45A:4312/sub8309:SAPMV45A:8309/ctxtVBAK-ZZSD_FDEST",
        ),
        GuiElement(
            name="country of destination",
            id=r"wnd[0]/usr/tabsTAXI_TABSTRIP_HEAD/tabpT\13/ssubSUBSCREEN_BODY:SAPMV45A:4312/sub8309:SAPMV45A:8309/txtVBAK-ZZSD_CFDEST",
        ),
        GuiElement(
            name="port of discharge",
            id=r"wnd[0]/usr/tabsTAXI_TABSTRIP_HEAD/tabpT\13/ssubSUBSCREEN_BODY:SAPMV45A:4312/sub8309:SAPMV45A:8309/ctxtVBAK-ZZSD_POD",
        ),
        GuiElement(
            name="stake holder",
            id=r"wnd[0]/usr/tabsTAXI_TABSTRIP_HEAD/tabpT\13/ssubSUBSCREEN_BODY:SAPMV45A:4312/sub8309:SAPMV45A:8309/ctxtVBAK-ZZSTAKE_HOLDER",
        ),
    ],
)

VA01_MAPPINGS = {name: value for name, value in locals().items() if name.isupper()}
