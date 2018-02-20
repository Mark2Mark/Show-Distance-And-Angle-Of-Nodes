# encoding: utf-8

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

import objc
from GlyphsApp import *
from GlyphsApp.plugins import *
from Foundation import NSString
import sys, os, re
import math
import traceback


def UnitVectorFromTo(B, A):
	A.x -= B.x
	A.y -= B.y
	Length = math.sqrt((A.x * A.x) + (A.y * A.y))
	A.x /= Length
	A.y /= Length
	return A


class ShowDistanceAndAngle ( ReporterPlugin ):
	def settings(self):
		self.menuName = "Distance & Angle"
		self.thisMenuTitle = {"name": u"%s:" % self.menuName, "action": None }
		self.vID = "com.markfromberg.ShowDistanceAndAngle" # vendorID

		self.angleAbsolute = True
		if not self.LoadPreferences( ):
			print "Error: Could not load preferences. Will resort to defaults."

		self.angleStyles = {
			"True" : u"= Relative Angle",
			"False" : u"= Shortest Angle", # Absolute = % 360
		}

		self.generalContextMenus = [
			self.thisMenuTitle,
			{"name": u"%s" % self.angleStyles[str(self.angleAbsolute)], "action": self.toggleAngleStyle },
		]
		

	def toggleAngleStyle(self):
		self.angleAbsolute = not self.angleAbsolute
		self.generalContextMenus = [
			self.thisMenuTitle,
			{"name": u"%s" % self.angleStyles[str(self.angleAbsolute)], "action": self.toggleAngleStyle },
		]
		
		self.RefreshView()
		self.SavePreferences()


	def SavePreferences( self ):
		Glyphs.defaults[ "%s.angleStyle" % self.vID ] = self.angleAbsolute#self.w.hTarget.get()

	def LoadPreferences( self ):
		Glyphs.registerDefault(  "%s.angleStyle" % self.vID, True ) # Default
		try:
			self.angleAbsolute = Glyphs.defaults[ "%s.angleStyle" % self.vID ]
		except:
			return False
		
		return True







	def foregroundInViewCoords(self, layer):
		try:
			self.drawNodeDistanceText( layer )
		except Exception as e:
			self.logToConsole( "drawForegroundForLayer_: %s" % str(e) )

	def drawCoveringBadge(self, x, y, width, height, radius, alpha):
		myPath = NSBezierPath.alloc().init()
		NSColor.colorWithCalibratedRed_green_blue_alpha_( 0, .6, 1, alpha ).set()
		myRect = NSRect( ( x, y ), ( width, height ) )
		thisPath = NSBezierPath.bezierPathWithRoundedRect_cornerRadius_( myRect, radius )
		myPath.appendBezierPath_( thisPath )
		myPath.fill()
	
	def drawNodeDistanceText( self, Layer ):
		try:
			badgeAlpha = .75
			try:
				selection = Layer.selection
			except:
				selection = Layer.selection()
			if len(selection) == 2:
				x1, y1 = selection[0].x, selection[0].y
				x2, y2 = selection[1].x, selection[1].y
				t = 0.5 # MIDLLE
				xAverage = x1 + (x2-x1) * t
				yAverage = y1 + (y2-y1) * t
				dist = math.hypot(x2 - x1, y2 - y1)
				
				

				# Angle
				#======
				dx, dy = x2 - x1, y2 - y1
				rads = math.atan2( dy, dx )
				degs = math.degrees( rads )


				if self.angleAbsolute == True:
					degs = degs % 180 # Not using 360 here. same angles will have the same number, no matter the path direction of this segment
				elif self.angleAbsolute == False:
					degs = degs % 90


				scale = self.getScale()		
				string = NSString.stringWithString_(u"%s\n%s°" % ( round(dist, 1), round(degs, 1) ))
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
				origin = glyphEditView.cachedPositionAtIndex_(glyphEditView.selectedLayerRange().location)
				cpX = cpX * scale + origin[0]
				cpY = cpY * scale + origin[1]
				
				self.drawCoveringBadge( cpX - badgeWidth/2 - badgeOffsetX, cpY - badgeHeight/2 - badgeOffsetY, badgeWidth, badgeHeight, badgeRadius, badgeAlpha)
				### is this one slowing down?
				self.drawText( string, (cpX - badgeOffsetX, cpY - badgeOffsetY))
		except Exception, e:
			self.logToConsole(e)
			pass
	
	def drawText( self, text, textPosition, fontColor=NSColor.whiteColor() ):
		try:
			string = NSString.stringWithString_(text)
			string.drawAtPoint_color_alignment_(textPosition, fontColor, 4)
		except Exception as e:
			self.logToConsole( "drawTextAtPoint: %s" % str(e) )


	def needsExtraMainOutlineDrawingForInactiveLayer_( self, Layer ):
		return True


	def RefreshView(self):
		try:
			Glyphs = NSApplication.sharedApplication()
			currentTabView = Glyphs.font.currentTab
			if currentTabView:
				currentTabView.graphicView().setNeedsDisplay_(True)
		except:
			pass


	def getScale( self ):
		return self._scale
	
	
	def logToConsole( self, message ):
		myLog = "Show %s plugin:\n%s" % ( self.title(), message )
		NSLog( myLog )

	def __file__(self):
		"""Please leave this method unchanged"""
		return __file__
