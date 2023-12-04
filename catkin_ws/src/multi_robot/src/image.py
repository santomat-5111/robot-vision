#!/usr/bin/env python3
import roslib
roslib.load_manifest('multi_robot')
import sys
import rospy
import cv2
from std_msgs.msg import String
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError
import numpy as np

class image_converter:

  def __init__(self):
    

    self.bridge = CvBridge()
    self.image_sub = rospy.Subscriber("/image_raw",Image,self.callback)

  def callback(self,data):
    try:
      cv_image = self.bridge.imgmsg_to_cv2(data, "bgr8")
    except CvBridgeError as e:
      print(e)

    cv2.imshow("Image window", cv_image)
    cv2.waitKey(3)

    blue_img, green_img, red_img = cv2.split(cv_image)
 
    blur = cv2.GaussianBlur(red_img, (5, 5), cv2.BORDER_DEFAULT)
    ret, thresh = cv2.threshold(blur, 58, 255, cv2.THRESH_BINARY)

    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # if len(contours) > 0:
    #   red_areas = max(contours, key=cv2.contourArea)
    #   x, y, w, h = cv2.boundingRect(red_areas)
    #   cv2.rectangle(mask,(x, y),(x+w, y+h),(0, 0, 255), 2)

    # rect = cv2.minAreaRect(contours)
    # box = cv2.boxPoints(rect)
    # box = np.int0(box)
    # cv2.drawContours(cv_image,[box],0,(0,0,255),2)

    for c in contours:
      rect = cv2.minAreaRect(c)
      box = cv2.boxPoints(rect)
      box = np.int0(box)
      cv_image = cv2.drawContours(cv_image,[box],0,(0,255,0),2)
      M = cv2.moments(c)
      if M['m00'] != 0:
          cx = int(M['m10']/M['m00'])
          cy = int(M['m01']/M['m00'])
          cv2.circle(cv_image, (cx, cy), 1, (0, 0, 255), -1)

    cv2.imshow("Identification", cv_image)


    try:
      self.image_pub.publish(self.bridge.cv2_to_imgmsg(cv_image, "bgr8"))
    except CvBridgeError as e:
      print(e)

def main(args):
  ic = image_converter()
  rospy.init_node('image_converter', anonymous=True)
  try:
    rospy.spin()
  except KeyboardInterrupt:
    print("Shutting down")
  cv2.destroyAllWindows()

if __name__ == '__main__':
    main(sys.argv)