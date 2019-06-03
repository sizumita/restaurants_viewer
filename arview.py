# coding: utf-8

import json
import time
from enum import IntFlag
from math import pi
import location
import numpy
import requests
import ui
from numpy import sin, cos
from objc_util import *


class SCNVector3(Structure):
    _fields_ = [('x', c_float), ('y', c_float), ('z', c_float)]


load_framework('SceneKit')
load_framework('ARKit')
with open('token.txt') as f:
    API_KEY = f.read()

URL = 'http://webservice.recruit.co.jp/hotpepper/gourmet/v1/?key={0}&lat={1}&lng={2}&range=5&format=json'

byou = 25.2
scale = 40
W = 4
L = 100
H = 4


class_list = [
    'NSError', 'SCNScene', 'ARSCNView',
    'ARWorldTrackingConfiguration',
    'ARSession', 'UIViewController',
    'ARPlaneAnchor', 'SCNView', 'SCNBox',
    'SCNText', 'SCNNode',
    'SCNLight', 'SCNCamera',
    'SCNAction',
    'SCNTransaction',
    'UIFont',
    'SCNSphere', 'SCNFloor',
    'SCNLookAtConstraint',
    'SCNPhysicsShape',
    'SCNPhysicsBody',
    'UIColor', 'NSObject'
]

NSError, SCNScene, ARSCNView, ARWorldTrackingConfiguration, \
ARSession, UIViewController, ARPlaneAnchor, SCNView, SCNBox, \
SCNText, SCNNode, SCNLight, SCNCamera, SCNAction, SCNTransaction, \
UIFont, SCNSphere, SCNFloor, SCNLookAtConstraint, \
SCNPhysicsShape, SCNPhysicsBody, UIColor, NSObject = map(ObjCClass, class_list)
deepskyblue = UIColor.color(red=0.0, green=191.0, blue=255.0, alpha=1.0)

rotate_action = SCNAction.rotateByX_y_z_duration_(0, pi * 2, 0, 10)
up = SCNAction.moveByX_y_z_duration_(0, 30, 0, 3)
down = SCNAction.moveByX_y_z_duration_(0, -30, 0, 3)
up_down = SCNAction.sequence_([up, down])

scene_view = None


class ARWorldAlignment(IntFlag):
    ARWorldAlignmentGravity = 0
    ARWorldAlignmentGravityAndHeading = 1
    ARWorldAlignmentCamera = 2


class ARPlaneDetection(IntFlag):
    ARPlaneDetectionNone = 0
    ARPlaneDetectionHorizontal = 1 << 0
    ARPlaneDetectionVertical = 1 << 1


class ARSessionRunOptions(IntFlag):
    ARSessionRunOptionsNone = 0
    ARSessionRunOptionResetTracking = 1 << 0
    ARSessionRunOptionRemoveExistingAnchors = 1 << 1


def get_location():
    location.start_updates()  # GPSデータ更新を開始
    gps_data = location.get_location()  # GPSデータを取得する
    location.stop_updates()  # GPSデータ更新を終了

    return gps_data['latitude'], gps_data['longitude']


def get_restaurants(_lat, _lng):
    """緯度: lat 経度: lng"""
    response = requests.get(URL.format(API_KEY, _lat, _lng))
    result = json.loads(response.text)
    lat_lng = []
    for restaurant in result['results']['shop']:
        lat = float(restaurant['lat'])
        lng = float(restaurant['lng'])
        lat_lng.append((lat, lng, restaurant['name']))
    r = []
    for lat, lng, name in lat_lng:
        r2 = []

        difference = (_lat - lat) * 3600
        r2.append(int(difference * byou))

        difference = (lng - _lng) * 3600
        r2.append(int(difference * byou))
        r2.append(name)

        r.append(r2)

    return r


def createARSceneView(x, y, w, h, debug=True):
    v = ARSCNView.alloc().initWithFrame_((CGRect(CGPoint(x, y), CGSize(w, h))))
    v.setShowsStatistics_(debug)
    return v


@on_main_thread
def run(ar_session):
    ar_configuration = ARWorldTrackingConfiguration.alloc().init()
    ar_configuration.setPlaneDetection_(ARPlaneDetection.ARPlaneDetectionHorizontal)
    ar_configuration.setWorldAlignment_(
        ARWorldAlignment.ARWorldAlignmentGravity)

    ar_session.runWithConfiguration_options_(ar_configuration,
                                             ARSessionRunOptions.ARSessionRunOptionResetTracking | ARSessionRunOptions.ARSessionRunOptionRemoveExistingAnchors)

    time.sleep(0.5)


def CustomViewController_viewWillAppear_(_self, _cmd, animated):
    return


def CustomViewController_viewWillDisappear_(_self, _cmd, animated):
    session = scene_view.session()
    session.pause()


def MyARSCNViewDelegate_renderer_didAdd_for_(_self, _cmd, scenerenderer, node, anchor):
    if not isinstance(anchor, ARPlaneAnchor):
        return


def MyARSCNViewDelegate_session_didFailWithError_(_self, _cmd, _session, _error):
    print('error', _error, _cmd, _session)
    err_obj = ObjCInstance(_error)
    print(err_obj)


def convert_round(x, z, r):
    cosr = cos(r)
    sinr = sin(r)
    X = cosr * x - sinr * z
    Z = sinr * x + cosr * z
    return X, Z


def get_text(text, x, y, z):
    text_mesh = SCNText.textWithString_extrusionDepth_(text, 3.0)
    text_mesh.setFlatness_(0.2)
    text_mesh.setChamferRadius_(0.4)
    text_mesh.setFont_(UIFont.fontWithName_size_('HelveticaNeue-Bold', 15))
    bbox_min, bbox_max = SCNVector3(), SCNVector3()
    text_mesh.getBoundingBoxMin_max_(byref(bbox_min), byref(bbox_max), restype=None,
                                     argtypes=[POINTER(SCNVector3), POINTER(SCNVector3)])
    text_width = bbox_max.x - bbox_min.x
    text_node = SCNNode.nodeWithGeometry_(text_mesh)
    text_node.setCastsShadow_(True)
    text_container = SCNNode.node()
    text_container.addChildNode_(text_node)
    text_container.setPosition_((x, y, z))
    text_container.runAction(SCNAction.repeatActionForever(SCNAction.group([rotate_action, up_down])))
    text_node.setPosition_((-text_width / 2, 0, 0))
    return text_container


def add_restaurants(root_node, round_num):
    restaurants = get_restaurants(*get_location())
    if round_num == 90.0 or round_num == 0:
        r = 0
    elif round_num < 90:
        if round_num < 45:
            r = round_num + (45 - round_num)
        else:
            r = 45 + round_num * 2
    else:
        r = round_num
    for restaurant in restaurants:
        box = SCNBox.boxWithWidth_height_length_chamferRadius_(W, L, H, 0)
        box_node = SCNNode.nodeWithGeometry_(box)
        x, z = restaurant[1], restaurant[0]

        if r:
            x, z = convert_round(x, z, r)
        box_node.setPosition_((x, 25, z))
        box_node.runAction(SCNAction.repeatActionForever(rotate_action))

        a = numpy.array([0, 0])
        b = numpy.array(restaurant[:2])
        u = b - a
        length = numpy.linalg.norm(u)

        if length < 100:
            box.material().setColor_(deepskyblue.CGColor())
        else:
            box.material().setColor_(UIColor.blueColor().CGColor())
        name = str(restaurant[2])
        metal = '{}メートル'.format(int(length))
        root_node.addChildNode_(
            get_text('{0}\n{1}'.format(name, metal.center(len(name))), x - 6, 25, z - 6))
        root_node.addChildNode_(box_node)


class MyARView(ui.View):
    def __init__(self):
        super().__init__(self)
        self.flex = 'WH'

    @on_main_thread
    def initialize(self, round_num):
        global scene_view

        screen = ui.get_screen_size()

        # シーンのセットアップ
        scene = SCNScene.scene()

        # view delegateのセットアップ
        methods = [MyARSCNViewDelegate_renderer_didAdd_for_, MyARSCNViewDelegate_session_didFailWithError_]
        protocols = ['ARSCNViewDelegate']
        MyARSCNViewDelegate = create_objc_class('MyARSCNViewDelegate', NSObject, methods=methods, protocols=protocols)
        delegate = MyARSCNViewDelegate.alloc().init()

        # シーンviewのセットアップ
        scene_view = createARSceneView(0, 0, screen.width, screen.height)
        scene_view.scene = scene
        scene_view.setDelegate_(delegate)

        # コントローラーのセットアップ
        methods = [CustomViewController_viewWillAppear_, CustomViewController_viewWillDisappear_]
        protocols = []
        CustomViewController = create_objc_class('CustomViewController', UIViewController, methods=methods,
                                                 protocols=protocols)
        cvc = CustomViewController.alloc().init()
        cvc.view = scene_view

        # 初期設定
        self_objc = ObjCInstance(self)
        self_objc.nextResponder().addChildViewController_(cvc)
        self_objc.addSubview_(scene_view)
        cvc.didMoveToParentViewController_(self_objc)

        # ARのセッションを開始
        run(scene_view.session())

        root_node = scene.rootNode()

        scene_view = SCNView.alloc().initWithFrame_options_(((0, 0), (400, 400)), None).autorelease()
        scene_view.setAutoresizingMask_(18)
        scene_view.setAllowsCameraControl_(True)

        # 光源設定
        light_node = SCNNode.node()
        light_node.setPosition_((1.5, 1.5, 1.5))
        light = SCNLight.light()
        light.setType_('omni')
        light.setCastsShadow_(True)
        light_node.setLight_(light)

        # カメラ設定
        camera = SCNCamera.camera()
        camera_node = SCNNode.node()
        camera_node.setCamera(camera)
        camera_node.setPosition((0, 2, 0))

        # メインノードに子ノードを追加
        root_node.addChildNode_(camera_node)
        root_node.addChildNode_(light_node)
        add_restaurants(root_node, round_num)

    def will_close(self):
        session = scene_view.session()
        session.pause()


if __name__ == '__main__':
    v = MyARView()
    v.present('full_screen', hide_title_bar=True, orientations=['portrait'])
    v.initialize(0)

