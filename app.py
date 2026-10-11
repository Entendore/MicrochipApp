import sys
import math
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QStackedWidget, QFrame, QGridLayout,
    QComboBox, QLineEdit, QSpinBox, QDoubleSpinBox, QCheckBox,
    QGroupBox, QScrollArea, QProgressBar, QRadioButton,
    QButtonGroup, QTabWidget, QSlider, QListWidget, QAbstractItemView
)
from PySide6.QtCore import Qt, QRectF, QPointF, QTimer
from PySide6.QtGui import (
    QPainter, QPen, QBrush, QColor, QFont, QPainterPath,
    QLinearGradient, QPolygonF
)

# ──────────────────────── STYLESHEET ────────────────────────
DARK_STYLESHEET = """
QMainWindow { background-color: #0d1117; }
QWidget { color: #c9d1d9; font-family: 'Segoe UI', Arial; font-size: 13px; }
QFrame#sidebar { background-color: #161b22; border-right: 1px solid #30363d; }
QPushButton#nav_btn {
    background-color: transparent; color: #8b949e; border: none;
    padding: 10px 14px; text-align: left; font-size: 13px; border-radius: 6px; margin: 1px 6px;
}
QPushButton#nav_btn:hover { background-color: #1f2937; color: #c9d1d9; }
QPushButton#nav_btn:checked { background-color: #1f6feb; color: #ffffff; }
QLabel#title { font-size: 20px; font-weight: bold; color: #58a6ff; }
QGroupBox {
    background-color: #161b22; border: 1px solid #30363d; border-radius: 8px;
    margin-top: 14px; padding: 14px; padding-top: 24px; font-weight: bold; color: #79c0ff;
}
QGroupBox::title { subcontrol-origin: margin; left: 12px; padding: 0 4px; }
QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {
    background-color: #0d1117; border: 1px solid #30363d; border-radius: 4px;
    padding: 6px 8px; color: #c9d1d9;
}
QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus { border-color: #1f6feb; }
QPushButton#calc_btn {
    background-color: #238636; color: #ffffff; border: none; border-radius: 6px;
    padding: 8px 16px; font-weight: bold;
}
QPushButton#calc_btn:hover { background-color: #2ea043; }
QSlider::groove:horizontal { background: #30363d; height: 6px; border-radius: 3px; }
QSlider::handle:horizontal { background: #1f6feb; width: 14px; margin: -4px 0; border-radius: 7px; }
QSlider::sub-page:horizontal { background: #1f6feb; border-radius: 3px; }
QScrollArea { border: none; background-color: transparent; }
QTabWidget::pane { border: 1px solid #30363d; border-radius: 4px; background-color: #161b22; }
QTabBar::tab { background-color: #0d1117; color: #8b949e; padding: 6px 12px; border: 1px solid #30363d; border-bottom: none; border-top-left-radius: 4px; border-top-right-radius: 4px; }
QTabBar::tab:selected { background-color: #161b22; color: #58a6ff; }
QListWidget { background-color: #0d1117; border: 1px solid #30363d; border-radius: 4px; }
"""

# ──────────────────────── HELPERS ────────────────────────
def format_value(value, unit):
    if value == 0: return f"0 {unit}"
    abs_v = abs(value)
    if abs_v >= 1e6: return f"{value/1e6:.3f} M{unit}"
    elif abs_v >= 1e3: return f"{value/1e3:.3f} k{unit}"
    elif abs_v >= 1: return f"{value:.3f} {unit}"
    elif abs_v >= 1e-3: return f"{value*1e3:.3f} m{unit}"
    elif abs_v >= 1e-6: return f"{value*1e6:.3f} µ{unit}"
    elif abs_v >= 1e-9: return f"{value*1e9:.3f} n{unit}"
    else: return f"{value*1e12:.3f} p{unit}"

# ──────────────────────── 555 TIMER + OSCILLOSCOPE ────────────────────────
class OscilloscopeWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.high_time = 0.7
        self.low_time = 0.3
        self.offset = 0
        self.setFixedHeight(150)
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate)
        self.timer.start(30)

    def animate(self):
        self.offset += 2
        self.update()

    def set_timings(self, high, low):
        period = high + low
        if period > 0:
            scale = 1.0 / period
            self.high_time = high * scale
            self.low_time = low * scale

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        painter.fillRect(self.rect(), QColor(10, 15, 20))

        # Grid
        painter.setPen(QPen(QColor(30, 60, 30), 1))
        for i in range(0, w, 30): painter.drawLine(i, 0, i, h)
        for i in range(0, h, 30): painter.drawLine(0, i, w, i)

        # Waveform
        painter.setPen(QPen(QColor(0, 255, 0), 2))
        y_high = h * 0.2
        y_low = h * 0.8
        
        path = QPainterPath()
        x = -self.offset % 100
        path.moveTo(0, y_low)
        
        while x < w:
            h_width = self.high_time * 100
            l_width = self.low_time * 100
            path.lineTo(x, y_low)
            path.lineTo(x, y_high)
            path.lineTo(x + h_width, y_high)
            path.lineTo(x + h_width, y_low)
            path.lineTo(x + h_width + l_width, y_low)
            x += h_width + l_width
            
        painter.drawPath(path)
        painter.end()

class Timer555Page(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 10, 20, 10)
        layout.addWidget(QLabel("⏱️ 555 Timer & Oscilloscope"))
        layout.addWidget(OscilloscopeWidget() if False else QLabel("")) # Placeholder setup below
        
        self.scope = OscilloscopeWidget()
        layout.addWidget(self.scope)

        g = QGroupBox("Astable Component Values")
        gl = QGridLayout(g)
        self.r1 = QDoubleSpinBox(); self.r1.setRange(1, 1e7); self.r1.setValue(10e3); self.r1.setSuffix(" Ω")
        self.r2 = QDoubleSpinBox(); self.r2.setRange(1, 1e7); self.r2.setValue(47e3); self.r2.setSuffix(" Ω")
        self.c1 = QDoubleSpinBox(); self.c1.setRange(1e-12, 1); self.c1.setValue(10e-9); self.c1.setDecimals(10); self.c1.setSuffix(" F")
        gl.addWidget(QLabel("R1:"), 0, 0); gl.addWidget(self.r1, 0, 1)
        gl.addWidget(QLabel("R2:"), 1, 0); gl.addWidget(self.r2, 1, 1)
        gl.addWidget(QLabel("C1:"), 2, 0); gl.addWidget(self.c1, 2, 1)
        
        btn = QPushButton("Calculate & Visualize"); btn.setObjectName("calc_btn")
        btn.clicked.connect(self.calc); gl.addWidget(btn, 3, 0, 1, 2)
        layout.addWidget(g)

        self.result = QLabel("Set values and calculate")
        self.result.setStyleSheet("color: #58a6ff; font-weight: bold; padding: 10px; background: #161b22; border-radius: 4px;")
        layout.addWidget(self.result)
        layout.addStretch()
        self.calc()

    def calc(self):
        r1, r2, c = self.r1.value(), self.r2.value(), self.c1.value()
        high = 0.693 * (r1 + r2) * c
        low = 0.693 * r2 * c
        freq = 1 / (high + low) if (high + low) > 0 else 0
        duty = (high / (high + low)) * 100 if (high + low) > 0 else 0
        self.result.setText(f"Freq: {format_value(freq, 'Hz')} | High: {format_value(high, 's')} | Low: {format_value(low, 's')} | Duty: {duty:.1f}%")
        self.scope.set_timings(high, low)

# ──────────────────────── VOLTAGE DIVIDER VISUALIZER ────────────────────────
class VoltageDividerVisual(QWidget):
    def __init__(self):
        super().__init__()
        self.vin = 12; self.r1 = 10000; self.r2 = 10000
        self.setFixedHeight(200)

    def update_vals(self, vin, r1, r2):
        self.vin, self.r1, self.r2 = vin, r1, r1 + r2 # fix: r2
        self.r2 = r2
        self.update()

    def paintEvent(self, event):
        p = QPainter(self); p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        p.fillRect(self.rect(), QColor(13, 17, 23))
        
        vout = self.vin * self.r2 / (self.r1 + self.r2) if (self.r1+self.r2)>0 else 0
        current = self.vin / (self.r1+self.r2) if (self.r1+self.r2)>0 else 0
        
        cx = w//2
        # Wires
        p.setPen(QPen(QColor(200,200,200), 3))
        p.drawLine(cx, 20, cx, 50) # Top
        p.drawLine(cx, 150, cx, 180) # Bottom
        
        # R1
        p.setPen(QPen(QColor(210, 180, 140), 3))
        p.drawRect(cx-15, 50, 30, 45)
        p.setPen(QPen(QColor(139, 148, 158)))
        p.drawText(QRectF(cx-40, 55, 30, 20), Qt.AlignRight, f"{format_value(self.r1, 'Ω')}")
        
        # Junction
        p.setPen(QPen(QColor(200,200,200), 3))
        p.drawLine(cx, 95, cx+50, 95)
        
        # R2
        p.setPen(QPen(QColor(210, 180, 140), 3))
        p.drawRect(cx-15, 95, 30, 45)
        p.setPen(QPen(QColor(139, 148, 158)))
        p.drawText(QRectF(cx-40, 105, 30, 20), Qt.AlignRight, f"{format_value(self.r2, 'Ω')}")
        
        # Labels
        p.setPen(QPen(QColor(255, 100, 100))); p.setFont(QFont("Arial", 12, QFont.Bold))
        p.drawText(cx+55, 98, f"Vout: {vout:.2f}V")
        p.drawText(20, 30, f"Vin: {self.vin:.1f}V")
        p.setPen(QPen(QColor(100, 255, 100)))
        p.drawText(20, 180, f"I: {format_value(current, 'A')}")
        p.end()

class VoltageDividerPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self); layout.setContentsMargins(20, 10, 20, 10)
        layout.addWidget(QLabel("⚡ Voltage Divider Visualizer"))
        
        self.vis = VoltageDividerVisual(); layout.addWidget(self.vis)
        
        g = QGroupBox("Parameters"); gl = QGridLayout(g)
        self.vin_sl = QSlider(Qt.Horizontal); self.vin_sl.setRange(0, 50); self.vin_sl.setValue(12)
        self.r1_sl = QSlider(Qt.Horizontal); self.r1_sl.setRange(1, 100); self.r1_sl.setValue(10)
        self.r2_sl = QSlider(Qt.Horizontal); self.r2_sl.setRange(1, 100); self.r2_sl.setValue(10)
        
        self.vin_lbl = QLabel("12.0 V"); self.r1_lbl = QLabel("10.0 kΩ"); self.r2_lbl = QLabel("10.0 kΩ")
        
        gl.addWidget(QLabel("Vin:"), 0, 0); gl.addWidget(self.vin_sl, 0, 1); gl.addWidget(self.vin_lbl, 0, 2)
        gl.addWidget(QLabel("R1:"), 1, 0); gl.addWidget(self.r1_sl, 1, 1); gl.addWidget(self.r1_lbl, 1, 2)
        gl.addWidget(QLabel("R2:"), 2, 0); gl.addWidget(self.r2_sl, 2, 1); gl.addWidget(self.r2_lbl, 2, 2)
        
        for s in [self.vin_sl, self.r1_sl, self.r2_sl]: s.valueChanged.connect(self.update_vis)
        layout.addWidget(g); layout.addStretch()
        self.update_vis()

    def update_vis(self):
        vin = self.vin_sl.value(); r1 = self.r1_sl.value()*1000; r2 = self.r2_sl.value()*1000
        self.vin_lbl.setText(f"{vin:.1f} V"); self.r1_lbl.setText(f"{r1/1000:.1f} kΩ"); self.r2_lbl.setText(f"{r2/1000:.1f} kΩ")
        self.vis.update_vals(vin, r1, r2)

# ──────────────────────── LED RESISTOR CALCULATOR ────────────────────────
class LEDCircuitVisual(QWidget):
    def __init__(self):
        super().__init__()
        self.led_on = False; self.setFixedHeight(150)
    def set_on(self, on): self.led_on = on; self.update()
    def paintEvent(self, event):
        p = QPainter(self); p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height(); p.fillRect(self.rect(), QColor(13,17,23))
        cx = w//2
        p.setPen(QPen(QColor(200,200,200), 3))
        p.drawLine(cx-80, h//2, cx-40, h//2) # wire
        p.drawRect(cx-40, h//2-10, 40, 20) # R
        p.drawLine(cx, h//2, cx+30, h//2) # wire
        
        # LED Triangle
        p.setPen(QPen(QColor(200,200,200), 2))
        p.drawPolygon(QPolygonF([QPointF(cx+30, h//2-20), QPointF(cx+30, h//2+20), QPointF(cx+70, h//2)]))
        p.drawLine(cx+70, h//2-20, cx+70, h//2+20) # Cathode line
        
        if self.led_on:
            p.setPen(Qt.NoPen); p.setBrush(QBrush(QColor(255, 0, 0, 150)))
            p.drawEllipse(QPointF(cx+50, h//2), 30, 30)
        p.end()

class LEDResistorPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self); layout.setContentsMargins(20, 10, 20, 10)
        layout.addWidget(QLabel("💡 LED Resistor Calculator"))
        self.vis = LEDCircuitVisual(); layout.addWidget(self.vis)
        
        g = QGroupBox("Parameters"); gl = QGridLayout(g)
        self.vsrc = QDoubleSpinBox(); self.vsrc.setRange(0, 50); self.vsrc.setValue(5); self.vsrc.setSuffix(" V")
        self.vled = QDoubleSpinBox(); self.vled.setRange(0, 10); self.vled.setValue(2.0); self.vled.setSuffix(" V")
        self.iled = QDoubleSpinBox(); self.iled.setRange(0, 1); self.iled.setValue(0.020); self.iled.setSuffix(" A"); self.iled.setDecimals(3); self.iled.setSingleStep(0.001)
        
        gl.addWidget(QLabel("Source Voltage:"), 0, 0); gl.addWidget(self.vsrc, 0, 1)
        gl.addWidget(QLabel("LED Forward V:"), 1, 0); gl.addWidget(self.vled, 1, 1)
        gl.addWidget(QLabel("LED Current:"), 2, 0); gl.addWidget(self.iled, 2, 1)
        
        btn = QPushButton("Calculate"); btn.setObjectName("calc_btn"); btn.clicked.connect(self.calc)
        gl.addWidget(btn, 3, 0, 1, 2); layout.addWidget(g)
        
        self.res = QLabel(""); self.res.setStyleSheet("font-size: 16px; color: #58a6ff; font-weight: bold; padding: 10px; background: #161b22; border-radius: 4px;")
        layout.addWidget(self.res); layout.addStretch(); self.calc()

    def calc(self):
        vs, vl, il = self.vsrc.value(), self.vled.value(), self.iled.value()
        if il > 0 and vs > vl:
            r = (vs - vl) / il; p = (vs - vl) * il
            self.res.setText(f"Resistor: {format_value(r, 'Ω')} | Power: {format_value(p, 'W')}")
            self.vis.set_on(True)
        else:
            self.res.setText("Invalid input (Vsrc must be > Vled, I > 0)"); self.vis.set_on(False)

# ──────────────────────── CAPACITOR CODE CALCULATOR ────────────────────────
class CapacitorCodePage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self); layout.setContentsMargins(20, 10, 20, 10)
        layout.addWidget(QLabel("🔋 Capacitor Code Calculator"))
        layout.addWidget(QLabel("Enter 3-digit code (e.g., 104 = 100nF):"))
        
        self.code = QLineEdit("104"); self.code.textChanged.connect(self.calc)
        layout.addWidget(self.code)
        
        self.res = QLabel(""); self.res.setStyleSheet("font-size: 18px; color: #58a6ff; font-weight: bold; padding: 15px; background: #161b22; border-radius: 4px;")
        layout.addWidget(self.res); layout.addStretch(); self.calc()

    def calc(self):
        code = self.code.text().strip()
        if len(code) == 3 and code.isdigit():
            val = int(code[:2]) * (10 ** int(code[2]))
            self.res.setText(f"Value: {format_value(val * 1e-12, 'F')} ({val} pF)")
        else:
            self.res.setText("Enter valid 3-digit code")

# ──────────────────────── SERIES/PARALLEL CALC ────────────────────────
class SeriesParallelPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self); layout.setContentsMargins(20, 10, 20, 10)
        layout.addWidget(QLabel("🔗 Series / Parallel Calculator"))
        
        hl = QHBoxLayout()
        self.type_combo = QComboBox(); self.type_combo.addItems(["Resistor (Ω)", "Capacitor (F)", "Inductor (H)"])
        self.config_combo = QComboBox(); self.config_combo.addItems(["Series", "Parallel"])
        hl.addWidget(self.type_combo); hl.addWidget(self.config_combo); layout.addLayout(hl)
        
        self.vals = QListWidget(); self.vals.setSelectionMode(QAbstractItemView.SingleSelection)
        layout.addWidget(self.vals)
        
        inp_layout = QHBoxLayout()
        self.new_val = QDoubleSpinBox(); self.new_val.setRange(1e-12, 1e9); self.new_val.setDecimals(6); self.new_val.setValue(10)
        add_btn = QPushButton("Add"); add_btn.clicked.connect(self.add_val); rm_btn = QPushButton("Remove"); rm_btn.clicked.connect(self.rm_val)
        inp_layout.addWidget(self.new_val); inp_layout.addWidget(add_btn); inp_layout.addWidget(rm_btn)
        layout.addLayout(inp_layout)
        
        self.res = QLabel("Add components to calculate"); self.res.setStyleSheet("font-size: 16px; color: #58a6ff; font-weight: bold; padding: 10px; background: #161b22; border-radius: 4px;")
        layout.addWidget(self.res); layout.addStretch()
        
        add_btn.clicked.connect(self.calc); rm_btn.clicked.connect(self.calc)
        self.config_combo.currentTextChanged.connect(self.calc); self.type_combo.currentTextChanged.connect(self.calc)

    def add_val(self): self.vals.addItem(f"{self.new_val.value()}"); self.calc()
    def rm_val(self): 
        for i in self.vals.selectedItems(): self.vals.takeItem(self.vals.row(i))
        self.calc()

    def calc(self):
        if self.vals.count() == 0: self.res.setText("Add components"); return
        vals = [float(self.vals.item(i).text()) for i in range(self.vals.count())]
        is_series = self.config_combo.currentText() == "Series"
        is_cap = self.type_combo.currentIndex() == 1
        
        # For capacitors, series/parallel math is flipped relative to resistors
        if (is_series and not is_cap) or (not is_series and is_cap):
            total = sum(vals)
        else:
            total = 1 / sum(1/v for v in vals if v > 0) if all(v > 0 for v in vals) else 0
            
        units = ["Ω", "F", "H"][self.type_combo.currentIndex()]
        self.res.setText(f"Total: {format_value(total, units)}")

# ──────────────────────── UNIT CONVERTER ────────────────────────
class UnitConverterPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self); layout.setContentsMargins(20, 10, 20, 10)
        layout.addWidget(QLabel("📏 Unit Converter"))
        
        gl = QGridLayout()
        self.type_combo = QComboBox(); self.type_combo.addItems(["Resistance", "Capacitance", "Voltage", "Current"])
        self.from_val = QDoubleSpinBox(); self.from_val.setRange(0, 1e12); self.from_val.setDecimals(6); self.from_val.setValue(1)
        self.from_unit = QComboBox(); self.to_unit = QComboBox()
        self.to_val = QLabel(""); self.to_val.setStyleSheet("color: #58a6ff; font-weight: bold; font-size: 16px;")
        
        self.units = {
            "Resistance": [("pΩ",1e-12),("nΩ",1e-9),("µΩ",1e-6),("mΩ",1e-3),("Ω",1),("kΩ",1e3),("MΩ",1e6),("GΩ",1e9)],
            "Capacitance": [("pF",1e-12),("nF",1e-9),("µF",1e-6),("mF",1e-3),("F",1),("kF",1e3)],
            "Voltage": [("µV",1e-6),("mV",1e-3),("V",1),("kV",1e3),("MV",1e6)],
            "Current": [("nA",1e-9),("µA",1e-6),("mA",1e-3),("A",1),("kA",1e3)]
        }
        
        self.type_combo.currentTextChanged.connect(self.update_units)
        gl.addWidget(QLabel("Type:"), 0, 0); gl.addWidget(self.type_combo, 0, 1)
        gl.addWidget(QLabel("Value:"), 1, 0); gl.addWidget(self.from_val, 1, 1); gl.addWidget(self.from_unit, 1, 2)
        gl.addWidget(QLabel("To:"), 2, 0); gl.addWidget(self.to_unit, 2, 1); gl.addWidget(self.to_val, 2, 2)
        layout.addLayout(gl)
        
        self.update_units("Resistance")
        for w in [self.from_val, self.from_unit, self.to_unit]: 
            if isinstance(w, QDoubleSpinBox): w.valueChanged.connect(self.convert)
            else: w.currentTextChanged.connect(self.convert)
        layout.addStretch()

    def update_units(self, type_name):
        self.from_unit.clear(); self.to_unit.clear()
        for name, _ in self.units[type_name]: self.from_unit.addItem(name); self.to_unit.addItem(name)
        self.from_unit.setCurrentText("Ω" if type_name=="Resistance" else "F" if type_name=="Capacitance" else "V" if type_name=="Voltage" else "A")
        self.to_unit.setCurrentIndex(0)

    def convert(self):
        type_name = self.type_combo.currentText()
        base = self.units[type_name]
        from_mult = dict(base)[self.from_unit.currentText()]
        to_mult = dict(base)[self.to_unit.currentText()]
        val = self.from_val.value() * from_mult / to_mult
        self.to_val.setText(f"{val:.6f}")

# ──────────────────────── ATMEGA328P REGISTER SIMULATOR ────────────────────────
class ATmegaVisual(QWidget):
    def __init__(self):
        super().__init__()
        self.ddrb = 0; self.portb = 0; self.setFixedHeight(200)

    def set_regs(self, ddrb, portb): self.ddrb = ddrb; self.portb = portb; self.update()

    def paintEvent(self, event):
        p = QPainter(self); p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height(); p.fillRect(self.rect(), QColor(13,17,23))
        
        p.setPen(QPen(QColor(88,166,255))); p.setFont(QFont("Consolas", 12, QFont.Bold))
        p.drawText(10, 20, "ATmega328P - PORTB Sim (Pins 8-13 / PB0-PB5)")
        
        for i in range(8):
            x = 20 + i * (w-40)//8
            ddrb_bit = (self.ddrb >> i) & 1
            portb_bit = (self.portb >> i) & 1
            
            # Draw Pin
            color = QColor(100,100,100) # Disabled / Input
            label = "IN (Z)"
            if ddrb_bit == 1:
                if portb_bit == 1: color = QColor(255, 50, 50); label = "OUT (H)"
                else: color = QColor(50, 50, 255); label = "OUT (L)"
            elif portb_bit == 1: color = QColor(255, 165, 0); label = "IN (PU)" # Pull-up

            p.setBrush(QBrush(color)); p.setPen(QPen(QColor(200,200,200), 2))
            p.drawRoundedRect(QRectF(x, 60, 40, 80), 4, 4)
            p.setPen(QPen(QColor(255,255,255))); p.setFont(QFont("Consolas", 9))
            p.drawText(QRectF(x, 65, 40, 20), Qt.AlignCenter, f"PB{i}")
            p.drawText(QRectF(x, 110, 40, 20), Qt.AlignCenter, label)
        p.end()

class ATmegaRegisterPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self); layout.setContentsMargins(20, 10, 20, 10)
        layout.addWidget(QLabel("💾 ATmega328P Register Simulator"))
        
        self.vis = ATmegaVisual(); layout.addWidget(self.vis)
        
        g = QGroupBox("Toggle Bits"); gl = QGridLayout(g)
        self.ddrb_checks = []; self.portb_checks = []
        for i in range(8):
            idx = 7 - i # MSB left
            gl.addWidget(QLabel(f"Bit {idx}"), 0, i+1)
            d = QCheckBox(); d.setChecked(False); d.stateChanged.connect(self.update_regs)
            p = QCheckBox(); p.setChecked(False); p.stateChanged.connect(self.update_regs)
            self.ddrb_checks.append(d); self.portb_checks.append(p)
            gl.addWidget(d, 1, i+1); gl.addWidget(p, 2, i+1)
        
        gl.addWidget(QLabel("DDRB:"), 1, 0); gl.addWidget(QLabel("PORTB:"), 2, 0)
        layout.addWidget(g)
        
        self.info = QLabel("DDRx=1: Output | DDRx=0, PORTx=1: Pull-up | DDRx=0, PORTx=0: Input (High-Z)")
        self.info.setWordWrap(True); self.info.setStyleSheet("color: #8b949e; padding: 5px; background: #161b22; border-radius: 4px;")
        layout.addWidget(self.info); layout.addStretch()

    def update_regs(self):
        ddrb = sum(1<<i for i, c in enumerate(self.ddrb_checks) if c.isChecked())
        portb = sum(1<<i for i, c in enumerate(self.portb_checks) if c.isChecked())
        self.vis.set_regs(ddrb, portb)

# ──────────────────────── UART VISUALIZER ────────────────────────
class UARTVisualWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.bits = [1]*10 # Idle
        self.offset = 0; self.setFixedHeight(120)
        self.timer = QTimer(self); self.timer.timeout.connect(self.animate); self.timer.start(50)
    
    def set_char(self, char):
        val = ord(char)
        self.bits = [0] # Start
        for i in range(8): self.bits.append((val >> i) & 1) # LSB first
        self.bits.append(1) # Stop
        self.offset = 0

    def animate(self): self.offset += 2; self.update()

    def paintEvent(self, event):
        p = QPainter(self); p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height(); p.fillRect(self.rect(), QColor(13,17,23))
        
        p.setPen(QPen(QColor(30,60,30), 1)); p.drawLine(0, h//4, w, h//4); p.drawLine(0, 3*h//4, w, 3*h//4)
        
        p.setPen(QPen(QColor(0, 255, 0), 3))
        y_h = h//4; y_l = 3*h//4
        bit_w = 60; x = -self.offset % (len(self.bits) * bit_w)
        
        path = QPainterPath(); path.moveTo(0, y_l)
        while x < w + bit_w:
            for bit in self.bits:
                y = y_h if bit else y_l
                path.lineTo(x, y); path.lineTo(x + bit_w, y)
                x += bit_w
        p.drawPath(path)
        p.end()

class UARTPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self); layout.setContentsMargins(20, 10, 20, 10)
        layout.addWidget(QLabel("📡 UART Protocol Visualizer"))
        layout.addWidget(QLabel("Enter a character to see its UART frame (8N1, LSB First):"))
        
        self.inp = QLineEdit("A"); self.inp.textChanged.connect(self.update_uart)
        layout.addWidget(self.inp)
        self.vis = UARTVisualWidget(); layout.addWidget(self.vis)
        
        self.info = QLabel(""); self.info.setStyleSheet("color: #58a6ff; font-family: Consolas; font-size: 14px; padding: 10px; background: #161b22; border-radius: 4px;")
        layout.addWidget(self.info); layout.addStretch(); self.update_uart()

    def update_uart(self):
        text = self.inp.text()
        if text:
            char = text[0]; val = ord(char)
            bits = ", ".join(str((val >> i) & 1) for i in range(8))
            self.info.setText(f"Char: '{char}' (0x{val:02X}) | Binary: {bits}")
            self.vis.set_char(char)

# ──────────────────────── OP-AMP CALCULATOR ────────────────────────
class OpAmpPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self); layout.setContentsMargins(20, 10, 20, 10)
        layout.addWidget(QLabel("📉 Op-Amp Circuit Solver"))
        
        self.type_combo = QComboBox(); self.type_combo.addItems(["Non-Inverting", "Inverting"])
        layout.addWidget(self.type_combo)
        
        g = QGroupBox("Parameters"); gl = QGridLayout(g)
        self.vin = QDoubleSpinBox(); self.vin.setRange(-100, 100); self.vin.setValue(1); self.vin.setSuffix(" V")
        self.rin = QDoubleSpinBox(); self.rin.setRange(1, 1e9); self.rin.setValue(10e3); self.rin.setSuffix(" Ω")
        self.rf = QDoubleSpinBox(); self.rf.setRange(1, 1e9); self.rf.setSetValue(100e3) if False else None; self.rf.setValue(100e3); self.rf.setSuffix(" Ω")
        
        gl.addWidget(QLabel("Vin:"), 0, 0); gl.addWidget(self.vin, 0, 1)
        gl.addWidget(QLabel("Rin/R1:"), 1, 0); gl.addWidget(self.rin, 1, 1)
        gl.addWidget(QLabel("Rf/R2:"), 2, 0); gl.addWidget(self.rf, 2, 1)
        layout.addWidget(g)
        
        self.res = QLabel(""); self.res.setStyleSheet("font-size: 16px; color: #58a6ff; font-weight: bold; padding: 10px; background: #161b22; border-radius: 4px;")
        layout.addWidget(self.res); layout.addStretch()
        
        self.type_combo.currentTextChanged.connect(self.calc)
        for w in [self.vin, self.rin, self.rf]: w.valueChanged.connect(self.calc)
        self.calc()

    def calc(self):
        vin, rin, rf = self.vin.value(), self.rin.value(), self.rf.value()
        if self.type_combo.currentText() == "Non-Inverting":
            gain = 1 + (rf / rin if rin > 0 else 0); vout = vin * gain
        else:
            gain = -(rf / rin if rin > 0 else 0); vout = vin * gain
        self.res.setText(f"Gain: {gain:.2f}x | Vout: {vout:.3f} V")

# ──────────────────────── FILTER CUTOFF CALCULATOR ────────────────────────
class FilterPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self); layout.setContentsMargins(20, 10, 20, 10)
        layout.addWidget(QLabel("🔊 Filter Cutoff Calculator"))
        
        self.type_combo = QComboBox(); self.type_combo.addItems(["RC Low-Pass", "RC High-Pass", "LC Low-Pass", "LC High-Pass"])
        layout.addWidget(self.type_combo)
        
        g = QGroupBox("Parameters"); gl = QGridLayout(g)
        self.r_spin = QDoubleSpinBox(); self.r_spin.setRange(1, 1e9); self.r_spin.setValue(10e3); self.r_spin.setSuffix(" Ω")
        self.c_spin = QDoubleSpinBox(); self.c_spin.setRange(1e-12, 1); self.c_spin.setValue(10e-9); self.c_spin.setDecimals(10); self.c_spin.setSuffix(" F")
        self.l_spin = QDoubleSpinBox(); self.l_spin.setRange(1e-9, 100); self.l_spin.setValue(1e-3); self.l_spin.setDecimals(6); self.l_spin.setSuffix(" H")
        
        gl.addWidget(QLabel("R:"), 0, 0); gl.addWidget(self.r_spin, 0, 1)
        gl.addWidget(QLabel("C:"), 1, 0); gl.addWidget(self.c_spin, 1, 1)
        gl.addWidget(QLabel("L:"), 2, 0); gl.addWidget(self.l_spin, 2, 1)
        layout.addWidget(g)
        
        self.res = QLabel(""); self.res.setStyleSheet("font-size: 16px; color: #58a6ff; font-weight: bold; padding: 10px; background: #161b22; border-radius: 4px;")
        layout.addWidget(self.res); layout.addStretch()
        
        self.type_combo.currentTextChanged.connect(self.toggle_lc)
        for w in [self.r_spin, self.c_spin, self.l_spin]: w.valueChanged.connect(self.calc)
        self.toggle_lc()

    def toggle_lc(self):
        is_lc = "LC" in self.type_combo.currentText()
        self.r_spin.setVisible(not is_lc); self.l_spin.setVisible(is_lc)
        self.calc()

    def calc(self):
        is_lc = "LC" in self.type_combo.currentText()
        if is_lc:
            l, c = self.l_spin.value(), self.c_spin.value()
            fc = 1 / (2 * math.pi * math.sqrt(l * c)) if l > 0 and c > 0 else 0
        else:
            r, c = self.r_spin.value(), self.c_spin.value()
            fc = 1 / (2 * math.pi * r * c) if r > 0 and c > 0 else 0
        self.res.setText(f"-3dB Cutoff Frequency: {format_value(fc, 'Hz')}")

# ──────────────────────── BJT BIASING CALCULATOR ────────────────────────
class BJTPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self); layout.setContentsMargins(20, 10, 20, 10)
        layout.addWidget(QLabel("🧲 BJT Voltage Divider Bias"))
        
        g = QGroupBox("Circuit Parameters"); gl = QGridLayout(g)
        self.vcc = QDoubleSpinBox(); self.vcc.setRange(0, 100); self.vcc.setValue(12); self.vcc.setSuffix(" V")
        self.r1 = QDoubleSpinBox(); self.r1.setRange(1, 1e7); self.r1.setValue(47e3); self.r1.setSuffix(" Ω")
        self.r2 = QDoubleSpinBox(); self.r2.setRange(1, 1e7); self.r2.setValue(10e3); self.r2.setSuffix(" Ω")
        self.rc = QDoubleSpinBox(); self.rc.setRange(1, 1e7); self.rc.setValue(1e3); self.rc.setSuffix(" Ω")
        self.re = QDoubleSpinBox(); self.re.setRange(1, 1e7); self.re.setValue(220); self.re.setSuffix(" Ω")
        self.beta = QDoubleSpinBox(); self.beta.setRange(1, 1000); self.beta.setValue(100)
        
        params = [("Vcc:", self.vcc), ("R1:", self.r1), ("R2:", self.r2), ("Rc:", self.rc), ("Re:", self.re), ("Beta:", self.beta)]
        for i, (lbl, spin) in enumerate(params): gl.addWidget(QLabel(lbl), i, 0); gl.addWidget(spin, i, 1)
        layout.addWidget(g)
        
        self.res = QLabel(""); self.res.setWordWrap(True); self.res.setStyleSheet("color: #58a6ff; font-size: 14px; font-weight: bold; padding: 10px; background: #161b22; border-radius: 4px;")
        layout.addWidget(self.res); layout.addStretch()
        for _, spin in params: spin.valueChanged.connect(self.calc)
        self.calc()

    def calc(self):
        vcc, r1, r2, rc, re, beta = self.vcc.value(), self.r1.value(), self.r2.value(), self.rc.value(), self.re.value(), self.beta.value()
        vb = vcc * r2 / (r1 + r2) if (r1+r2)>0 else 0
        ve = vb - 0.7 if vb > 0.7 else 0
        ie = ve / re if re > 0 else 0; ic = ie * beta / (beta + 1)
        vc = vcc - ic * rc; vce = vc - ve
        
        self.res.setText(f"Vb: {vb:.2f}V | Ve: {ve:.2f}V | Vc: {vc:.2f}V | Vce: {vce:.2f}V\nIc ≈ {format_value(ic, 'A')} | Q-Point: ({format_value(ic, 'A')}, {vce:.2f}V)")

# ──────────────────────── MAIN WINDOW ────────────────────────
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("⚡ MicroChip Academy — Advanced Electronics")
        self.setMinimumSize(1100, 750); self.resize(1200, 800)
        self.setStyleSheet(DARK_STYLESHEET)
        self.init_ui()

    def init_ui(self):
        central = QWidget(); self.setCentralWidget(central)
        main_layout = QHBoxLayout(central); main_layout.setContentsMargins(0,0,0,0); main_layout.setSpacing(0)

        sidebar = QFrame(); sidebar.setObjectName("sidebar"); sidebar.setFixedWidth(200)
        sidebar_layout = QVBoxLayout(sidebar); sidebar_layout.setContentsMargins(8, 15, 8, 15); sidebar_layout.setSpacing(2)
        
        logo = QLabel("⚡ MicroChip\n   Academy")
        logo.setStyleSheet("font-size: 16px; font-weight: bold; color: #58a6ff; padding: 6px; margin-bottom: 12px;")
        sidebar_layout.addWidget(logo)

        self.nav_buttons = []
        nav_items = [
            ("⏱️", "555 Oscilloscope"), ("⚡", "Voltage Divider"), ("💡", "LED Calculator"),
            ("🔋", "Capacitor Code"), ("🔗", "Series/Parallel"), ("📏", "Unit Converter"),
            ("💾", "ATmega Simulator"), ("📡", "UART Visualizer"), ("📉", "Op-Amp Solver"),
            ("🔊", "Filter Cutoff"), ("🧲", "BJT Biasing")
        ]
        for icon, name in nav_items:
            btn = QPushButton(f"  {icon}  {name}"); btn.setObjectName("nav_btn"); btn.setCheckable(True); btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda checked, n=name: self.navigate_to(n))
            sidebar_layout.addWidget(btn); self.nav_buttons.append((btn, name))
        
        sidebar_layout.addStretch()
        main_layout.addWidget(sidebar)

        self.stack = QStackedWidget(); self.pages = {}
        pages_to_create = [
            ("555 Oscilloscope", Timer555Page), ("Voltage Divider", VoltageDividerPage),
            ("LED Calculator", LEDResistorPage), ("Capacitor Code", CapacitorCodePage),
            ("Series/Parallel", SeriesParallelPage), ("Unit Converter", UnitConverterPage),
            ("ATmega Simulator", ATmegaRegisterPage), ("UART Visualizer", UARTPage),
            ("Op-Amp Solver", OpAmpPage), ("Filter Cutoff", FilterPage), ("BJT Biasing", BJTPage)
        ]
        
        for name, cls in pages_to_create:
            page = cls()
            scroll = QScrollArea(); scroll.setWidgetResizable(True); scroll.setWidget(page)
            self.pages[name] = scroll; self.stack.addWidget(scroll)
        
        main_layout.addWidget(self.stack, 1)
        self.navigate_to("555 Oscilloscope")

    def navigate_to(self, page_name):
        if page_name in self.pages:
            self.stack.setCurrentWidget(self.pages[page_name])
            for btn, name in self.nav_buttons: btn.setChecked(name == page_name)

def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MainWindow(); window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()