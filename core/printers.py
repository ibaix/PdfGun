import win32print


def list_printers() -> list[str]:
    flags = win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS
    printers = win32print.EnumPrinters(flags)
    return sorted({entry[2] for entry in printers})


def get_default_printer() -> str | None:
    try:
        return win32print.GetDefaultPrinter()
    except win32print.error:
        return None
