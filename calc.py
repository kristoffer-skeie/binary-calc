import tkinter as tk
from tkinter import ttk

HEX_DIGITS = "0123456789ABCDEF"

def todecimal(binary):
    binary = binary.strip()
    if not binary or any(c not in "01" for c in binary):
        raise ValueError(f"Not a binary number: {binary!r}")
    
    decimal = 0
    for position, bit in enumerate(reversed(binary)):
        if bit == "1":
            decimal += 2 ** position
    return decimal


def tobinary(n):
    if n < 0:
        return "-" + tobinary(-n)
    if n == 0:
        return "0"
    bits = ""
    while n > 0:
        bits = str(n % 2) + bits
        n //= 2
    return bits


def hextodecimal(hexstr):
    hexstr = hexstr.strip().upper()
    if hexstr.startswith("0X"):
        hexstr = hexstr[2:]
    if not hexstr or any(c not in HEX_DIGITS for c in hexstr):
        raise ValueError(f"Not a hex number: {hexstr!r}")
    decimal = 0
    for position, digit in enumerate(reversed(hexstr)):
        decimal += HEX_DIGITS.index(digit) * 16 ** position
    return decimal


def tohex(n):
    if n < 0:
        return "-" + tohex(-n)
    if n == 0:
        return "0"
    digits = ""
    while n > 0:
        digits = HEX_DIGITS[n % 16] + digits
        n //= 16
    return digits

def parse(text, base):
    text = text.strip().replace(" ", "")
    negative = text.startswith("-")
    if negative:
        text = text[1:]
    if base == "BIN":
        value = todecimal(text)
    elif base == "HEX":
        value = hextodecimal(text)
    else:
        if not text.isdigit():
            raise ValueError(f"Not a decimal number: {text!r}")
        value = int(text)
    return -value if negative else value


def group(s, size):
    sign = "-" if s.startswith("-") else ""
    s = s.lstrip("-")
    s = s.zfill(-(-len(s) // size) * size)
    return sign + " ".join(s[i:i + size] for i in range(0, len(s), size))

# UI
class CalcApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Binary / Hex Calc")
        self.resizable(False, False)
        style = ttk.Style(self)
        style.configure("Out.TLabel", font=("Consolas", 13))
        style.configure("Err.TLabel", foreground="#c0392b")

        pad = {"padx": 8, "pady": 4}

        # --- Converter ---
        conv = ttk.LabelFrame(self, text="Convert")
        conv.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))

        self.conv_base = tk.StringVar(value="BIN")
        self.conv_input = tk.StringVar()
        entry = ttk.Entry(conv, textvariable=self.conv_input, width=30, font=("Consolas", 13))
        entry.grid(row=0, column=0, columnspan=3, sticky="ew", **pad)
        entry.focus()
        for i, b in enumerate(("BIN", "DEC", "HEX")):
            ttk.Radiobutton(conv, text=b, value=b, variable=self.conv_base,
                            command=self.update_conv).grid(row=1, column=i, **pad)

        self.conv_out = {}
        for i, b in enumerate(("BIN", "DEC", "HEX")):
            ttk.Label(conv, text=b + ":").grid(row=2 + i, column=0, sticky="e", **pad)
            lbl = ttk.Label(conv, text="", style="Out.TLabel")
            lbl.grid(row=2 + i, column=1, columnspan=2, sticky="w", **pad)
            self.conv_out[b] = lbl
        self.conv_err = ttk.Label(conv, text="", style="Err.TLabel")
        self.conv_err.grid(row=5, column=0, columnspan=3, **pad)
        self.conv_input.trace_add("write", lambda *_: self.update_conv())

        # --- Calculator ---
        calc = ttk.LabelFrame(self, text="Calculate")
        calc.grid(row=1, column=0, sticky="ew", padx=10, pady=(5, 10))

        self.calc_base = tk.StringVar(value="BIN")
        for i, b in enumerate(("BIN", "DEC", "HEX")):
            ttk.Radiobutton(calc, text=b, value=b, variable=self.calc_base,
                            command=self.update_calc).grid(row=0, column=i, **pad)

        self.a = tk.StringVar()
        self.b = tk.StringVar()
        self.op = tk.StringVar(value="+")
        ttk.Entry(calc, textvariable=self.a, width=14, font=("Consolas", 13)).grid(row=1, column=0, **pad)
        ops = ttk.Combobox(calc, textvariable=self.op, width=4, state="readonly",
                           values=["+", "-", "*", "//", "%", "AND", "OR", "XOR", "<<", ">>"])
        ops.grid(row=1, column=1, **pad)
        ttk.Entry(calc, textvariable=self.b, width=14, font=("Consolas", 13)).grid(row=1, column=2, **pad)

        self.calc_out = {}
        for i, b in enumerate(("BIN", "DEC", "HEX")):
            ttk.Label(calc, text=b + ":").grid(row=2 + i, column=0, sticky="e", **pad)
            lbl = ttk.Label(calc, text="", style="Out.TLabel")
            lbl.grid(row=2 + i, column=1, columnspan=2, sticky="w", **pad)
            self.calc_out[b] = lbl
        self.calc_err = ttk.Label(calc, text="", style="Err.TLabel")
        self.calc_err.grid(row=5, column=0, columnspan=3, **pad)

        for var in (self.a, self.b, self.op):
            var.trace_add("write", lambda *_: self.update_calc())

        # Feature: the calculater always on top of other windows
        self.topmost = tk.BooleanVar(value=True)
        ttk.Checkbutton(self, text="Always on top", variable=self.topmost,
                        command=self.update_topmost).grid(row=2, column=0, sticky="w", padx=10, pady=(0, 10))
        self.update_topmost()

        self.bind("<Escape>", lambda e: self.destroy())

    def update_topmost(self):
        self.attributes("-topmost", self.topmost.get())

    def show(self, labels, value):
        labels["BIN"].config(text=group(tobinary(value), 4))
        labels["DEC"].config(text=str(value))
        labels["HEX"].config(text=tohex(value))

    def clear(self, labels):
        for lbl in labels.values():
            lbl.config(text="")

    def update_conv(self):
        text = self.conv_input.get()
        if not text.strip():
            self.clear(self.conv_out)
            self.conv_err.config(text="")
            return
        try:
            self.show(self.conv_out, parse(text, self.conv_base.get()))
            self.conv_err.config(text="")
        except ValueError as e:
            self.clear(self.conv_out)
            self.conv_err.config(text=str(e))

    def update_calc(self):
        if not self.a.get().strip() or not self.b.get().strip():
            self.clear(self.calc_out)
            self.calc_err.config(text="")
            return
        try:
            base = self.calc_base.get()
            a, b = parse(self.a.get(), base), parse(self.b.get(), base)
            op = self.op.get()
            if op in ("//", "%") and b == 0:
                raise ValueError("Division by zero")
            if op in ("<<", ">>") and b < 0:
                raise ValueError("Negative shift")
            result = {
                "+": lambda: a + b, "-": lambda: a - b, "*": lambda: a * b,
                "//": lambda: a // b, "%": lambda: a % b,
                "AND": lambda: a & b, "OR": lambda: a | b, "XOR": lambda: a ^ b,
                "<<": lambda: a << b, ">>": lambda: a >> b,
            }[op]()
            self.show(self.calc_out, result)
            self.calc_err.config(text="")
        except ValueError as e:
            self.clear(self.calc_out)
            self.calc_err.config(text=str(e))


if __name__ == "__main__":
    CalcApp().mainloop()
