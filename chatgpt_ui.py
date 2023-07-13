import sys
import openai
import pickle
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from qt_material import apply_stylesheet

class ChatGptApp(QWidget):
    def __init__(self):
        super().__init__()

        self.buttonstate_file="button_state.pkl"
        self.buttondata_file="button_data.pkl"

        self.initUI()


    def initUI(self):
        self.file_label = QTextEdit("학습 결과")
        self.file_label.setFrameShape(QLabel.Box)
        self.file_label.setFixedSize(700, 300)
        self.file_label.setStyleSheet("font-size: 13pt;")

        self.verify_button=QPushButton("검증", self)

        self.verify_label = QTextEdit("검증 결과를 표시할 라벨")
        self.verify_label.setFrameShape(QLabel.Box)
        self.verify_label.setFixedSize(700, 300)
        self.verify_label.setStyleSheet("font-size: 13pt;")

        '''self.file_input = QPlainTextEdit()
        self.file_input.setFixedSize(700, 100)
        self.file_input.setPlainText("내용을 입력하세요...")
        self.file_input.textChanged.connect(self.clean_TextChanged)'''

        load_button = QPushButton("파일 불러오기", self)
        load_button.clicked.connect(self.loadFile)

        '''verify_button = QPushButton("입력", self)
        verify_button.clicked.connect(self.Script)'''

        self.addBtn_hbox=QVBoxLayout()
        self.addButton = QPushButton("+", self)
        self.addButton.clicked.connect(self.addButtonClicked)   

        # 하단 '파일 불러오기', '검증' 버튼 레이아웃 설정
        vbox_left_hbox=QHBoxLayout()
        vbox_left_hbox.addWidget(load_button) # 파일 불러오기
        vbox_left_hbox.addWidget(self.verify_button) # 검증

        vbox_left = QVBoxLayout()
        vbox_left.addWidget(self.file_label)
        #vbox_left.addWidget(self.file_input)
        vbox_left.addWidget(self.verify_label)
        vbox_left.addLayout(vbox_left_hbox)


        self.vbox_right = QVBoxLayout()
        #self.vbox_right.addWidget(self.addButton)
        self.addBtn_hbox.addWidget(self.addButton)
        self.vbox_right.addLayout(self.addBtn_hbox)
        self.vbox_right.addStretch()

        hbox = QHBoxLayout()
        hbox.addLayout(vbox_left)
        hbox.addLayout(self.vbox_right)

        self.setLayout(hbox)

        self.setWindowTitle("Chat Gpt 앱")
        self.setGeometry(100, 100, 900, 800)  # 윈도우 창 크기 설정
        self.show()

        self.buttonCounter = 0

        # 추가된 버튼들을 저장할 리스트
        self.buttons = []

        # 학습 내용 저장할 리스트
        # self.texts = []

    def clean_TextChanged(self):
        if self.file_input.toPlainText() == "파일 내용을 입력하세요.":
            self.file_input.clear()
    
    def addButtonClicked(self):
        addBtn_dialog=QDialog(self)
        #addBtn_dialog.setStyleSheet("width: 250px;")
        text, ok = QInputDialog.getText(addBtn_dialog, "학습 추가", "<html><font size='5'>학습 할 이름을 입력하세요:</font></html>")
        if ok and text:
            self.buttonCounter += 1
            button = QPushButton(text, self)
            button.setIcon(QIcon("img/icons8-chatgpt-24.png"))
            button.clicked.connect(lambda _, text="default" : self.showInputDialog(text))
            #self.vbox_right.addWidget(button)
            self.addBtn_hbox.addWidget(button)
            self.buttons.append(button)

    def showInputDialog(self,text):
        button = self.sender()
        text_input = QTextEdit(self)
        text_input.setFixedSize(400, 500)

        if button.property("study_text"):
            text_input.setPlainText(button.property("study_text"))

        text_input.setStyleSheet("font-size: 13pt;")

        dialog = QMessageBox()
        dialog.setWindowTitle("사전 학습 데이터 입력")

	# 아이콘 파일 경로
        icon_path = './img/icons8-chatgpt-48.png'

        # QIcon으로 아이콘 로드
        custom_icon = QIcon(icon_path)

        #dialog.setIcon(QMessageBox.Question)
        dialog.setIconPixmap(custom_icon.pixmap(128, 128))
        dialog.addButton("저장", QMessageBox.AcceptRole)
        dialog.addButton("취소", QMessageBox.RejectRole)
        BtnDelete=dialog.addButton("삭제", QMessageBox.ActionRole)
        EduBtn=dialog.addButton("학습", QMessageBox.ActionRole)
        dialog.layout().addWidget(text_input)

        if dialog.exec_() == QMessageBox.AcceptRole:
                button = self.sender()
                text = text_input.toPlainText()
                button.setProperty("study_text", text)

	    # 삭제 버튼 누르면 삭제
        if dialog.clickedButton()==BtnDelete:
            self.buttons.remove(button)
            button.deleteLater()
        
        # 학습 버튼 누를 시
        if dialog.clickedButton()==EduBtn:
            print(text_input.toPlainText())
            self.Script(text_input.toPlainText())
            EduBtn.clicked.connect(self.loading)
            

    def loadFile(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "파일 불러오기")
        if file_path:
            with open(file_path, "r") as file:
                file_content = file.read()
                self.file_label.setText(file_content)

    def Script(self,text):
        msgs = []
        temp_msg = text
        msg = {"role": "user", "content": temp_msg}
        msgs.append(msg)

        print(msgs)

        loading_label = QLabel(self)
        loading_label.setWordWrap(True)

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

    def saveButtonState(self):
        button_state = self.addButton.isChecked()
        with open("button_state.pkl", "wb") as f:
            pickle.dump(button_state, f)

        # 추가된 버튼들의 이름과 텍스트를 저장
        button_data = []
        for button in self.buttons:
            text = button.property("study_text")
            if text:
                button_data.append((button.text(), text))

        with open("button_data.pkl", "wb") as f:
            pickle.dump(button_data, f)

    def loadButtonState(self):
        try:
            with open("button_state.pkl", "rb") as f:
                button_state = pickle.load(f)
                self.addButton.setChecked(button_state)
        except FileNotFoundError:
            pass

        try:
            with open("button_data.pkl", "rb") as f:
                button_data = pickle.load(f)
                for name, study_text in button_data:
                    button = QPushButton(name, self)
                    button.setProperty("study_text", study_text)
                    button.clicked.connect(lambda _, text=study_text: self.showInputDialog(text))
                    self.addBtn_hbox.addWidget(button)
                    self.buttons.append(button)
                #self.vbox_right.addStretch()
        except FileNotFoundError:
            pass
    
    # 학습 버튼 클릭 시 loading 이벤트
    def loading(self):
        # 로딩중일때 다시 클릭하는 경우
        try: 
            self.loading
            self.loading.deleteLater()
            
        # 처음 클릭하는 경우    
        except:
            self.loading = loading(self)
    
    def closeEvent(self, event):
        self.saveButtonState()
        event.accept()

# loading gif
class loading(QWidget):
    
    def __init__(self,parent):
        super(loading,self).__init__(parent)    
        self.setupUi(self) 
        self.center()
        self.show()
        
        # 동적 이미지 추가
        self.movie = QMovie('web-5811_128.gif', QByteArray(), self)
        self.movie.setCacheMode(QMovie.CacheAll)
        # QLabel에 동적 이미지 삽입
        self.label.setMovie(self.movie)
        self.movie.start()
        
        # 윈도우 해더 숨기기
        self.setWindowFlags(Qt.FramelessWindowHint)   
    
    # 위젯 정중앙 위치
    def center(self):
        size=self.size()
        ph = self.parent().geometry().height()
        pw = self.parent().geometry().width()
        self.move(int(pw/2 - size.width()/2), int(ph/2 - size.height()/2))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ChatGptApp()
    window.loadButtonState()  
    apply_stylesheet(app, theme='dark_lightgreen.xml')
    window.show()
    sys.exit(app.exec_())