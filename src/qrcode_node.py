#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import cv2
from pyzbar.pyzbar import decode,Decoded,Point,Rect
import rospy
from rospy import Subscriber,Publisher
from gs_vision.msg import QR,QR_array
from sensor_msgs.msg import Image
from cv_bridge import CvBridge,CvBridgeError

rospy.init_node("qrcode_node")

image_topic_name=rospy.get_param(rospy.search_param("image_topic"))

bridge = CvBridge()
qr_publisher = Publisher("geoscan/vision/qr", QR_array, queue_size=10)
sost = QR_array()
qr_publisher.publish(sost)

def callback(data):
    global bridge
    global qr_publisher
    global sost
    try:
        img = bridge.imgmsg_to_cv2(data,"bgr8")
        result = decode(img)
        qr_a = QR_array()
        if (len(result) > 0):
            for qr_d in result:
                if (qr_d.type == "QRCODE"):
                    qr = QR()
                    qr.data = str(qr_d.data, encoding="utf-8")
                    qr.left = qr_d.rect.left
                    qr.top = qr_d.rect.top
                    qr.width = qr_d.rect.width
                    qr.height = qr_d.rect.height
                    qr.x1 = qr_d.polygon[0].x
                    qr.y1 = qr_d.polygon[0].y
                    qr.x2 = qr_d.polygon[1].x
                    qr.y2 = qr_d.polygon[1].y
                    qr.x3 = qr_d.polygon[2].x
                    qr.y3 = qr_d.polygon[2].y
                    qr.x4 = qr_d.polygon[3].x
                    qr.y4 = qr_d.polygon[3].y
                    qr_a.qrs.append(qr)
            sost = qr_a
            qr_publisher.publish(qr_a)
        else:
            if (QR_array() != sost):
                null_qr = QR_array()
                qr_publisher.publish(null_qr)
                sost = null_qr
    except CvBridgeError as e:
        rospy.loginfo(str(e))

image_subscriber = Subscriber(image_topic_name, Image, callback)

while not rospy.is_shutdown():
    pass
