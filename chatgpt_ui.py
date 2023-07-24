import sys
import openai
import pickle
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from qt_material import apply_stylesheet

'''import nltk
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')'''
from nltk import word_tokenize, pos_tag

class ChatGptApp(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()
        
    def initUI(self):
        self.file_label = QTextEdit("학습 결과")
        self.file_label.setFrameShape(QLabel.Box)
        self.file_label.setFixedSize(700, 300)
        #self.file_label.setStyleSheet("font-size: 10pt;")
        self.file_label.setReadOnly(True)

        self.verify_button=QPushButton("검증", self)
        self.verify_button.clicked.connect(self.find_difference)

        self.verify_label = QTextEdit("검증 결과")
        self.verify_label.setFrameShape(QLabel.Box)
        self.verify_label.setFixedSize(700, 300)
        #self.verify_label.setStyleSheet("font-size: 10pt;")
        self.verify_label.setReadOnly(True)
        #self.verify_label.setStyleSheet("color: red; font-size: 16px; font-family: Arial;")

        self.filename_label=QLabel("불러온 파일이 없습니다.")
        #self.filename_label.setStyleSheet("font-size: 8pt;")
        self.filename_label.setFixedSize(700, 50)

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

        # loading gif
        '''self.loading_label = QLabel(self)
        #self.loading_label.setWordWrap(True)
        self.loading_movie = QMovie("loading.gif") 
        self.loading_label.setMovie(self.loading_movie)

        self.loading_label.setFixedSize(50, 50)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.loading_label)
        self.layout.setAlignment(Qt.AlignCenter)
        
        # QLabel의 크기가 변경될 때마다 QMovie의 크기 조정
        self.loading_label.resizeEvent = self.loading_movie.setScaledSize(self.loading_label.size())
        self.loading_movie.start()'''

        # 하단 '파일 불러오기', '검증' 버튼 레이아웃 설정
        vbox_left_hbox=QHBoxLayout()
        vbox_left_hbox.addWidget(load_button) # 파일 불러오기
        vbox_left_hbox.addWidget(self.verify_button) # 검증

        self.vbox_left = QVBoxLayout()
        self.vbox_left.addWidget(self.file_label)
        #vbox_left.addWidget(self.file_input)
        #self.vbox_left.addLayout(self.layout) # 로딩 gif 표시
        self.vbox_left.addWidget(self.verify_label)
        self.vbox_left.addWidget(self.filename_label) # 파일명 표시
        self.vbox_left.addLayout(vbox_left_hbox)


        self.vbox_right = QVBoxLayout()
        #self.vbox_right.addWidget(self.addButton)
        self.addBtn_hbox.addWidget(self.addButton)
        self.vbox_right.addLayout(self.addBtn_hbox)
        self.vbox_right.addStretch()

        hbox = QHBoxLayout()
        hbox.addLayout(self.vbox_left)
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
        text, ok = QInputDialog.getText(addBtn_dialog, "학습 추가", "<html><font size='4'>학습 할 이름을 입력하세요:</font></html>")
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
        #text_input.setFixedSize(400, 500)

        if button.property("study_text"): 
            text_input.setPlainText(button.property("study_text"))

        #text_input.setStyleSheet("font-size: 13pt;")

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

    def loadFile(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "파일 불러오기")
        if file_path:
            file_name=file_path.split("/")[-1]# 파일 경로에서 파일명만 추출
            self.filename_label.setText('파일명: ' + file_name)
            with open(file_path, "r", encoding='UTF-8') as file:
                #file_content = file.read()
                #self.file_label.setText(file_content)
                sql_script=file.read()
                self.verify_label.setText(', '.join(self.verify_result(sql_script)))

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
        
        #self.file_label.setText(self.response)
        self.file_label.setText(', '.join(self.file_result(response)))
        #self.verify_label.setText('\n'.join(self.result(response)))

    def response_gpt(self,msg):
        openai.api_key = '###################'
        response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=msg
        )
    
        return response['choices'][0]['message']['content']
    
    # 학습 데이터에서 날짜 추출
    def file_result(self, txt):
        # 토큰화 후 품사 태깅
        tokenized_sentence = pos_tag(word_tokenize(txt))
        #print(tokenized_sentence)

        dates=[]
        for words in tokenized_sentence:
            #if words[1]=='CD' and words[0].isdecimal() and len(words[0])==8:
            #    dates.append(words[0])
            if words[1]=='CD' and len(words[0])>=8:
                if words[0][:8].isdecimal():
                    dates.append(words[0][:8])
        dates=list(set(dates))
        dates.sort()

        return dates
    
    # 검증 데이터에서 날짜 추출
    def verify_result(self, txt):
        # 토큰화 후 품사 태깅
        sql_tokenized_sentence = pos_tag(word_tokenize(txt))
        #print(sql_tokenized_sentence)

        sql_dates=[]
        for words in sql_tokenized_sentence:
            if words[1]=='POS' and len(words[0])>=8:
                if words[0][1:9].isdecimal():
                    sql_dates.append(words[0][1:9])
        sql_dates=list(set(sql_dates))
        sql_dates.sort()
        sql_dates_result=[sql_dates[i] for i in [0, 2, 4]]

        return sql_dates_result
    
    # 학습 데이터 vs 검증 데이터 비교
    def find_difference(self):
        text1 = self.file_label.toPlainText()
        text2 = self.verify_label.toPlainText()

        # 텍스트 비교하여 다른 부분 찾기
        # 두 텍스트를 문자 단위로 비교하여 다른 부분의 인덱스 찾기
        diff_indices = []
        min_length = min(len(text1), len(text2))
        start_idx=None

        for i in range(min_length):
            if text1[i] != text2[i]:
                if start_idx is None:
                    start_idx = i
                diff_indices.append(i)
            elif start_idx is not None:
                self.apply_red_format(start_idx, i)
                start_idx = None

        # 남은 글자들 처리
        if start_idx is not None:
            self.apply_red_format(start_idx, len(text1) if len(text1) > len(text2) else len(text2))
    
    # 다른 부분 빨간 폰트로 표시
    def apply_red_format(self, start, end):
        red_format = QTextCharFormat()
        red_format.setForeground(QColor("red"))

        # QTextEdit2에서 다른 부분에 빨간 폰트 적용
        cursor = self.verify_label.textCursor()
        cursor.setPosition(start, QTextCursor.MoveAnchor)
        cursor.setPosition(end, QTextCursor.KeepAnchor)
        cursor.setCharFormat(red_format)

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
    
    def closeEvent(self, event):
        self.saveButtonState()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ChatGptApp()
    window.loadButtonState()
    #apply_stylesheet(app, theme='light_blue.xml', invert_secondary=True)
    
    style_sheet = """
    /* 전체 버튼 스타일을 설정합니다 */
     /* QLabel 스타일을 설정합니다 */
    /* 전체 버튼 스타일을 설정합니다 */
    QPushButton {
        background-color: rgb(58, 134, 255); /* 배경색 */
        color: white; /* 텍스트 색상 */
        padding: 10px 2px; /* 안쪽 여백 */
        font-family: "맑은 고딕", sans-serif; /* 폰트 설정 */
        font-size: 18px; /* 폰트 크기 */
	    border-radius: 6px;
    }
    QLabel {
        background-color: #F0F0F0; /* 배경색 */
        border: 2px solid rgb(58, 134, 255); /* 테두리 */
        color: rgb(58, 134, 255);; /* 텍스트 색상 */
        font-family: "맑은 고딕", sans-serif; /* 폰트 설정 */
        font-size: 20px; /* 폰트 크기 */
        border-radius: 6px;
    }
    QTextEdit {
        min-width:400px;
        min-height:300px;
        background-color: #F0F0F0; /* 배경색 */
        border: 2px solid rgb(58, 134, 255); /* 테두리 */
        color: rgb(58, 134, 255);; /* 텍스트 색상 */
        font-family: "맑은 고딕", sans-serif; /* 폰트 설정 */
        font-size: 20px; /* 폰트 크기 */
        border-radius: 6px;
    }
    """

    # QApplication에 스타일시트 설정
    app.setStyleSheet(style_sheet)

    window.show()
    sys.exit(app.exec_())