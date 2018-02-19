# encoding: utf-8

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# --> let me know if you have ideas for improving
# --> Mark Froemberg aka DeutschMark @ GitHub
# --> www.markfromberg.com
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

class ShowDistanceAndAngleOfNodes ( ReporterPlugin ):
	def settings(self):
		self.menuName = "Distance & Angle"

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
				
				### HACK TO KEEP THE TEXT IN ITS BADGE FOR ALL ZOOMS
				badgeAlpha = .75
				
				'''
				ANGLE
				'''
				dx, dy = x2 - x1, y2 - y1
				rads = math.atan2( dy, dx )
				degs = math.degrees( rads )

				### CLEAN UP THE DIRECTIONS, LIMIT ANGLES BETWEEN 0 AND 180
				### SO THE SAME PERCIEVED ANGLE WILL HAVE THE SAME VALUE
				### IGNORING PATH DIRECTION
				if -180 < degs < -90:
					degs = degs + 180
				elif degs == 180:
					degs = 0
				elif degs == -90:
					degs = 90
				
				scale = self.getScale()
				
				string = NSString.stringWithString_(u"%s\n%s°" % ( round(dist, 1), round(degs, 1) ))
				attributes = NSString.drawTextAttributes_(NSColor.whiteColor())
				textSize = string.sizeWithAttributes_(attributes)
				
				### BADGE
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
	
	def getHandleSize( self ):
		try:
			Selected = NSUserDefaults.standardUserDefaults().integerForKey_( "GSHandleSize" )
			if Selected == 0:
				return 5.0
			elif Selected == 2:
				return 10.0
			else:
				return 7.0 # Regular
		except Exception as e:
			self.logToConsole( "getHandleSize: HandleSize defaulting to 7.0. %s" % str(e) )
			return 7.0

	def getScale( self ):
		return self._scale
	
	def setController_( self, Controller ):
		try:
			self.controller = Controller
		except Exception as e:
			self.logToConsole( "Could not set controller" )
	
	def logToConsole( self, message ):
		myLog = "Show %s plugin:\n%s" % ( self.title(), message )
		NSLog( myLog )

	def __file__(self):
		"""Please leave this method unchanged"""
		return __file__
