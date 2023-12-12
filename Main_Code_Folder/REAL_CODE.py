import cv2  # opencv 
import tensorflow as tf
import sys
import os
import glob
import serial
import time

from ultralytics import YOLO
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

# 이미지 경로 설정 변수
main_window_background = 'IMAGE/MAIN_WINDOW_BACKGROUND_IMAGE.jpg'
menu_window_background_image = 'IMAGE/MENU_WINDOW_BACKGROUND_IMAGE.png'
button_background_image = 'IMAGE/button_image.png'

# 사과 이미지가 저장될 폴더
A_CLASS_image = 'APPLE_IMAGE_FOLDER/A_CLASS/'
B_CLASS_image = 'APPLE_IMAGE_FOLDER/B_CLASS/'
C_CLASS_image = 'APPLE_IMAGE_FOLDER/C_CLASS/'
D_CLASS_image = 'APPLE_IMAGE_FOLDER/D_CLASS/'
E_CLASS_image = 'APPLE_IMAGE_FOLDER/E_CLASS/'
tan_image = 'APPLE_IMAGE_FOLDER/TAN_APPLE/'
gup_image = 'APPLE_IMAGE_FOLDER/GUP_APPLE/'
black_spot_image = 'APPLE_IMAGE_FOLDER/BLACK_SPOT_APPLE/'

# 웹캠 화면 출력 창에 뜨는 직선 관련된 변수
line_position = 50

# 클래스 이름, 순서 'BLACK_SPOT', 'GOOD_APPLE', 'GUP_APPLE', 'SOSO_APPLE', 'TAN_APPLE'                                                               
class MAIN_WINDOW(QWidget):
    
    THRESHOLD_VALUE = 200
    TIMER_INTERVAL = 100
    #global set_count_1, set_count_2, set_count_3, set_count_4, set_count_5
    # 초기화
    def __init__(self): 
        super().__init__()
        self.model = YOLO('S_model.pt')
        self.arduino = serial.Serial("COM5", 9600)
        self.init_ui()
        
        self.webcam = cv2.VideoCapture(1) # 0번은 노트북 캠, 1번은 오캠
        
        # 웹캠 화면 출력 창 정보들, 선으로 감지하는 관련 코드
        global width_for_line, height_for_line, x_line, pt1, pt2, counting_buffer
        
        width_for_line = self.webcam.get(cv2.CAP_PROP_FRAME_WIDTH)
        height_for_line = self.webcam.get(cv2.CAP_PROP_FRAME_HEIGHT)
        
        x_line = line_position * width_for_line / 100
        pt1 = (int(x_line), 0)
        pt2 = (int(x_line), int(height_for_line))
        counting_buffer = {}
        
        # 프레임 업데이트
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(50) 

    def init_ui(self):
        # 창 사이즈 및 제목 설정
        self.setWindowTitle('MONITORING SYSTEM')
        self.setFixedSize(1440, 800)
        
        self.image_list_1 = set()
        self.image_list_2 = set()
        self.image_list_3 = set()
        self.image_list_4 = set()
        self.image_list_5 = set()
        self.image_list_6 = set()
        self.image_list_7 = set()
        self.image_list_8 = set()
        
        # 카메라 판===============================================================================================================================
        self.rect_widget = QWidget(self)
        self.rect_widget.setGeometry(QRect(345, 145, 750, 510))
        self.rect_widget.setStyleSheet(f"background-image: url({menu_window_background_image}); border-radius: 15px;")
        
        # 메인 창 배경을 이미지로 지정
        palette = QPalette()
        palette.setBrush(QPalette.Background,QBrush(QPixmap("image/MAIN_WINDOW_BACKGROUND_IMAGE.jpg")))
        self.setPalette(palette)

        # 메인 창에 웹캠 화면 출력창을 띄운다
        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignCenter)
        layout = QVBoxLayout(self)
        layout.addWidget(self.image_label)
        self.setLayout(layout)
        
        # 시간 나타내는 코드 부분 
        self.timeLabel = QLabel(self)
        self.timeLabel.setGeometry(QRect(520, 10, 500, 150))
        self.timeLabel.setStyleSheet("color: white; font-size: 100px;")
                
        time_layout = QVBoxLayout()
        time_layout.addWidget(self.timeLabel)
        self.setLayout(time_layout)
        
        timer = QTimer(self)
        timer.timeout.connect(self.updateTime)
        timer.start(1000)
        self.updateTime()
        
        # 메뉴 버튼 
        self.menu_btn = QPushButton('MENU', self)
        self.menu_btn.move(1330,20)
        self.menu_btn.setStyleSheet(f"background-image: url({main_window_background}); color: white; font-size: 28px;")
        self.menu_btn.setFixedSize(100, 50)
        self.menu_btn.setFlat(True)
        
        # 사과를 등급 별로 분류하여, 카운트를 표기할 사각형 모양 판===================================================================================
        self.rect_widget = QWidget(self)
        self.rect_widget.setGeometry(QRect(300, 690, 840, 80))
        self.rect_widget.setStyleSheet(f"background-image: url({menu_window_background_image}); border-radius: 20px;")
        
        # 사과를 등급 별로 분류하여, 카운트를 표기하기 위한 텍스트들==================================================================================
        self.text_label_1 = QLabel("A_CLASS : 0", self.rect_widget)
        self.text_label_1.setGeometry(QRect(10, 13, 135, 30))  
        self.text_label_1.setStyleSheet("color: white; font-size: 20px; font-weight: bold;")  

        self.text_label_2 = QLabel("B_CLASS : 0", self.rect_widget)
        self.text_label_2.setGeometry(QRect(165, 13, 130, 30))  
        self.text_label_2.setStyleSheet("color: white; font-size: 20px; font-weight: bold;")
        
        self.text_label_3 = QLabel("C_CLASS : 0", self.rect_widget)
        self.text_label_3.setGeometry(QRect(335, 13, 139, 30))  
        self.text_label_3.setStyleSheet("color: white; font-size: 20px; font-weight: bold;")
        
        self.text_label_4 = QLabel("D_CLASS : 0", self.rect_widget)
        self.text_label_4.setGeometry(QRect(515, 13, 160, 30))  
        self.text_label_4.setStyleSheet("color: white; font-size: 20px; font-weight: bold;")
        
        self.text_label_5 = QLabel("E_CLASS : 0", self.rect_widget)
        self.text_label_5.setGeometry(QRect(685, 13, 210, 30))  
        self.text_label_5.setStyleSheet("color: white; font-size: 20px; font-weight: bold;")
        
        self.text_label_6 = QLabel("TAN : 0", self.rect_widget)
        self.text_label_6.setGeometry(QRect(10, 50, 170, 30))  
        self.text_label_6.setStyleSheet("color: white; font-size: 20px; font-weight: bold;")
        
        self.text_label_7 = QLabel("GUP : 0", self.rect_widget)
        self.text_label_7.setGeometry(QRect(165, 50, 170, 30))  
        self.text_label_7.setStyleSheet("color: white; font-size: 20px; font-weight: bold;")
        
        self.text_label_8 = QLabel("BLACK_SPOT : 0", self.rect_widget)
        self.text_label_8.setGeometry(QRect(335, 50, 170, 30))  
        self.text_label_8.setStyleSheet("color: white; font-size: 20px; font-weight: bold;")
        
        # 등급 개수 카운트=======================================================================================================================
        self.count_1 = 0
        self.count_2 = 0
        self.count_3 = 0
        self.count_4 = 0
        self.count_5 = 0
        self.count_6 = 0
        self.count_7 = 0
        self.count_8 = 0
        
        self.set_count_1 = 0
        self.set_count_2 = 0
        self.set_count_3 = 0
        self.set_count_4 = 0
        self.set_count_5 = 0
        self.set_count_6 = 0
        self.set_count_7 = 0
        self.set_count_8 = 0
                
        # 메뉴판 생성===========================================================================================================================
        self.menu_widget = QWidget(self)
        self.menu_widget.setGeometry(QRect(0, 0, 0, 0))
        self.menu_widget.setStyleSheet(f"background-image: url({menu_window_background_image}); border-radius: 30px; font-weight: bold;")
        self.menu_widget.setVisible(False)
        
        self.animation_1 = QPropertyAnimation(self.menu_widget, b'geometry')
        self.animation_1.setDuration(300)  
        self.animation_1.setStartValue(QRect(1440, 60, 240, 739))
        self.animation_1.setEndValue(QRect(1200, 60, 240, 739))
        
        # A_CLASS================================================================================================================================
        MENU_button_1 = QPushButton("A_CLASS", self.menu_widget)
        MENU_button_1.clicked.connect(self.menu_button_animation_1)
        MENU_button_1.setGeometry(10, 30, 220, 50)  
        MENU_button_1.setStyleSheet(f"background-image: url({button_background_image}); color: #E6E6E6; font-weight: bold; border-radius: 15px;") 
        font = MENU_button_1.font()
        font.setPointSize(13)
        font.setFamily('Consolas')
        font.setBold(True)
        MENU_button_1.setFont(font)
        
        # 이미지를 보여주는 창, 스크롤바 형태로 밑으로 넘길 수 있음
        self.view_1 = QGraphicsView(self)
        self.view_1.setStyleSheet(f"background-image: url({button_background_image});")
        self.scene_1 = QGraphicsScene(self)
        
        rect_item_1 = QGraphicsRectItem(0, 0, 300, 800)  
        self.scene_1.addItem(rect_item_1)
        self.view_1.setScene(self.scene_1)
        
        # 스크롤 바 추가 및 창 애니메이션 설정
        h_scrollbar_1 = QScrollBar(self)
        h_scrollbar_1.setOrientation(2)  # 수직 방향
        self.view_1.setHorizontalScrollBar(h_scrollbar_1)
        self.view_1.setGeometry(QRect(0, 0, 300, 800))
        
        layout_1 = QVBoxLayout()
        layout_1.addWidget(self.view_1)
        
        self.timer_1 = QTimer(self)
        self.timer_1.timeout.connect(self.check_for_new_images_1)
        self.timer_1.start(500)
        
        layout_1.addWidget(h_scrollbar_1)
        self.setLayout(layout_1)
        self.view_1.setVisible(False)
        self.view_visible_1 = False
        self.animation_duration_1 = 500

        # B_CLASS================================================================================================================================
        MENU_button_2 = QPushButton("B_CLASS", self.menu_widget)
        MENU_button_2.clicked.connect(self.menu_button_animation_2)
        MENU_button_2.setGeometry(10, 120, 220, 50)  
        MENU_button_2.setStyleSheet(f"background-image: url({button_background_image}); color: #E6E6E6; font-weight: bold; border-radius: 15px;") 
        font = MENU_button_2.font()
        font.setPointSize(13)
        font.setFamily('Consolas')
        font.setBold(True)
        MENU_button_2.setFont(font)
        
        # 이미지를 보여주는 창, 스크롤바 형태로 밑으로 넘길 수 있음
        self.view_2 = QGraphicsView(self)
        self.view_2.setStyleSheet(f"background-image: url({button_background_image});")
        self.scene_2 = QGraphicsScene(self)
        
        rect_item_2 = QGraphicsRectItem(0, 0, 300, 800)  
        self.scene_2.addItem(rect_item_2)
        self.view_2.setScene(self.scene_2)
        
        # 스크롤 바 추가 및 창 애니메이션 설정
        h_scrollbar_2 = QScrollBar(self)
        h_scrollbar_2.setOrientation(2)  # 수직 방향
        self.view_2.setHorizontalScrollBar(h_scrollbar_2)
        self.view_2.setGeometry(QRect(0, 0, 300, 800))
        
        layout_2 = QVBoxLayout()
        layout_2.addWidget(self.view_2)
        
        self.timer_2 = QTimer(self)
        self.timer_2.timeout.connect(self.check_for_new_images_2)
        self.timer_2.start(500)
        
        layout_2.addWidget(h_scrollbar_2)
        self.setLayout(layout_2)
        self.view_2.setVisible(False)
        self.view_visible_2 = False
        self.animation_duration_2 = 500
        
        # C_CLASS================================================================================================================================
        MENU_button_3 = QPushButton("C_CLASS", self.menu_widget)
        MENU_button_3.clicked.connect(self.menu_button_animation_3)
        MENU_button_3.setGeometry(10, 210, 220, 50)  
        MENU_button_3.setStyleSheet(f"background-image: url({button_background_image}); color: #E6E6E6; font-weight: bold; border-radius: 15px;") 
        font = MENU_button_3.font()
        font.setPointSize(13)
        font.setFamily('Consolas')
        font.setBold(True)
        MENU_button_3.setFont(font)
        
        # 이미지를 보여주는 창, 스크롤바 형태로 밑으로 넘길 수 있음
        self.view_3 = QGraphicsView(self)
        self.view_3.setStyleSheet(f"background-image: url({button_background_image});")
        self.scene_3 = QGraphicsScene(self)
        
        rect_item_3 = QGraphicsRectItem(0, 0, 300, 800)  
        self.scene_3.addItem(rect_item_3)
        self.view_3.setScene(self.scene_3)
        
        # 스크롤 바 추가 및 창 애니메이션 설정
        h_scrollbar_3 = QScrollBar(self)
        h_scrollbar_3.setOrientation(2)  # 수직 방향
        self.view_3.setHorizontalScrollBar(h_scrollbar_3)
        self.view_3.setGeometry(QRect(0, 0, 300, 800))
        
        layout_3 = QVBoxLayout()
        layout_3.addWidget(self.view_3)
        
        self.timer_3 = QTimer(self)
        self.timer_3.timeout.connect(self.check_for_new_images_3)
        self.timer_3.start(500)
        
        layout_3.addWidget(h_scrollbar_3)
        self.setLayout(layout_3)
        self.view_3.setVisible(False)
        self.view_visible_3 = False
        self.animation_duration_3 = 500
        
        # D_CLASS================================================================================================================================
        MENU_button_4 = QPushButton("D_CLASS", self.menu_widget)
        MENU_button_4.clicked.connect(self.menu_button_animation_4)
        MENU_button_4.setGeometry(10, 300, 220, 50)  
        MENU_button_4.setStyleSheet(f"background-image: url({button_background_image}); color: #E6E6E6; font-weight: bold; border-radius: 15px;") 
        font = MENU_button_4.font()
        font.setPointSize(13)
        font.setFamily('Consolas')
        font.setBold(True)
        MENU_button_4.setFont(font)
        
        # 이미지를 보여주는 창, 스크롤바 형태로 밑으로 넘길 수 있음
        self.view_4 = QGraphicsView(self)
        self.view_4.setStyleSheet(f"background-image: url({button_background_image});")
        self.scene_4 = QGraphicsScene(self)
        
        rect_item_4 = QGraphicsRectItem(0, 0, 300, 800)  
        self.scene_4.addItem(rect_item_4)
        self.view_4.setScene(self.scene_4)
        
        # 스크롤 바 추가 및 창 애니메이션 설정
        h_scrollbar_4 = QScrollBar(self)
        h_scrollbar_4.setOrientation(2)  # 수직 방향
        self.view_4.setHorizontalScrollBar(h_scrollbar_4)
        self.view_4.setGeometry(QRect(0, 0, 300, 800))
        
        layout_4 = QVBoxLayout()
        layout_4.addWidget(self.view_4)
        
        self.timer_4 = QTimer(self)
        self.timer_4.timeout.connect(self.check_for_new_images_4)
        self.timer_4.start(500)
        
        layout_2.addWidget(h_scrollbar_4)
        self.setLayout(layout_4)
        self.view_4.setVisible(False)
        self.view_visible_4 = False
        self.animation_duration_4 = 500
        
        # E_CLASS================================================================================================================================
        MENU_button_5 = QPushButton("E_CLASS", self.menu_widget)
        MENU_button_5.clicked.connect(self.menu_button_animation_5)
        MENU_button_5.setGeometry(10, 390, 220, 50)  
        MENU_button_5.setStyleSheet(f"background-image: url({button_background_image}); color: #E6E6E6; font-weight: bold; border-radius: 15px;") 
        font = MENU_button_5.font()
        font.setPointSize(13)
        font.setFamily('Consolas')
        font.setBold(True)
        MENU_button_5.setFont(font)
        
        # 이미지를 보여주는 창, 스크롤바 형태로 밑으로 넘길 수 있음
        self.view_5 = QGraphicsView(self)
        self.view_5.setStyleSheet(f"background-image: url({button_background_image});")
        self.scene_5 = QGraphicsScene(self)
        
        rect_item_5 = QGraphicsRectItem(0, 0, 300, 800)  
        self.scene_5.addItem(rect_item_5)
        self.view_5.setScene(self.scene_5)
        
        # 스크롤 바 추가 및 창 애니메이션 설정
        h_scrollbar_5 = QScrollBar(self)
        h_scrollbar_5.setOrientation(2)  # 수직 방향
        self.view_5.setHorizontalScrollBar(h_scrollbar_5)
        self.view_5.setGeometry(QRect(0, 0, 300, 800))
        
        layout_5 = QVBoxLayout()
        layout_5.addWidget(self.view_5)
        
        self.timer_5 = QTimer(self)
        self.timer_5.timeout.connect(self.check_for_new_images_5)
        self.timer_5.start(500)
        
        layout_5.addWidget(h_scrollbar_5)
        self.setLayout(layout_5)
        self.view_5.setVisible(False)
        self.view_visible_5 = False
        self.animation_duration_5 = 500
        
        # 탄저병==================================================================================================================================
        MENU_button_6 = QPushButton("TAN_CLASS", self.menu_widget)
        MENU_button_6.clicked.connect(self.menu_button_animation_6)
        MENU_button_6.setGeometry(10, 460, 220, 50)  
        MENU_button_6.setStyleSheet(f"background-image: url({button_background_image}); color: #E6E6E6; font-weight: bold; border-radius: 15px;") 
        font = MENU_button_6.font()
        font.setPointSize(13)
        font.setFamily('Consolas')
        font.setBold(True)
        MENU_button_6.setFont(font)
        
        # 이미지를 보여주는 창, 스크롤바 형태로 밑으로 넘길 수 있음
        self.view_6 = QGraphicsView(self)
        self.view_6.setStyleSheet(f"background-image: url({button_background_image});")
        self.scene_6 = QGraphicsScene(self)
        
        rect_item_6 = QGraphicsRectItem(0, 0, 300, 800)  
        self.scene_6.addItem(rect_item_6)
        self.view_6.setScene(self.scene_6)
        
        # 스크롤 바 추가 및 창 애니메이션 설정
        h_scrollbar_6 = QScrollBar(self)
        h_scrollbar_6.setOrientation(2)  # 수직 방향
        self.view_6.setHorizontalScrollBar(h_scrollbar_6)
        self.view_6.setGeometry(QRect(0, 0, 300, 800))
        
        layout_6 = QVBoxLayout()
        layout_6.addWidget(self.view_6)
        
        self.timer_6 = QTimer(self)
        self.timer_6.timeout.connect(self.check_for_new_images_6)
        self.timer_6.start(500)
        
        layout_6.addWidget(h_scrollbar_6)
        self.setLayout(layout_6)
        self.view_6.setVisible(False)
        self.view_visible_6 = False
        self.animation_duration_6 = 500
        
        # 겹무늬썩음병============================================================================================================================
        MENU_button_7 = QPushButton("GUP_CLASS", self.menu_widget)
        MENU_button_7.clicked.connect(self.menu_button_animation_7)
        MENU_button_7.setGeometry(10, 530, 220, 50)  
        MENU_button_7.setStyleSheet(f"background-image: url({button_background_image}); color: #E6E6E6; font-weight: bold; border-radius: 15px;") 
        font = MENU_button_7.font()
        font.setPointSize(13)
        font.setFamily('Consolas')
        font.setBold(True)
        MENU_button_7.setFont(font)
        
        # 이미지를 보여주는 창, 스크롤바 형태로 밑으로 넘길 수 있음
        self.view_7 = QGraphicsView(self)
        self.view_7.setStyleSheet(f"background-image: url({button_background_image});")
        self.scene_7 = QGraphicsScene(self)
        
        rect_item_7 = QGraphicsRectItem(0, 0, 300, 800)  
        self.scene_7.addItem(rect_item_7)
        self.view_7.setScene(self.scene_7)
        
        # 스크롤 바 추가 및 창 애니메이션 설정
        h_scrollbar_7 = QScrollBar(self)
        h_scrollbar_7.setOrientation(2)  # 수직 방향
        self.view_7.setHorizontalScrollBar(h_scrollbar_7)
        self.view_7.setGeometry(QRect(0, 0, 300, 800))
        
        layout_7 = QVBoxLayout()
        layout_7.addWidget(self.view_7)
        
        self.timer_7 = QTimer(self)
        self.timer_7.timeout.connect(self.check_for_new_images_7)
        self.timer_7.start(500)
        
        layout_7.addWidget(h_scrollbar_7)
        self.setLayout(layout_7)
        self.view_7.setVisible(False)
        self.view_visible_7 = False
        self.animation_duration_7 = 500
        
        # 검은점무늬병============================================================================================================================
        MENU_button_8 = QPushButton("BLACK_SPOT_CLASS", self.menu_widget)
        MENU_button_8.clicked.connect(self.menu_button_animation_8)
        MENU_button_8.setGeometry(10, 600, 220, 50)  
        MENU_button_8.setStyleSheet(f"background-image: url({button_background_image}); color: #E6E6E6; font-weight: bold; border-radius: 15px;") 
        font = MENU_button_8.font()
        font.setPointSize(13)
        font.setFamily('Consolas')
        font.setBold(True)
        MENU_button_8.setFont(font)
        
        # 이미지를 보여주는 창, 스크롤바 형태로 밑으로 넘길 수 있음
        self.view_8 = QGraphicsView(self)
        self.view_8.setStyleSheet(f"background-image: url({button_background_image});")
        self.scene_8 = QGraphicsScene(self)
        
        rect_item_8 = QGraphicsRectItem(0, 0, 300, 800)  
        self.scene_8.addItem(rect_item_8)
        self.view_8.setScene(self.scene_8)
        
        # 스크롤 바 추가 및 창 애니메이션 설정
        h_scrollbar_8 = QScrollBar(self)
        h_scrollbar_8.setOrientation(2)  # 수직 방향
        self.view_8.setHorizontalScrollBar(h_scrollbar_8)
        self.view_8.setGeometry(QRect(0, 0, 300, 800))
        
        layout_8 = QVBoxLayout()
        layout_8.addWidget(self.view_8)
        
        self.timer_8 = QTimer(self)
        self.timer_8.timeout.connect(self.check_for_new_images_8)
        self.timer_8.start(500)
        
        layout_8.addWidget(h_scrollbar_8)
        self.setLayout(layout_8)
        self.view_8.setVisible(False)
        self.view_visible_8 = False
        self.animation_duration_8 = 500
        
        # 무게
        self.weight_timer = QTimer(self)
        self.weight_timer.timeout.connect(self.weight_timer_event)
        self.weight_timer.start(10)
        
        # 메뉴 버튼 클릭 시 애니메이션 토글=======================================================================================================
        self.menu_btn.clicked.connect(self.menu_Animation)
        self.show()
        
    def check_for_new_images_1(self):
        dir_watcher_1 = QDir(A_CLASS_image)
        dir_watcher_1.setNameFilters(['*.png', '*.jpg', '*.jpeg', '*.gif'])
        dir_watcher_1.refresh()

        current_images_1 = set(dir_watcher_1.entryList())

        new_images_1 = current_images_1 - self.image_list_1
        if new_images_1:
            for image in new_images_1:
                self.add_image_1(os.path.join(A_CLASS_image, image))

            self.image_list_1 = current_images_1
            
    def check_for_new_images_2(self):
        dir_watcher_2 = QDir(B_CLASS_image)
        dir_watcher_2.setNameFilters(['*.png', '*.jpg', '*.jpeg', '*.gif'])
        dir_watcher_2.refresh()

        current_images_2 = set(dir_watcher_2.entryList())

        new_images_2 = current_images_2 - self.image_list_2
        if new_images_2:
            for image in new_images_2:
                self.add_image_2(os.path.join(B_CLASS_image, image))

            self.image_list_2 = current_images_2
            
    def check_for_new_images_3(self):
        dir_watcher_3 = QDir(C_CLASS_image)
        dir_watcher_3.setNameFilters(['*.png', '*.jpg', '*.jpeg', '*.gif'])
        dir_watcher_3.refresh()

        current_images_3 = set(dir_watcher_3.entryList())

        new_images_3 = current_images_3 - self.image_list_3
        if new_images_3:
            for image in new_images_3:
                self.add_image_3(os.path.join(C_CLASS_image, image))

            self.image_list_3 = current_images_3
            
    def check_for_new_images_4(self):
        dir_watcher_4 = QDir(D_CLASS_image)
        dir_watcher_4.setNameFilters(['*.png', '*.jpg', '*.jpeg', '*.gif'])
        dir_watcher_4.refresh()

        current_images_4 = set(dir_watcher_4.entryList())

        new_images_4 = current_images_4 - self.image_list_4
        if new_images_4:
            for image in new_images_4:
                self.add_image_4(os.path.join(D_CLASS_image, image))

            self.image_list_4 = current_images_4
            
    def check_for_new_images_5(self):
        dir_watcher_5 = QDir(E_CLASS_image)
        dir_watcher_5.setNameFilters(['*.png', '*.jpg', '*.jpeg', '*.gif'])
        dir_watcher_5.refresh()

        current_images_5 = set(dir_watcher_5.entryList())

        new_images_5 = current_images_5 - self.image_list_5
        if new_images_5:
            for image in new_images_5:
                self.add_image_5(os.path.join(E_CLASS_image, image))

            self.image_list_5 = current_images_5
            
    def check_for_new_images_6(self):
        dir_watcher_6 = QDir(tan_image)
        dir_watcher_6.setNameFilters(['*.png', '*.jpg', '*.jpeg', '*.gif'])
        dir_watcher_6.refresh()

        current_images_6 = set(dir_watcher_6.entryList())

        new_images_6 = current_images_6 - self.image_list_6
        if new_images_6:
            for image in new_images_6:
                self.add_image_6(os.path.join(tan_image, image))

            self.image_list_6 = current_images_6
            
    def check_for_new_images_7(self):
        dir_watcher_7 = QDir(gup_image)
        dir_watcher_7.setNameFilters(['*.png', '*.jpg', '*.jpeg', '*.gif'])
        dir_watcher_7.refresh()

        current_images_7 = set(dir_watcher_7.entryList())

        new_images_7 = current_images_7 - self.image_list_7
        if new_images_7:
            for image in new_images_7:
                self.add_image_7(os.path.join(gup_image, image))

            self.image_list_7 = current_images_7
            
    def check_for_new_images_8(self):
        dir_watcher_8 = QDir(black_spot_image)
        dir_watcher_8.setNameFilters(['*.png', '*.jpg', '*.jpeg', '*.gif'])
        dir_watcher_8.refresh()

        current_images_8 = set(dir_watcher_8.entryList())

        new_images_8 = current_images_8 - self.image_list_8
        if new_images_8:
            for image in new_images_8:
                self.add_image_8(os.path.join(black_spot_image, image))

            self.image_list_8 = current_images_8
        
    def add_image_1(self, image_path_1):
        pixmap_item_1 = QGraphicsPixmapItem(self.load_image_1(image_path_1))
        pixmap_item_1.setPos(30, 60 * self.set_count_1)
        pixmap_item_1.setScale(0.3)
        self.set_count_1 += 3
        self.scene_1.addItem(pixmap_item_1)
        
    def add_image_2(self, image_path_2):
        pixmap_item_2 = QGraphicsPixmapItem(self.load_image_2(image_path_2))
        pixmap_item_2.setPos(30, 60 * self.set_count_2)
        pixmap_item_2.setScale(0.3)
        self.set_count_2 += 3
        self.scene_2.addItem(pixmap_item_2)
        
    def add_image_3(self, image_path_3):
        pixmap_item_3 = QGraphicsPixmapItem(self.load_image_3(image_path_3))
        pixmap_item_3.setPos(30, 60 * self.set_count_3)
        pixmap_item_3.setScale(0.3)
        self.set_count_3 += 3
        self.scene_3.addItem(pixmap_item_3)
        
    def add_image_4(self, image_path_4):
        pixmap_item_4 = QGraphicsPixmapItem(self.load_image_4(image_path_4))
        pixmap_item_4.setPos(30, 60 * self.set_count_4)
        pixmap_item_4.setScale(0.3)
        self.set_count_4 += 3
        self.scene_4.addItem(pixmap_item_4)
        
    def add_image_5(self, image_path_5):
        pixmap_item_5 = QGraphicsPixmapItem(self.load_image_5(image_path_5))
        pixmap_item_5.setPos(30, 60 * self.set_count_5)
        pixmap_item_5.setScale(0.3)
        self.set_count_5 += 3
        self.scene_5.addItem(pixmap_item_5)
        
    def add_image_6(self, image_path_6):
        pixmap_item_6 = QGraphicsPixmapItem(self.load_image_6(image_path_6))
        pixmap_item_6.setPos(30, 60 * self.set_count_6)
        pixmap_item_6.setScale(0.3)
        self.set_count_6 += 3
        self.scene_6.addItem(pixmap_item_6)
        
    def add_image_7(self, image_path_7):
        pixmap_item_7 = QGraphicsPixmapItem(self.load_image_7(image_path_7))
        pixmap_item_7.setPos(30, 60 * self.set_count_7)
        pixmap_item_7.setScale(0.3)
        self.set_count_7 += 3
        self.scene_7.addItem(pixmap_item_7)
        
    def add_image_8(self, image_path_8):
        pixmap_item_8 = QGraphicsPixmapItem(self.load_image_8(image_path_8))
        pixmap_item_8.setPos(30, 60 * self.set_count_8)
        pixmap_item_8.setScale(0.3)
        self.set_count_8 += 3
        self.scene_8.addItem(pixmap_item_8)
    
    def load_image_1(self, image_path_1):
        pixmap_1 = QPixmap(image_path_1)
        return pixmap_1
    
    def load_image_2(self, image_path_2):
        pixmap_2 = QPixmap(image_path_2)
        return pixmap_2
    
    def load_image_3(self, image_path_3):
        pixmap_3 = QPixmap(image_path_3)
        return pixmap_3
    
    def load_image_4(self, image_path_4):
        pixmap_4 = QPixmap(image_path_4)
        return pixmap_4
    
    def load_image_5(self, image_path_5):
        pixmap_5 = QPixmap(image_path_5)
        return pixmap_5
    
    def load_image_6(self, image_path_6):
        pixmap_6 = QPixmap(image_path_6)
        return pixmap_6
    
    def load_image_7(self, image_path_7):
        pixmap_7 = QPixmap(image_path_7)
        return pixmap_7
    
    def load_image_8(self, image_path_8):
        pixmap_8 = QPixmap(image_path_8)
        return pixmap_8
    
    # 시계 UI 업데이트 함수
    def updateTime(self):
        # 현재 시간 가져오기
        current_time = QTime.currentTime()

        # 시간을 시:분:초 형식으로 변환하여 레이블에 표시
        time_text = current_time.toString('hh:mm:ss')
        self.timeLabel.setText(time_text)
               
    def menu_button_animation_1(self):
        if not self.view_visible_1:
            self.animate_view_appear_1()
        else:
            self.animate_view_disappear_1()
            
    def menu_button_animation_2(self):
        if not self.view_visible_2:
            self.animate_view_appear_2()
        else:
            self.animate_view_disappear_2()
            
    def menu_button_animation_3(self):
        if not self.view_visible_3:
            self.animate_view_appear_3()
        else:
            self.animate_view_disappear_3()
            
    def menu_button_animation_4(self):
        if not self.view_visible_4:
            self.animate_view_appear_4()
        else:
            self.animate_view_disappear_4()
            
    def menu_button_animation_5(self):
        if not self.view_visible_5:
            self.animate_view_appear_5()
        else:
            self.animate_view_disappear_5()
            
    def menu_button_animation_6(self):
        if not self.view_visible_6:
            self.animate_view_appear_6()
        else:
            self.animate_view_disappear_6()
            
    def menu_button_animation_7(self):
        if not self.view_visible_7:
            self.animate_view_appear_7()
        else:
            self.animate_view_disappear_7()
            
    def menu_button_animation_8(self):
        if not self.view_visible_8:
            self.animate_view_appear_8()
        else:
            self.animate_view_disappear_8()
            
    # 이미지 출력 창 애니메이션
    def animate_view_appear_1(self):
        self.view_visible_1 = True
        self.view_1.setVisible(True)

        animation_2 = QPropertyAnimation(self.view_1, b"geometry")
        animation_2.setDuration(500)
        animation_2.setStartValue(QRect(0, -self.view_1.height(), self.view_1.width(), self.view_1.height()))
        animation_2.setEndValue(QRect(0, 0, self.view_1.width(), self.view_1.height()))
        animation_2.setEasingCurve(QEasingCurve.OutQuad)
        animation_2.start()

    def animate_view_disappear_1(self):
        self.view_visible_1 = False

        animation_3 = QPropertyAnimation(self.view_1, b"geometry")
        animation_3.setDuration(500)
        animation_3.setStartValue(QRect(0, 0, self.view_1.width(), self.view_1.height()))
        animation_3.setEndValue(QRect(0, -self.view_1.height(), self.view_1.width(), self.view_1.height()))
        animation_3.setEasingCurve(QEasingCurve.InQuad)
        animation_3.finished.connect(lambda: self.view_1.setVisible(False))
        animation_3.start()
        
    def animate_view_appear_2(self):
        self.view_visible_2 = True
        self.view_2.setVisible(True)

        animation_4 = QPropertyAnimation(self.view_2, b"geometry")
        animation_4.setDuration(500)
        animation_4.setStartValue(QRect(0, -self.view_2.height(), self.view_2.width(), self.view_2.height()))
        animation_4.setEndValue(QRect(0, 0, self.view_2.width(), self.view_2.height()))
        animation_4.setEasingCurve(QEasingCurve.OutQuad)
        animation_4.start()

    def animate_view_disappear_2(self):
        self.view_visible_2 = False

        animation_5 = QPropertyAnimation(self.view_2, b"geometry")
        animation_5.setDuration(500)
        animation_5.setStartValue(QRect(0, 0, self.view_2.width(), self.view_2.height()))
        animation_5.setEndValue(QRect(0, -self.view_2.height(), self.view_2.width(), self.view_2.height()))
        animation_5.setEasingCurve(QEasingCurve.InQuad)
        animation_5.finished.connect(lambda: self.view_2.setVisible(False))
        animation_5.start()
        
    def animate_view_appear_3(self):
        self.view_visible_3 = True
        self.view_3.setVisible(True)

        animation_6 = QPropertyAnimation(self.view_3, b"geometry")
        animation_6.setDuration(500)
        animation_6.setStartValue(QRect(0, -self.view_3.height(), self.view_3.width(), self.view_3.height()))
        animation_6.setEndValue(QRect(0, 0, self.view_3.width(), self.view_3.height()))
        animation_6.setEasingCurve(QEasingCurve.OutQuad)
        animation_6.start()

    def animate_view_disappear_3(self):
        self.view_visible_3 = False

        animation_7 = QPropertyAnimation(self.view_3, b"geometry")
        animation_7.setDuration(500)
        animation_7.setStartValue(QRect(0, 0, self.view_3.width(), self.view_3.height()))
        animation_7.setEndValue(QRect(0, -self.view_3.height(), self.view_3.width(), self.view_3.height()))
        animation_7.setEasingCurve(QEasingCurve.InQuad)
        animation_7.finished.connect(lambda: self.view_3.setVisible(False))
        animation_7.start()
        
    def animate_view_appear_4(self):
        self.view_visible_4 = True
        self.view_4.setVisible(True)

        animation_8 = QPropertyAnimation(self.view_4, b"geometry")
        animation_8.setDuration(500)
        animation_8.setStartValue(QRect(0, -self.view_4.height(), self.view_4.width(), self.view_4.height()))
        animation_8.setEndValue(QRect(0, 0, self.view_4.width(), self.view_4.height()))
        animation_8.setEasingCurve(QEasingCurve.OutQuad)
        animation_8.start()

    def animate_view_disappear_4(self):
        self.view_visible_4 = False

        animation_9 = QPropertyAnimation(self.view_4, b"geometry")
        animation_9.setDuration(500)
        animation_9.setStartValue(QRect(0, 0, self.view_4.width(), self.view_4.height()))
        animation_9.setEndValue(QRect(0, -self.view_4.height(), self.view_4.width(), self.view_4.height()))
        animation_9.setEasingCurve(QEasingCurve.InQuad)
        animation_9.finished.connect(lambda: self.view_4.setVisible(False))
        animation_9.start()
        
    def animate_view_appear_5(self):
        self.view_visible_5 = True
        self.view_5.setVisible(True)

        animation_10 = QPropertyAnimation(self.view_5, b"geometry")
        animation_10.setDuration(500)
        animation_10.setStartValue(QRect(0, -self.view_5.height(), self.view_5.width(), self.view_5.height()))
        animation_10.setEndValue(QRect(0, 0, self.view_5.width(), self.view_5.height()))
        animation_10.setEasingCurve(QEasingCurve.OutQuad)
        animation_10.start()

    def animate_view_disappear_5(self):
        self.view_visible_5 = False

        animation_11 = QPropertyAnimation(self.view_5, b"geometry")
        animation_11.setDuration(500)
        animation_11.setStartValue(QRect(0, 0, self.view_5.width(), self.view_5.height()))
        animation_11.setEndValue(QRect(0, -self.view_5.height(), self.view_5.width(), self.view_5.height()))
        animation_11.setEasingCurve(QEasingCurve.InQuad)
        animation_11.finished.connect(lambda: self.view_5.setVisible(False))
        animation_11.start()
        
    def animate_view_appear_6(self):
        self.view_visible_6 = True
        self.view_6.setVisible(True)

        animation_12 = QPropertyAnimation(self.view_6, b"geometry")
        animation_12.setDuration(500)
        animation_12.setStartValue(QRect(0, -self.view_6.height(), self.view_6.width(), self.view_6.height()))
        animation_12.setEndValue(QRect(0, 0, self.view_6.width(), self.view_6.height()))
        animation_12.setEasingCurve(QEasingCurve.OutQuad)
        animation_12.start()

    def animate_view_disappear_6(self):
        self.view_visible_6 = False

        animation_13 = QPropertyAnimation(self.view_6, b"geometry")
        animation_13.setDuration(500)
        animation_13.setStartValue(QRect(0, 0, self.view_6.width(), self.view_6.height()))
        animation_13.setEndValue(QRect(0, -self.view_6.height(), self.view_6.width(), self.view_6.height()))
        animation_13.setEasingCurve(QEasingCurve.InQuad)
        animation_13.finished.connect(lambda: self.view_6.setVisible(False))
        animation_13.start()
        
    def animate_view_appear_7(self):
        self.view_visible_7 = True
        self.view_7.setVisible(True)

        animation_14 = QPropertyAnimation(self.view_7, b"geometry")
        animation_14.setDuration(500)
        animation_14.setStartValue(QRect(0, -self.view_7.height(), self.view_7.width(), self.view_7.height()))
        animation_14.setEndValue(QRect(0, 0, self.view_7.width(), self.view_7.height()))
        animation_14.setEasingCurve(QEasingCurve.OutQuad)
        animation_14.start()

    def animate_view_disappear_7(self):
        self.view_visible_7 = False

        animation_15 = QPropertyAnimation(self.view_7, b"geometry")
        animation_15.setDuration(500)
        animation_15.setStartValue(QRect(0, 0, self.view_7.width(), self.view_7.height()))
        animation_15.setEndValue(QRect(0, -self.view_7.height(), self.view_7.width(), self.view_7.height()))
        animation_15.setEasingCurve(QEasingCurve.InQuad)
        animation_15.finished.connect(lambda: self.view_7.setVisible(False))
        animation_15.start()
        
    def animate_view_appear_8(self):
        self.view_visible_8 = True
        self.view_8.setVisible(True)

        animation_16 = QPropertyAnimation(self.view_8, b"geometry")
        animation_16.setDuration(500)
        animation_16.setStartValue(QRect(0, -self.view_8.height(), self.view_8.width(), self.view_8.height()))
        animation_16.setEndValue(QRect(0, 0, self.view_8.width(), self.view_8.height()))
        animation_16.setEasingCurve(QEasingCurve.OutQuad)
        animation_16.start()

    def animate_view_disappear_8(self):
        self.view_visible_8 = False

        animation_17 = QPropertyAnimation(self.view_8, b"geometry")
        animation_17.setDuration(500)
        animation_17.setStartValue(QRect(0, 0, self.view_8.width(), self.view_8.height()))
        animation_17.setEndValue(QRect(0, -self.view_8.height(), self.view_8.width(), self.view_8.height()))
        animation_17.setEasingCurve(QEasingCurve.InQuad)
        animation_17.finished.connect(lambda: self.view_8.setVisible(False))
        animation_17.start()
    
    # 메뉴판 안의 애니메이션 함수 
    def menu_Animation(self):
        if self.menu_widget.isVisible():
            self.animation_1.setDirection(QPropertyAnimation.Backward)    # 사각형 박스가 보이면 사라지도록 애니메이션 설정
        
        else:
            self.animation_1.setDirection(QPropertyAnimation.Forward) # 사각형 박스가 숨겨져 있으면 나타나도록 애니메이션 설정

        # 애니메이션 실행 및 사각형 박스의 가시성 토글
        self.animation_1.start()
        self.menu_widget.setVisible(not self.menu_widget.isVisible())
        
    def weight_timer_event(self):
        global weight_value, WEIGHT_VALUE
        weight_value = self.arduino.readline().decode()    
        WEIGHT_VALUE = float(weight_value)
        
    # 프레임 업데이트 함수
    def update_frame(self):
        global frame
        status, frame = self.webcam.read()

        if status:
            frame = cv2.resize(frame, (720, 480))   # 프로그램 창 크기 지정
            results = self.model.track(frame, persist = True, verbose = False)  # 객체가 여러 개일 때 ID 별로 구분하기 위해 track 붙임

            if results is not None:
                annotated_frame = results[0].plot()
                
                # 클래스를 구분하기 위한 코드
                boxes = results[0].boxes.xyxy.tolist()
                classes = results[0].boxes.cls.tolist()
                names = results[0].names
                confidences = results[0].boxes.conf.tolist()
                
                for box, cls, conf in zip(boxes, classes, confidences):
                    name = names[int(cls)]
                
                # 선으로 감지하기 위한 계산 코드
                result = results[0].cpu().boxes
                detect_id = result.id.tolist() if result.id != None else []
                detect_xyxy = result.xyxy.tolist() if result.xyxy != None else []
                frame_counting_buffer = dict(zip(detect_id, detect_xyxy))
                
                for i in frame_counting_buffer:
                    counting_buffer[i] = counting_buffer.get(i, [])
                    if len(counting_buffer[i]) >= 2:
                        counting_buffer[i] = counting_buffer[i][-1:]
                    # 버퍼에 평균 x 축 추가
                    avg_x = (frame_counting_buffer[i][0] + frame_counting_buffer[i][2]) / 2
                    counting_buffer[i].append(avg_x)
                    
                    if len(counting_buffer[i]) >= 2:
                        if (counting_buffer[i][0] > x_line) and (counting_buffer[i][1] < x_line):
                            if name == 'GOOD_APPLE': # A_CLASS APPLE
                                start_time_1 = time.time()
                                
                                while (time.time() - start_time_1 < 2):
                                    self.weight_timer_event()
                                    
                                if WEIGHT_VALUE >= 714:
                                    self.count_1 += 1
                                    self.text_label_1.setText(f"A_CLASS : {self.count_1}")
                                    img_name_1 = f'capture_{len(os.listdir(A_CLASS_image)) + 1}.png'
                                    img_path_1 = os.path.join(A_CLASS_image, img_name_1)
                                    cv2.imwrite(img_path_1, frame)
                                    
                                elif WEIGHT_VALUE >= 500 and WEIGHT_VALUE < 714:
                                    self.count_2 += 1
                                    self.text_label_2.setText(f"B_CLASS : {self.count_2}")                          
                                    img_name_2 = f'capture_{len(os.listdir(B_CLASS_image)) + 1}.png'
                                    img_path_2 = os.path.join(B_CLASS_image, img_name_2)
                                    cv2.imwrite(img_path_2, frame)
                                    
                                elif WEIGHT_VALUE >= 385 and WEIGHT_VALUE < 500:
                                    self.count_3 += 1
                                    self.text_label_3.setText(f"C_CLASS : {self.count_3}")
                                    img_name_3 = f'capture_{len(os.listdir(C_CLASS_image)) + 1}.png'
                                    img_path_3 = os.path.join(C_CLASS_image, img_name_3)
                                    cv2.imwrite(img_path_3, frame)
                                    
                                elif WEIGHT_VALUE >= 263 and WEIGHT_VALUE < 385:
                                    self.count_4 += 1
                                    self.text_label_4.setText(f"D_CLASS : {self.count_4}")
                                    img_name_4 = f'capture_{len(os.listdir(D_CLASS_image)) + 1}.png'
                                    img_path_4 = os.path.join(D_CLASS_image, img_name_4)
                                    cv2.imwrite(img_path_4, frame)
                                    
                                else:
                                    self.count_5 += 1
                                    self.text_label_5.setText(f"E_CLASS : {self.count_5}")
                                    img_name_5 = f'capture_{len(os.listdir(E_CLASS_image)) + 1}.png'
                                    img_path_5 = os.path.join(E_CLASS_image, img_name_5)
                                    cv2.imwrite(img_path_5, frame)
                                    
                                
                            elif name == 'SOSO_APPLE':
                                start_time_2 = time.time()
                                
                                while (time.time() - start_time_2 < 2):
                                    self.weight_timer_event()
                                
                                if WEIGHT_VALUE >= 714:
                                    self.count_2 += 1
                                    self.text_label_2.setText(f"B_CLASS : {self.count_2}")
                                    
                                    img_name_2 = f'capture_{len(os.listdir(B_CLASS_image)) + 1}.png'
                                    img_path_2 = os.path.join(B_CLASS_image, img_name_2)
                                    cv2.imwrite(img_path_2, frame)
                                
                                elif WEIGHT_VALUE >= 500 and WEIGHT_VALUE < 714:
                                    self.count_3 += 1
                                    self.text_label_3.setText(f"C_CLASS : {self.count_3}")
                                    img_name_3 = f'capture_{len(os.listdir(C_CLASS_image)) + 1}.png'
                                    img_path_3 = os.path.join(C_CLASS_image, img_name_3)
                                    cv2.imwrite(img_path_3, frame)
                                    
                                elif WEIGHT_VALUE >= 385 and WEIGHT_VALUE < 500:
                                    self.count_4 += 1
                                    self.text_label_4.setText(f"D_CLASS : {self.count_4}")                             
                                    img_name_4 = f'capture_{len(os.listdir(D_CLASS_image)) + 1}.png'
                                    img_path_4 = os.path.join(D_CLASS_image, img_name_4)
                                    cv2.imwrite(img_path_4, frame)
                                    
                                else:
                                    self.count_5 += 1
                                    self.text_label_5.setText(f"E_CLASS : {self.count_5}")
                                    img_name_5 = f'capture_{len(os.listdir(E_CLASS_image)) + 1}.png'
                                    img_path_5 = os.path.join(E_CLASS_image, img_name_5)
                                    cv2.imwrite(img_path_5, frame)
                        
                            elif name == 'TAN_APPLE':
                                print(WEIGHT_VALUE)
                                self.count_6 += 1
                                self.text_label_6.setText(f"TAN : {self.count_6}")
                                
                                img_name_6 = f'capture_{len(os.listdir(tan_image)) + 1}.png'
                                img_path_6 = os.path.join(tan_image, img_name_6)
                                cv2.imwrite(img_path_6, frame)
                        
                            elif name == 'GUP_APPLE':
                                print(WEIGHT_VALUE)
                                self.count_7 += 1
                                self.text_label_7.setText(f"GUP : {self.count_7}")
                                
                                img_name_7 = f'capture_{len(os.listdir(gup_image)) + 1}.png'
                                img_path_7 = os.path.join(gup_image, img_name_7)
                                cv2.imwrite(img_path_7, frame)
                        
                            elif name == 'BLACK_SPOT':
                                print(WEIGHT_VALUE)
                                self.count_8 += 1
                                self.text_label_8.setText(f"BLACK_SPOT : {self.count_8}")
                                
                                img_name_8 = f'capture_{len(os.listdir(black_spot_image)) + 1}.png'
                                img_path_8 = os.path.join(black_spot_image, img_name_8)
                                cv2.imwrite(img_path_8, frame)
                
                cv2.line(annotated_frame, pt1=pt1, pt2=pt2, color=(0, 0, 255), thickness=2) 
                
                height, width, channel = annotated_frame.shape
                bytes_per_line = 3 * width
                q_image = QImage(annotated_frame.data, width, height, bytes_per_line, QImage.Format_BGR888)

                pixmap = QPixmap.fromImage(q_image)

                # 웹캠 화면을 프로그램 창의 어디에 띄울지 정하는 변수
                cam_coordinate_x = 100
                cam_coordinate_y = 100
                
                # 웹캠 화면 좌표 설정 및 업데이트
                self.image_label.setGeometry(cam_coordinate_x, cam_coordinate_y, width, height)
                self.image_label.setPixmap(pixmap)
                self.image_label.update()
        
    def keyPressEvent(self, event):
        # 'Q' 키를 누르면 프로그램을 종료합니다.
        if event.key() == Qt.Key_Q:
            A_CLASS_files = glob.glob('APPLE_IMAGE_FOLDER/A_CLASS/*.png')
            B_CLASS_files = glob.glob('APPLE_IMAGE_FOLDER/B_CLASS/*.png')
            C_CLASS_files = glob.glob('APPLE_IMAGE_FOLDER/C_CLASS/*.png')
            D_CLASS_files = glob.glob('APPLE_IMAGE_FOLDER/D_CLASS/*.png')
            E_CLASS_files = glob.glob('APPLE_IMAGE_FOLDER/E_CLASS/*.png')
            tan_files = glob.glob('APPLE_IMAGE_FOLDER/TAN_APPLE/*.png')
            gup_files = glob.glob('APPLE_IMAGE_FOLDER/GUP_APPLE/*.png')
            black_spot_files = glob.glob('APPLE_IMAGE_FOLDER/BLACK_SPOT_APPLE/*.png')
            [os.remove(f) for f in A_CLASS_files]
            [os.remove(f) for f in B_CLASS_files]
            [os.remove(f) for f in C_CLASS_files]
            [os.remove(f) for f in D_CLASS_files]
            [os.remove(f) for f in E_CLASS_files]
            [os.remove(f) for f in tan_files]
            [os.remove(f) for f in gup_files]
            [os.remove(f) for f in black_spot_files]
            self.arduino.close()
            super().closeEvent(event)
            app.quit()
    
# 메인 함수
if __name__ == '__main__':
    app = QApplication(sys.argv)
    my_app = MAIN_WINDOW() 
    my_app.show() 
    sys.exit(app.exec_()) 