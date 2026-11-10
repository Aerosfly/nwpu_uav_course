#!/usr/bin/env python3
import rospy
import rospkg
from geometry_msgs.msg import Twist
from sensor_msgs.msg import Image
import cv2
from cv_bridge import CvBridge
import numpy as np
import pyzbar.pyzbar as pyzbar  # 导入刚才装好的二维码库

w = 360
h = 240

# 控制参数
ptd_w = [0.5, 0, 0] # 偏航参数
ptd_f = [0.8, 0, 0] # 前后参数
zero_twist_published = False
bridge = None
pub = None
speed = Twist()

def findQRCode(img):
    # 转换为灰度图
    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    barcodes = pyzbar.decode(imgGray)
    
    myCodeC = []
    myCodeArea = []
    
    for barcode in barcodes:
        (x, y, w_box, h_box) = barcode.rect
        # 画绿色方框
        cv2.rectangle(img, (x, y), (x + w_box, y + h_box), (0, 255, 0), 2)
        
        # 提取内容
        barcodeData = barcode.data.decode("utf-8")
        # 屏幕上显示文字
        cv2.putText(img, barcodeData, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        # 终端打印
        rospy.loginfo("Found QRCODE: {}".format(barcodeData))
        
        cx = x + w_box // 2
        cy = y + h_box // 2
        area = w_box * h_box
        
        myCodeArea.append(area)
        myCodeC.append([cx, cy])
        
    if len(myCodeArea) != 0:
        i = myCodeArea.index(max(myCodeArea))
        return img, [myCodeC[i], myCodeArea[i]]
    else:
        return img, [[0, 0], 0]

def trackTarget(info, w, h, ptd_w, ptd_f):
    # yaw channel (偏航通道)
    error_w = info[0][0] - w // 2
    speed_w = ptd_w[0] * error_w
    speed_w = int(np.clip(speed_w, -100, 100)) / 100.0

    # forward channel (前后通道)
    error_f = np.sqrt(info[1]) - 70
    speed_f = ptd_f[0] * error_f
    speed_f = int(np.clip(speed_f, -100, 100)) / 100.0

    if info[0][0] != 0:
        yaw_speed = speed_w
    else:
        yaw_speed = 0

    if info[1] != 0:
        forward_speed = speed_f
    else:
        forward_speed = 0

    return yaw_speed, forward_speed

def callback(msg):
    global zero_twist_published, bridge, pub
    img = bridge.imgmsg_to_cv2(msg, "bgr8")
    img = cv2.resize(img, (w, h))
    
    # 调用二维码识别
    img, info = findQRCode(img)
    yaw_speed, forward_speed = trackTarget(info, w, h, ptd_w, ptd_f)
    
    rc = "forward: " + str(round(forward_speed, 2)) + " yaw: " + str(round(yaw_speed, 2))
    
    if yaw_speed != 0 or forward_speed != 0:
        speed.linear.x = -forward_speed
        speed.linear.y = 0.0
        speed.linear.z = 0.0 
        speed.angular.x = 0.0
        speed.angular.y = 0.0
        speed.angular.z = -yaw_speed
        rospy.loginfo(rc)
        pub.publish(speed)
        zero_twist_published = False
    else:
        if not zero_twist_published:
            pub.publish(speed) # 没找到二维码就悬停
            zero_twist_published = True
        
    cv2.imshow('QR Frame', img)
    cv2.waitKey(1)

if __name__ == '__main__':
    bridge = CvBridge()
    rospy.init_node('qr_tracker', anonymous=True)
    pub = rospy.Publisher("cmd_vel", Twist, queue_size=1)
    sub = rospy.Subscriber("image_raw", Image, callback)
    
    rospy.spin()
