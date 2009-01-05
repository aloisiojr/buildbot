import os, time
from buildbot import uthreads
from twisted.trial import unittest
from twisted.application import service
from twisted.internet import defer, reactor
from buildbot.framework import master
from test.base import TestCase
import StringIO

stubclasses = """
from buildbot.framework import interfaces
from zope.interface import implements

from buildbot.framework.sourcemanager import SourceManager
class MySourceManager(SourceManager):
    implements(interfaces.ISourceManager)

from buildbot.framework.slaves import Slave
class MySlave(Slave):
    implements(interfaces.ISlave)

from buildbot.framework.scheduler import Scheduler
class MyScheduler(Scheduler):
    implements(interfaces.IScheduler)
"""

add_one_of_each = """
addSourceManager(MySourceManager('sm'))
addSlave(MySlave('sl', 'pass'))
addScheduler(MyScheduler('sch', lambda stuff : None))
"""

just_sourcemgr = """
addSourceManager(MySourceManager('sm2'))
"""

class config(TestCase):
    def configToFile(conf):
        return StringIO.StringIO(conf)

    @uthreads.returns_deferred
    def testLoadConfig(self):
        bm = master.BuildMaster(".", "cfg.py")
        yield bm.loadConfig(stubclasses + add_one_of_each)
        assert len(bm.slaves) == 1
        assert len(bm.sourceManagerPool) == 1
        assert len(bm.schedulerPool) == 1

    @uthreads.returns_deferred
    def testReloadConfig(self):
        bm = master.BuildMaster(".", "cfg.py")
        yield bm.loadConfig(stubclasses + add_one_of_each)
        assert len(bm.slaves) == 1
        assert len(bm.sourceManagerPool) == 1
        assert len(bm.schedulerPool) == 1
        yield bm.loadConfig(stubclasses + add_one_of_each + just_sourcemgr)
        assert len(bm.slaves) == 1
        assert len(bm.sourceManagerPool) == 2
        assert len(bm.schedulerPool) == 1
        yield bm.loadConfig(stubclasses + just_sourcemgr)
        assert len(bm.slaves) == 0
        assert len(bm.sourceManagerPool) == 1
        assert len(bm.schedulerPool) == 0
