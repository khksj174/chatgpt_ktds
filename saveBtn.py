import sys
import pickle
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QLabel, QPushButton, QFileDialog, QVBoxLayout, QHBoxLayout, QInputDialog, QProgressDialog, QPlainTextEdit, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QMovie

class MainWindow(QMainWindow):

    buttonCounter = 0

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Push Button Example")
        self.button = QPushButton("Push Me", self)
        self.button.clicked.connect(self.buttonClicked)

        # 버튼을 추가할 QVBoxLayout 생성
        self.vbox_right = QVBoxLayout()

        # 메인 윈도우의 central widget 생성
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        # central widget의 레이아웃 생성
        layout = QHBoxLayout(central_widget)
        layout.addWidget(self.button)

        # 버튼을 추가할 QVBoxLayout을 메인 레이아웃에 추가
        layout.addLayout(self.vbox_right)

        # 추가된 버튼들을 저장할 리스트
        self.buttons = []


    def buttonClicked(self):
        text, ok = QInputDialog.getText(self, "학습 추가", "학습 할 내용을 입력하세요:")
        if ok and text:
            self.buttonCounter += 1
            button = QPushButton(text, self)
            button.setProperty("text", text)
            button.clicked.connect(lambda _, text=text: self.showText(text))
            self.vbox_right.addWidget(button)
            self.buttons.append(button)

    def saveButtonState(self):
        button_state = self.button.isChecked()
        with open("button_state.pkl", "wb") as f:
            pickle.dump(button_state, f)

        # 추가된 버튼들의 이름과 텍스트를 저장
        button_data = []
        for button in self.buttons:
            text = button.property("text")
            if text:
                button_data.append((button.text(), text))

        with open("button_data.pkl", "wb") as f:
            pickle.dump(button_data, f)

    def loadButtonState(self):
        try:
            with open("button_state.pkl", "rb") as f:
                button_state = pickle.load(f)
                self.button.setChecked(button_state)
        except FileNotFoundError:
            pass

        try:
            with open("button_data.pkl", "rb") as f:
                button_data = pickle.load(f)
                for name, text in button_data:
                    button = QPushButton(name, self)
                    button.setProperty("text", text)
                    button.clicked.connect(lambda _, text=text: self.showText(text))
                    self.vbox_right.addWidget(button)
                    self.buttons.append(button)
        except FileNotFoundError:
            pass

    def showText(self, text):
        QMessageBox.information(self, "입력된 텍스트", f"입력된 텍스트:\n{text}")

    def closeEvent(self, event):
        self.saveButtonState()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.loadButtonState()
    mainWindow.show()
    sys.exit(app.exec())
