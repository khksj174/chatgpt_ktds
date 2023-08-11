import sys
import openai
import pickle
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from pathlib import Path
from nltk import word_tokenize, pos_tag

class ChatGptApp(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()
        
    def initUI(self):

        self.file_label = QTextEdit("학습 결과")
        self.file_label.setFrameShape(QLabel.Box)
        self.file_label.setFixedSize(500, 300)
        self.file_label.setReadOnly(True)

        self.verify_button=QPushButton("검증", self)
        self.verify_button.clicked.connect(self.find_difference)

        self.verify_label = QTextEdit("검증 결과")
        self.verify_label.setFrameShape(QLabel.Box)
        self.verify_label.setFixedSize(500, 300)
        self.verify_label.setReadOnly(True)

        self.filename_label=QLabel("불러온 파일이 없습니다.")
        self.filename_label.setFixedSize(500, 50)

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

        self.vbox_left = QVBoxLayout()
        self.vbox_left.addWidget(self.file_label)
        #vbox_left.addWidget(self.file_input)
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

        self.setWindowTitle("Chat-Gpt 앱")
        self.setGeometry(100, 100, 720, 560)  # 윈도우 창 크기 설정
        self.show()

        self.buttonCounter = 0

        # 추가된 버튼들을 저장할 리스트
        self.buttons = []

    '''def clean_TextChanged(self):
        if self.file_input.toPlainText() == "파일 내용을 입력하세요.":
            self.file_input.clear()'''
    
    def addButtonClicked(self):
        addBtn_dialog=QDialog(self)

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

        if button.property("study_text"): 
            text_input.setPlainText(button.property("study_text"))

        dialog = QMessageBox()
        dialog.setWindowTitle(button.text())

	    # 아이콘 파일 경로
        #icon_path = './img/icons8-chatgpt-48.png'
        icon_path = './ui/img/gpt_icon.jpg'
        # QIcon으로 아이콘 로드
        custom_icon = QIcon(icon_path)
        dialog.setIcon(QMessageBox.Question)
        dialog.setIconPixmap(custom_icon.pixmap(64, 64))

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
            self.file_name=file_path.split("/")[-1]# 파일 경로에서 파일명만 추출
            self.filename_label.setText('파일명: ' + self.file_name)
            with open(file_path, "r", encoding='cp949') as file:
                file_content=file.read()
                self.verify_label.setText(file_content)
                self.verify_label_dates=', '.join(self.verify_result(file_content))

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
        
        self.file_label_dates=', '.join(self.file_result(response))
        self.file_label.setText(response)

    def response_gpt(self,msg):
        openai.api_key = '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'
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

        if "카드" in self.file_name:
            sql_dates_result=[sql_dates[i] for i in [0, 2, 4]]
        else:
            sql_dates_result=sql_dates

        return sql_dates_result
    
    # 학습 데이터 vs 검증 데이터 비교
    def find_difference(self):
        apply_red_cnt=0
        # 텍스트 비교하여 다른 부분 찾기
        text1=self.file_label_dates
        self.verify_label.setText(self.verify_label_dates)
        text2 = self.verify_label.toPlainText()
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
                apply_red_cnt+=1
                start_idx = None

        # 남은 글자들 처리
        if start_idx is not None:
            self.apply_red_format(start_idx, len(text1) if len(text1) > len(text2) else len(text2))
            apply_red_cnt+=1

        # 검증 결과 정상/비정상 판단    
        self.verify_label.moveCursor(self.verify_label.textCursor().Start) # 커서를 끝으로 이동
        self.verify_label.insertPlainText("chat-GPT 검증 결과: ")
        # 폰트 설정
        #wrong_font = QFont("맑은 고딕", 12, QFont.Bold)
        wrong_font_color = QColor(255, 0, 0)  # 빨간
        # 현재 커서 위치 가져오기
        cursor = self.verify_label.textCursor()
        position = cursor.position()
        if apply_red_cnt>0:
            # 텍스트 추가
            verify_wrong="스크립트 날짜 오류!!\n\n"
            self.verify_label.insertPlainText(verify_wrong)
            # 텍스트에 적용할 폰트 색상 및 폰트 설정
            char_format = QTextCharFormat()
            #char_format.setFont(wrong_font)
            char_format.setForeground(wrong_font_color)
            # 텍스트에 적용
            cursor.setPosition(position)
            cursor.setPosition(position + len(verify_wrong), QTextCursor.KeepAnchor)
            cursor.mergeCharFormat(char_format)

            self.verify_label.insertPlainText(f"학습 결과: {self.file_label_dates}\n정상 배치 날짜: ")
        else:
            self.verify_label.insertPlainText("정상\n\n"+ "배치 날짜: ") 

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
                for self.name, study_text in button_data:
                    button = QPushButton(self.name, self)
                    button.setProperty("study_text", study_text)
                    button.clicked.connect(lambda _, text=study_text: self.showInputDialog(text))
                    self.addBtn_hbox.addWidget(button)
                    self.buttons.append(button)
        except FileNotFoundError:
            pass
    
    def closeEvent(self, event):
        self.saveButtonState()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # 폰트 추가
    font_path = './ui/font/SUIT-Variable.ttf'
    font_id = QFontDatabase.addApplicationFont(font_path)
    app.setFont(QFont("SUIT Variable", 10))

    window = ChatGptApp()
    window.loadButtonState()

    # QApplication에 스타일시트 설정
    app.setStyleSheet(Path('./ui/Aqua.qss').read_text(encoding='utf-8'))
    
    window.show()
    sys.exit(app.exec_())