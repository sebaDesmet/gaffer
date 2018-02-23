##########################################################################
#
#  Copyright (c) 2018, Image Engine Design Inc. All rights reserved.
#
#  Redistribution and use in source and binary forms, with or without
#  modification, are permitted provided that the following conditions are
#  met:
#
#      * Redistributions of source code must retain the above
#        copyright notice, this list of conditions and the following
#        disclaimer.
#
#      * Redistributions in binary form must reproduce the above
#        copyright notice, this list of conditions and the following
#        disclaimer in the documentation and/or other materials provided with
#        the distribution.
#
#      * Neither the name of John Haddon nor the names of
#        any other contributors to this software may be used to endorse or
#        promote products derived from this software without specific prior
#        written permission.
#
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
#  IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
#  THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
#  PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR
#  CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
#  EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
#  PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
#  PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
#  LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
#  NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
#  SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
##########################################################################

import GafferUITest
import GafferUI
import GafferTest
import Gaffer

import os
import time
import weakref

class BackupsTest( GafferUITest.TestCase ) :

	def testAcquire( self ) :

		a = Gaffer.ApplicationRoot()
		self.assertIsNone( GafferUI.Backups.acquire( a, createIfNecessary = False ) )

		b = GafferUI.Backups.acquire( a )
		self.assertIsInstance( b, GafferUI.Backups )
		self.assertIs( b, GafferUI.Backups.acquire( a ) )

		wa = weakref.ref( a )
		wb = weakref.ref( b )

		del a
		self.assertIsNone( wa() )
		del b
		self.assertIsNone( wb() )

	def testSingleBackup( self ) :

		a = Gaffer.ApplicationRoot()

		b = GafferUI.Backups.acquire( a )
		b.settings()["fileName"].setValue( self.temporaryDirectory() + "/backups/${script:name}.gfr" )

		s = Gaffer.ScriptNode()
		s["fileName"].setValue( self.temporaryDirectory() + "/test.gfr" )
		a["scripts"].addChild( s )
		s.save()

		backupFileName = self.temporaryDirectory() + "/backups/test.gfr"
		self.assertFalse( os.path.exists( backupFileName ) )
		self.assertEqual( b.backups( s ), [] )

		self.assertEqual( b.backup( s ), backupFileName )
		self.assertTrue( os.path.exists( backupFileName ) )
		self.assertEqual( b.backups( s ), [ backupFileName ] )
		self.__assertFilesEqual( s["fileName"].getValue(), backupFileName )

		s.addChild( Gaffer.Node() )
		s.save()

		self.assertEqual( b.backup( s ), backupFileName )
		self.assertEqual( b.backups( s ), [ backupFileName ] )
		self.__assertFilesEqual( s["fileName"].getValue(), backupFileName )

	def testMultipleBackups( self ) :

		a = Gaffer.ApplicationRoot()

		b = GafferUI.Backups.acquire( a )
		b.settings()["fileName"].setValue( "${script:directory}/${script:name}-backup${backup:number}.gfr" )
		b.settings()["files"].setValue( 3 )

		s = Gaffer.ScriptNode()
		s["fileName"].setValue( self.temporaryDirectory() + "/test.gfr" )
		s["add"] = GafferTest.AddNode()
		a["scripts"].addChild( s )

		expectedBackups = []
		for i in range( 0, 50 ) :

			s["add"]["op1"].setValue( i )
			s.save()

			backupFileName = "{0}/test-backup{1}.gfr".format( self.temporaryDirectory(), i % 3 )
			if i < 3 :
				self.assertFalse( os.path.exists( backupFileName ) )

			self.assertEqual( b.backup( s ), backupFileName )
			self.assertTrue( os.path.exists( backupFileName ) )
			self.__assertFilesEqual( s["fileName"].getValue(), backupFileName )

			expectedBackups.append( backupFileName )
			if len( expectedBackups ) > 3 :
				del expectedBackups[0]
			self.assertEqual( b.backups( s ), expectedBackups )

			time.sleep( 0.01 )

	def __assertFilesEqual( self, f1, f2 ) :

		with open( f1 ) as f1 :
			l1 = f1.readlines()

		with open( f2 ) as f2 :
			l2 = f2.readlines()

		self.assertEqual( l1, l2 )

if __name__ == "__main__":
	unittest.main()
