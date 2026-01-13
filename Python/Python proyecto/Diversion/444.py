import sys
from PyQt5.QtWidgets import QApplication, QDialog, QLabel, QPushButton, QVBoxLayout, QMessageBox
from PyQt5.QtCore import Qt

class VersoDialog(QDialog):
    def __init__(self, versos, index=0, parent=None):
        super().__init__(parent)  # Usamos 'parent' para que la nueva ventana se apile encima de la anterior
        self.setWindowTitle("YANBLOCK")
        self.setFixedSize(800, 400)  # 📏 Tamaño de la ventana
        self.index = index
        self.versos = versos

        layout = QVBoxLayout()

        # Texto centrado con letra grande
        self.label = QLabel(self.versos[self.index], self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("font-size: 18pt;")
        layout.addWidget(self.label)

        # Botón OK más grande
        self.ok_button = QPushButton("OK", self)
        self.ok_button.setMinimumSize(120, 45)
        self.ok_button.setStyleSheet("font-size: 12pt;")  
        self.ok_button.clicked.connect(self.mostrar_siguiente)
        layout.addWidget(self.ok_button, alignment=Qt.AlignCenter)

        self.setLayout(layout)

    def mostrar_siguiente(self):
        # Crear la nueva ventana, pero no cerramos la actual
        if self.index + 1 < len(self.versos):
            self.index += 1
            self.label.setText(self.versos[self.index])  # Cambia el texto
            # Crear y mostrar la nueva ventana encima de la anterior
            new_verso_dialog = VersoDialog(self.versos, self.index, parent=self)
            new_verso_dialog.show()  # Muestra la nueva ventana encima de la anterior
        else:
            self.close()  # Cierra la ventana cuando llega al final


class Ventana:
    def __init__(self):
        self.index = 0
        self.letra = [
            "Aunque no estés aquí y estés allá",
            "Mami, tú estás clara que siempre te vo'a clavar",
            "Que esto nunca va a acabar, si yo siempre vo'a acabarte",
            "Tú siempre vas a tenerme y yo siempre vo'a tenerte",
            "Tú siempre vas a llamar y yo voy a responderte",
            "Tú siempre vas a llamar y yo voy a responderte",
            "Me enchulé de tus defectos imperfectamente perfectos",
            "Le contesto en to momento, monumento es ese cuerpo,\nma",
            "¿Cuándo vamo a vernos?, que el infierno está viniendo",
            "Y me quiero morir viniéndome, metiéndote, yeah"
        ]

    def mostrar(self):
        dlg = VersoDialog(self.letra)
        dlg.exec_()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Pregunta inicial
    reply = QMessageBox.question(
        None,
        "444",
        "¿Quieres escuchar 444?",
        QMessageBox.Yes | QMessageBox.No,
        QMessageBox.Yes
    )

    if reply == QMessageBox.Yes:
        ventana = Ventana()
        ventana.mostrar()
    else:
        sys.exit(0)
