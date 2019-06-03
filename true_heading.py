from objc_util import *
import ui
from arview import MyARView
import time


def run_ar_kit(true):
    v = MyARView()
    v.present('full_screen', hide_title_bar=True, orientations=['portrait'])
    v.initialize(true)


def locationManager_didUpdateHeading_(self, _cmd, manager, newHeading):
    headingObj = ObjCInstance(newHeading)
    magnetic = headingObj.magneticHeading()
    true = headingObj.trueHeading()
    myloc.stopUpdatingHeading()
    run_ar_kit(true)


def locationManager_didFailWithError_(_self,_cmd,manager,error):
    error = ObjCInstance(error)
    print(error)


methods = [locationManager_didUpdateHeading_, locationManager_didFailWithError_]
protocols = ['CLLocationManagerDelegate']
MyLocationManagerDelegate = create_objc_class('MyLocationManagerDelegate', methods=methods, protocols=protocols)
CLLocationManager = ObjCClass ('CLLocationManager')
myloc = CLLocationManager.alloc().init().autorelease()
delegate = MyLocationManagerDelegate.alloc().init()
myloc.setDelegate_(delegate)
locationAvailable = CLLocationManager.headingAvailable()
myloc.headingOrientation = 3
myloc.headingFilter = 3
myloc.startUpdatingHeading()

