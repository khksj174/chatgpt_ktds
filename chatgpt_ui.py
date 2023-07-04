import sys
import openai
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QFileDialog, QVBoxLayout, QHBoxLayout, QInputDialog, QProgressDialog, QPlainTextEdit, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QMovie

class ChatGptApp(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.file_label = QLabel("")
        self.file_label.setFrameShape(QLabel.Box)
        self.file_label.setFixedSize(700, 300)

        self.verify_label = QLabel("검증 결과를 표시할 라벨")
        self.verify_label.setFrameShape(QLabel.Box)
        self.verify_label.setFixedSize(700, 300)

        self.file_input = QPlainTextEdit()
        self.file_input.setFixedSize(700, 100)
        self.file_input.setPlainText("내용을 입력하세요...")
        self.file_input.textChanged.connect(self.clean_TextChanged)

        load_button = QPushButton("파일 불러오기", self)
        load_button.clicked.connect(self.loadFile)

        verify_button = QPushButton("입력", self)
        verify_button.clicked.connect(self.Script)

        self.addButton = QPushButton("+", self)
        self.addButton.clicked.connect(self.addButtonClicked)

        vbox_left = QVBoxLayout()
        vbox_left.addWidget(load_button)
        vbox_left.addWidget(self.file_label)
        vbox_left.addWidget(self.file_input)
        vbox_left.addWidget(verify_button)
        vbox_left.addWidget(self.verify_label)

        self.vbox_right = QVBoxLayout()
        self.vbox_right.addStretch(1)
        self.vbox_right.addWidget(self.addButton)

        hbox = QHBoxLayout()
        hbox.addLayout(vbox_left)
        hbox.addLayout(self.vbox_right)

        self.setLayout(hbox)

        self.setWindowTitle("Chat Gpt 앱")
        self.setGeometry(100, 100, 900, 800)  # 윈도우 창 크기 설정
        self.show()

        self.buttonCounter = 0

    def clean_TextChanged(self):
        if self.file_input.toPlainText() == "파일 내용을 입력하세요.":
            self.file_input.clear()

    def addButtonClicked(self):
        text, ok = QInputDialog.getText(self, "학습 추가", "학습 할 이름을 입력하세요:")
        if ok and text:
            self.buttonCounter += 1
            button = QPushButton(text, self)
            button.setIcon(QIcon("img/icon.png"))
            button.clicked.connect(self.showInputDialog)
            self.vbox_right.addWidget(button) 

    def showInputDialog(self):
        button = self.sender()
        text_input = QPlainTextEdit(self)
        text_input.setFixedSize(400, 500)
        text_input.setPlainText("학습 시킬 내용을 입력하세요.")

        dialog = QMessageBox()
        dialog.setWindowTitle("사전 학습 데이터 입력")
        dialog.setText("Chat-gpt에게 학습 시킬 내용을 입력하세요:")
        dialog.setIcon(QMessageBox.Question)
        dialog.addButton("확인", QMessageBox.AcceptRole)
        dialog.addButton("취소", QMessageBox.RejectRole)
        dialog.layout().addWidget(text_input)
    

        if dialog.exec_() == QMessageBox.Accepted:
            print(text_input)
            lines = text_input.toPlainText().split('\n')

            messages = []
            for line in lines:
                message = {"role": "user", "content": line}
                messages.append(message)

            response = self.response_gpt(messages)

            self.file_label.setText(response)

        #QMessageBox.information(self, "입력 결과", f"입력된 텍스트: {text}\n버튼: {button.text()}")

    def buttonClicked(self):
        button = self.sender()
        index = self.buttonLayout.indexOf(button)
        self.verify_label.setText(f"Button {index + 1} 클릭됨.")

    def loadFile(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "파일 불러오기")
        if file_path:
            with open(file_path, "r") as file:
                file_content = file.read()
                self.file_label.setText(file_content)

    def Script(self):
        msgs = []
        text = self.file_input.toPlainText()

        msg = {"role": "user", "content": text}
        msgs.append(msg)

        loading_label = QLabel(self)
        loading_movie = QMovie("img/1494.gif")
        loading_label.setMovie(loading_movie)
        
        layout = QVBoxLayout()
        layout.addWidget(loading_label)
        layout.setAlignment(Qt.AlignCenter)
        self.setLayout(layout)

        loading_label.show()
        loading_movie.start()

        response = self.response_gpt(msgs)
        print(response)

        loading_movie.stop()
        loading_label.hide()
        
        self.file_label.setText(response)

    def response_gpt(self,msg):
        openai.api_key = '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'
        response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=msg
        )
    
        return response['choices'][0]['message']['content']

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ChatGptApp()
    sys.exit(app.exec_())
