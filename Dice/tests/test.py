###
# Copyright (c) 2010, Andrey Rahmatullin
# Copyright (c) 2020, oddluck <oddluck@riseup.net>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright notice,
#     this list of conditions, and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions, and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name of the author of this software nor the name of
#     contributors to this software may be used to endorse or promote products
#     derived from this software without specific prior written consent.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
###

from supybot.test import PluginTestCase

class DiceTestCase(PluginTestCase):
    plugins = ('Dice',)
    def testPlugin(self):
        self.assertHelp('Dice roll')
        self.assertNotError('Dice roll 1d2')
        self.assertNoResponse('Dice roll dummy')

    def testRollStd(self):
        self.assertRegexp('Dice roll 1d20', r'\[1d20\] \d+')
        self.assertRegexp('Dice roll d20', r'\[1d20\] \d+')
        self.assertRegexp('Dice roll 1d20+5', r'\[1d20\+5\] \d+')
        self.assertRegexp('Dice roll d20+5', r'\[1d20\+5\] \d+')
        self.assertRegexp('Dice roll 1d20-30', r'\[1d20-30\] -\d+')
        self.assertRegexp('Dice roll d20-30', r'\[1d20-30\] -\d+')
        self.assertRegexp('Dice roll 2d20-1', r'\[2d20-1\] \d+')
        self.assertRegexp('Dice roll d20-1d6+3', r'\[1d20-1d6\+3\] -?\d+')
        self.assertRegexp('Dice roll 1d20+d20+3', r'\[2d20\+3\] \d+')
        self.assertRegexp('Dice roll 1d20+4+d6-3', r'\[1d20\+1d6\+1\] \d+')
        self.assertNoResponse('Dice roll 1d1')

    def testRollMult(self):
        self.assertRegexp('Dice roll 2#1d20', r'\[1d20\] \d+, \d+')
        self.assertRegexp('Dice roll 2#d20', r'\[1d20\] \d+, \d+')
        self.assertRegexp('Dice roll 2#1d20+5', r'\[1d20\+5\] \d+, \d+')
        self.assertRegexp('Dice roll 2#d20+5', r'\[1d20\+5\] \d+, \d+')
        self.assertRegexp('Dice roll 2#1d20-30', r'\[1d20-30\] -\d+, -\d+')
        self.assertRegexp('Dice roll 2#d20-30', r'\[1d20-30\] -\d+, -\d+')
        self.assertRegexp('Dice roll 2#2d20-1', r'\[2d20-1\] \d+, \d+')
        self.assertNoResponse('Dice roll 2#1d1')

    def testRollSR(self):
        self.assertRegexp('Dice roll 2#sd', r'\(pool 2\) (\d hits?|critical glitch!)')
        self.assertRegexp('Dice roll 4#sd', r'\(pool 4\) (\d hits?(, glitch)?|critical glitch!)')
        self.assertNoResponse('Dice roll 0#sd')

    def testRollSRX(self):
        self.assertRegexp('Dice roll 2#sdx', r'\(pool 2, exploding\) (\d hits?|critical glitch!)')
        self.assertRegexp('Dice roll 4#sdx', r'\(pool 4, exploding\) (\d hits?(, glitch)?|critical glitch!)')
        self.assertNoResponse('Dice roll 0#sdx')

    def testRoll7S(self):
        self.assertRegexp('Dice roll 3k2', r'\[3k2\] \(\d+\) \d+, \d+')
        self.assertRegexp('Dice roll 2k3', r'\[2k2\] \(\d+\) \d+, \d+')
        self.assertRegexp('Dice roll 3kk2', r'\[3k2\] \(\d+\) \d+, \d+ \| \d+')
        self.assertRegexp('Dice roll +3k2', r'\[3k2\] \(\d+\) \d+, \d+ \| \d+')
        self.assertRegexp('Dice roll -3k2', r'\[3k2, not exploding\] \(\d+\) \d+, \d+')
        self.assertRegexp('Dice roll +3kk2', r'\[3k2\] \(\d+\) \d+, \d+ \| \d+')
        self.assertRegexp('Dice roll -3kk2', r'\[3k2, not exploding\] \(\d+\) \d+, \d+ \| \d+')
        self.assertRegexp('Dice roll 3k2+1', r'\[3k2\+1\] \(\d+\) \d+, \d+')
        self.assertRegexp('Dice roll 3k2-1', r'\[3k2-1\] \(\d+\) \d+, \d+')
        self.assertRegexp('Dice roll -3k2-1', r'\[3k2-1, not exploding\] \(\d+\) \d+, \d+')
        self.assertRegexp('Dice roll 10k10', r'\[10k10\] \(\d+\) (\d+, ){9}\d+')
        self.assertRegexp('Dice roll 12k10', r'\[10k10\+20\] \(\d+\) (\d+, ){9}\d+')
        self.assertRegexp('Dice roll 12k9', r'\[10k10\+10\] \(\d+\) (\d+, ){9}\d+')
        self.assertRegexp('Dice roll 12k8', r'\[10k10\] \(\d+\) (\d+, ){9}\d+')
        self.assertRegexp('Dice roll 12k9+5', r'\[10k10\+15\] \(\d+\) (\d+, ){9}\d+')
        self.assertRegexp('Dice roll 12kk9', r'\[10k10\+10\] \(\d+\) (\d+, ){9}\d+')
        self.assertRegexp('Dice roll 12kk7', r'\[10k9\] \(\d+\) (\d+, ){8}\d+ \| \d+')
        self.assertRegexp('Dice roll 3#3k2', r'\[3k2\] \(\d+\) \d+, \d+(; \(\d+\) \d+, \d+){2}')

    def testDeck(self):
        validator = r'(2|3|4|5|6|7|8|9|10|J|Q|K|A)(♣|♦|♥|♠)|(Black|Red) Joker'
        self.assertRegexp('Dice draw', validator)
        self.assertResponse('Dice shuffle', 'shuffled')
        for i in range(0, 54):
            self.assertRegexp('Dice draw', validator)

    def testWoD(self):
        self.assertRegexp('Dice roll 3w', r'\(3\) (\d success(es)?|FAIL)')
        self.assertRegexp('Dice roll 3w-', r'\(3, not exploding\) (\d success(es)?|FAIL)')
        self.assertRegexp('Dice roll 3w8', r'\(3, 8-again\) (\d success(es)?|FAIL)')
        self.assertNoResponse('Dice roll 0w')

    def testDH(self):
        self.assertRegexp('Dice roll vs(10)', r'-?\d+ \(\d+ vs 10\)')
        self.assertRegexp('Dice roll vs(10+20)', r'-?\d+ \(\d+ vs 30\)')
        self.assertRegexp('Dice roll vs(10+20-5)', r'-?\d+ \(\d+ vs 25\)')
        self.assertRegexp('Dice roll 3vs(10+20)', r'-?\d+, -?\d+, -?\d+ \(\d+, \d+, \d+ vs 30\)')

    def testWG(self):
        self.assertRegexp('Dice roll 10#wg', r'\[pool 10\] \d+ icon\(s\): [❶❷❸❹❺❻] ([1-5➅] )*(\| Glory|\| Complication)?')


# vim:set shiftwidth=4 tabstop=8 expandtab textwidth=78:
