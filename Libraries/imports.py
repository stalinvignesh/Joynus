#from android.permissions import request_permissions, Permission
import cv2
import kivymd.uix.fitimage
import numpy as np
import traceback,sys
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.uix.image import Image
from kivymd.app import MDApp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.uix.label import MDLabel , MDIcon
from kivymd.uix.button import MDRaisedButton , MDFillRoundFlatButton , MDFloatingActionButton
from kivymd.uix.dropdownitem import  MDDropDownItem
from kivymd.uix.menu import MDDropdownMenu
#from android.permissions import request_permissions, Permission
from kivymd.uix.dialog import MDDialog
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.textfield  import MDTextField
import random
from kivy.properties import StringProperty
from pyzbar.pyzbar import decode
from kivy.storage.jsonstore import JsonStore
from datetime import datetime,date
import qrcode
from kivy.core.image import Image as CoreImage
from io import BytesIO
from kivymd.uix.fitimage import FitImage
from kivymd.uix.pickers import MDDatePicker, MDTimePicker
import os,sys,re
import yagmail
from kivymd.uix.selectioncontrol import MDCheckbox , MDSwitch
from kivymd.uix.controllers import WindowController
from kivymd.uix.segmentedcontrol import MDSegmentedControl,MDSegmentedControlItem
from kivymd.uix.snackbar import MDSnackbar
from kivymd.uix.card import MDCard
from kivymd.uix.relativelayout import MDRelativeLayout
import cv2
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.button import MDIconButton
from kivymd.uix.segmentedbutton import MDSegmentedButton,MDSegmentedButtonItem
from kivy.properties import BooleanProperty, ObjectProperty
from kivymd.uix.card import MDSeparator
from kivy.base import ExceptionManager, ExceptionHandler
from kivy.logger import Logger
from kivymd.uix.scrollview import MDScrollView
from kivy.animation import Animation,AnimationTransition
from kivymd.uix.spinner import MDSpinner
from kivymd.uix.spinner.spinner import MDSpinner
from kivy.uix.screenmanager import FadeTransition
from kivymd.uix.list import OneLineIconListItem , OneLineAvatarIconListItem, IconRightWidget , IconLeftWidgetWithoutTouch
from kivymd.uix.list import MDList
from kivymd.toast import toast
from kivy.effects.dampedscroll import DampedScrollEffect