# encoding: utf-8
from __future__ import division, print_function, unicode_literals

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# --> let me know if you have ideas for improving
# --> Mark Froemberg aka DeutschMark @ GitHub
# --> www.markfromberg.com
#
# - Note:
# 		+ About Relative/Absolute/Shortest angle: https://forum.glyphsapp.com/t/show-distance-and-angle/8176/17
#
# - ToDo
#	-
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from GlyphsApp import *
from GlyphsApp.plugins import *
from Foundation import NSString
from AppKit import NSColor, NSBezierPath
import math
import traceback

@objc.python_method
def UnitVectorFromTo(B, A):
	A.x -= B.x
	A.y -= B.y
	Length = math.sqrt((A.x * A.x) + (A.y * A.y))
	A.x /= Length
	A.y /= Length
	return A

COLOR = 0, .6, 1, 0.75

class ShowDistanceAndAngle(ReporterPlugin):

	@objc.python_method
	def settings(self):
		try:
			self.menuName = Glyphs.localize({
				'en': "Distance & Angle",
				'de': 'Abstand & Winkel',
				'fr': 'distance & angle',
				'es': 'distancia & angulo',
			})
			
			# print(self.menuName, "Version 1.0.5")
			self.thisMenuTitle = {"name": u"%s:" % self.menuName, "action": None}
			self.vID = "com.markfromberg.ShowDistanceAndAngle"  # vendorID

			self.angleAbsolute = True
			if not self.LoadPreferences():
				print("Error: Could not load preferences. Will resort to defaults.")

			self.angleStyles = {
				True: u"= Relative Angle",
				False: u"= Shortest Angle",  # Absolute = % 360
			}

			self.generalContextMenus = [
				self.thisMenuTitle,
				{"name": u"%s" % self.angleStyles[bool(self.angleAbsolute)], "action": self.toggleAngleStyle_},
			]
		except:
			print(traceback.format_exc())

	def toggleAngleStyle_(self, sender):
		try:
			self.angleAbsolute = not self.angleAbsolute
			self.generalContextMenus = [
				self.thisMenuTitle,
				{"name": "%s" % self.angleStyles[bool(self.angleAbsolute)], "action": self.toggleAngleStyle_},
			]
			self.RefreshView()
			self.SavePreferences()
		except:
			print(traceback.format_exc())

	@objc.python_method
	def SavePreferences(self):
		try:
			Glyphs.defaults["%s.angleStyle" % self.vID] = self.angleAbsolute  # self.w.hTarget.get()
		except:
			print(traceback.format_exc())

	@objc.python_method
	def LoadPreferences(self):
		try:
			Glyphs.registerDefault("%s.angleStyle" % self.vID, True)  # Default
			try:
				self.angleAbsolute = Glyphs.boolDefaults["%s.angleStyle" % self.vID]
			except:
				return False

			return True
		except:
			print(traceback.format_exc())

	@objc.python_method
	def foregroundInViewCoords(self, layer=None):
		if layer is None:
			layer = self.controller.activeLayer()
		if layer:
			try:
				self.drawNodeDistanceText(layer)
			except:
				print(traceback.format_exc())

	@objc.python_method
	def background(self, layer):
		try:
			selection = layer.selection
			if len(selection) == 2:
				x1, y1 = selection[0].x, selection[0].y
				x2, y2 = selection[1].x, selection[1].y
				self.drawLine(x1, y1, x2, y2)
		except:
			print(traceback.format_exc())

	@objc.python_method
	def drawCoveringBadge(self, x, y, width, height, radius):
		try:
			myPath = NSBezierPath.alloc().init()
			NSColor.colorWithCalibratedRed_green_blue_alpha_(*COLOR).set()
			myRect = NSRect((x, y), (width, height))
			thisPath = NSBezierPath.bezierPathWithRoundedRect_cornerRadius_(myRect, radius)
			myPath.appendBezierPath_(thisPath)
			myPath.fill()
		except:
			print(traceback.format_exc())

	@objc.python_method
	def drawLine(self, x1, y1, x2, y2, strokeWidth=1):
		try:
			myPath = NSBezierPath.bezierPath()
			myPath.moveToPoint_((x1, y1))
			myPath.lineToPoint_((x2, y2))
			myPath.setLineWidth_(strokeWidth / self.getScale())
			NSColor.colorWithCalibratedRed_green_blue_alpha_(*COLOR).set()
			myPath.stroke()
		except:
			print(traceback.format_exc())

	@objc.python_method
	def drawNodeDistanceText(self, layer):
		if layer is None:
			return
		try:
			try:
				selection = layer.selection
			except:
				selection = layer.selection()
			if len(selection) == 2:
				x1, y1 = selection[0].x, selection[0].y
				x2, y2 = selection[1].x, selection[1].y
				t = 0.5  # MIDLLE
				xAverage = x1 + (x2 - x1) * t
				yAverage = y1 + (y2 - y1) * t
				dist = math.hypot(x2 - x1, y2 - y1)

				# Angle
				#======
				# print(x2 >= x1 or y2 >= y1)
				switch = (x1, y1) >= (x2, y2)

				if switch and not self.angleAbsolute:
					dx, dy = x1 - x2, y1 - y2
					#print("switch")
				else:
					dx, dy = x2 - x1, y2 - y1
				rads = math.atan2(dy, dx)
				degs = math.degrees(rads)

				if self.angleAbsolute:
					degs = degs % 180  # Not using 360 here. same angles will have the same number, no matter the path direction of this segment
				else:
					degs = abs(degs) % 90

				scale = self.getScale()
				string = NSString.stringWithString_(u"%s\n%s°" % (round(dist, 1), round(degs, 1)))
				attributes = NSString.drawTextAttributes_(NSColor.whiteColor())
				textSize = string.sizeWithAttributes_(attributes)

				# Badge
				#======
				badgeWidth = textSize.width + 8
				badgeHeight = textSize.height + 4
				badgeRadius = 5

				unitVector = UnitVectorFromTo(NSPoint(x1, y1), NSPoint(x2, y2))

				badgeOffsetX = -unitVector.y * (badgeWidth / 2 + 4)
				badgeOffsetY = unitVector.x * (badgeHeight / 2 + 4)

				cpX, cpY = math.floor(xAverage), math.floor(yAverage)

				glyphEditView = self.controller.graphicView()
				try:
					selection = glyphEditView.selectedLayerRange()
				except:
					selection = glyphEditView.textStorage().selectedRange()
				origin = glyphEditView.cachedPositionAtIndex_(selection.location)
				cpX = cpX * scale + origin[0]
				cpY = cpY * scale + origin[1]

				self.drawCoveringBadge(cpX - badgeWidth / 2 - badgeOffsetX, cpY - badgeHeight / 2 - badgeOffsetY, badgeWidth, badgeHeight, badgeRadius)
				self.drawText(string, (cpX - badgeOffsetX, cpY - badgeOffsetY))
		except:
			print(traceback.format_exc())

	@objc.python_method
	def drawText(self, text, textPosition, fontColor=NSColor.whiteColor()):
		try:
			string = NSString.stringWithString_(text)
			string.drawAtPoint_color_alignment_handleSize_(textPosition, fontColor, 4, -1)
		except:
			print(traceback.format_exc())

	def needsExtraMainOutlineDrawingForInactiveLayer_(self, layer):
		return True

	@objc.python_method
	def RefreshView(self):
		try:
			currentTabView = Glyphs.font.currentTab
			if currentTabView:
				currentTabView.graphicView().setNeedsDisplay_(True)
		except:
			pass

	@objc.python_method
	def logToConsole(self, message):
		myLog = "Show %s plugin:\n%s" % (self.title(), message)
		NSLog(myLog)

	@objc.python_method
	def __file__(self):
		"""Please leave this method unchanged"""
		return __file__
