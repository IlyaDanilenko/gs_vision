#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import cv2
import rospy
from rospy import Subscriber,Publisher
from std_msgs.msg import Int32
from sensor_msgs.msg import Image
from cv_bridge import CvBridge,CvBridgeError
from gs_vision.msg import Apriltag,Apriltag_array
from apriltag import Detector,Detection

rospy.init_node("apriltag_node") # обязательный блок инициализации ноды

image_topic_name=rospy.get_param(rospy.search_param("image_topic"))

bridge = CvBridge() # Класс конвертора из картинки форма ROS в формат OpenCv
detector = Detector() # Класс детектора apriltag
apriltag_publisher = Publisher("geoscan/vision/apriltag", Apriltag_array, queue_size=10) # объвление Издателя - публикует сообщение в топик в который публикуются id тегов
sost = Apriltag_array()
apriltag_publisher.publish(sost)

def callback(data): # функция обработки подписчика
    global bridge
    global detector
    global apriltag_publisher
    global sost
    try:
        img = bridge.imgmsg_to_cv2(data,"bgr8") # конвертирование картинки ROS в OpenCv
        img = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY) # обесцвечивание картинки
        result = detector.detect(img) # детектирование apriltag
        if (len(result) > 0):
            apr_a = Apriltag_array()
            for r in result:
                apr = Apriltag()
                apr.tag_family = str(r.tag_family, encoding='utf-8')
                apr.tag_id = r.tag_id
                apr.hamming = r.hamming
                apr.goodness = r.goodness
                apr.decision_margin = r.decision_margin
                apr.center_x = r.center[0]
                apr.center_y = r.center[1]
                apr.x1 = r.corners[0][0]
                apr.y1 = r.corners[0][1]
                apr.x2 = r.corners[1][0]
                apr.y2 = r.corners[1][1]
                apr.x3 = r.corners[2][0]
                apr.y3 = r.corners[2][1]
                apr.x4 = r.corners[3][0]
                apr.y4 = r.corners[3][1]
                apr_a.apriltags.append(apr)
            sost = apr_a
            apriltag_publisher.publish(apr_a) # публикует в топик id распознаного apriltag
        else:
            if (Apriltag_array() != sost):
                null_apriltag = Apriltag_array()
                apriltag_publisher.publish(null_apriltag) # если детектор не распознал apriltag публикует в топик число соответствующего пустому id
                sost = null_apriltag

    except CvBridgeError as e:
        rospy.loginfo(str(e))

image_subscriber = Subscriber(image_topic_name, Image, callback) # подписчик на топик в котором публикуется изображения камеры

while not rospy.is_shutdown(): # обязательное часть иначе нода прирвется после приема одного сообщения
    pass
