###
# Copyright (c) 2015, waratte
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

# Standard modules
import random
import time
import os
import re
import subprocess
import requests

import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks
try:
    from supybot.i18n import PluginInternationalization
    _ = PluginInternationalization('Cobe')
except ImportError:
    # Placeholder that allows to run the plugin on a bot
    # without the i18n module
    _ = lambda x:x

# Additional supybot modules
import supybot.ircmsgs as ircmsgs
import supybot.conf as conf
import supybot.schedule as schedule
import supybot.log as log

# Custom modules imported
try:
    from cobe_hubbot.sqlite_brain import SQLiteBrain
except ImportError:
    raise callbacks.Error('You need to install cobe for this plugin to work!')

MATCH_MESSAGE_STRIPNICK = re.compile('^(<[^ ]+> )?(?P<message>.*)$')

class Cobe(callbacks.Plugin):
    """
    Cobe is frontend to the cobe markov-chain bot for Limnoria/supybot. Use "list Cobe" to list possible
    commands and "help Cobe <command>" to read their docs.
    """
    threaded = True
    magicnick = '<&#@!%~>'

    def __init__(self, irc):
        self.__parent = super(Cobe, self)
        self.__parent.__init__(irc)

    def _strip_nick(self, irc, msg, text):
        for user in irc.state.channels[msg.args[0]].users:
            if len(user) <= 4: # Do not replace short nicks, as they might very
                # well be part of a word
                continue
            text = text.replace(user, self.magicnick)
            text = text.replace(user.lower(), self.magicnick)
            text = text.replace(user.capitalize(), self.magicnick)
        return text

    def _getBrainDirectoryForChannel(self, channel):
        """Internal method for retrieving the directory of a brainfile for a channel"""
        directory = conf.supybot.directories.data
        directory = directory.dirize(channel.lower() + "/cobe.brain")
        return directory

    def _doCommand(self, channel):
        """Internal method for accessing a cobe brain."""
        dataDirectory = conf.supybot.directories.data
        dataDirectory = dataDirectory.dirize(channel.lower() + "/cobe.brain")
        return 'cobe --brain %s' % dataDirectory

    def _cleanText(self, text):
        """Internal method for cleaning text of imperfections."""
        text = ircutils.stripFormatting(text)       # Strip IRC formatting from the string.
        text = text.strip()                         # Strip whitespace from beginning and the end of the string.
        if len(text) > 1:
            # So we don't get an error if the text is too small
            text = text[0].upper() + text[1:]       # Capitalize first letter of the string.
        text = utils.str.normalizeWhitespace(text)  # Normalize the whitespace in the string.
        return text

    def _processText(self, channel, text):
        match = False
        ignore = self.registryValue("ignorePattern", channel)
        strip = self.registryValue("stripPattern", channel)
        text = ircutils.stripFormatting(text)
        if self.registryValue('stripRelayedNick', channel):
            text = MATCH_MESSAGE_STRIPNICK.match(text).group('message')
        if ignore:
            match = re.search(ignore, text)
            if match:
                log.debug("Cobe: %s matches ignorePattern for %s" % (text, channel))
                return
        if strip:
            match = re.findall(strip, text)
            if match:
                for x in match:
                    text = text.replace(x, '')
                    log.debug("Cobe: %s matches stripPattern for %s. New text text: %s" % (x, channel, text))
        if self.registryValue('stripURL', channel):
            new_text = re.sub(r'(?i)\b((?:[a-z][\w-]+:(?:/{1,3}|[a-z0-9%])|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'".,<>?«»“”‘’]))', '', text)
            if new_text != text:
                log.debug("Cobe: url(s) stripped from text for %s. New text text: %s" % (channel, new_text))
                text = new_text
        text = text.strip()                         # Strip whitespace from beginning and the end of the string.
        if len(text) > 1:
            # So we don't get an error if the text is too small
            text = text[0].upper() + text[1:]       # Capitalize first letter of the string.
        text = utils.str.normalizeWhitespace(text)  # Normalize the whitespace in the string.
        if text and len(text) > 1 and not text.isspace():
            return text
        else:
            return None

    def _learn(self, irc, msg, channel, text, probability):
        """Internal method for learning phrases."""
        text = self._processText(channel, text)  # Run text ignores/strips/cleanup.
        if os.path.exists(self._getBrainDirectoryForChannel(channel)):
            # Does this channel have a directory for the brain file stored and does this file exist?
            if text:
                self.log.debug("Learning: {0}".format(text))
                cobeBrain = SQLiteBrain(self._getBrainDirectoryForChannel(channel))
                cobeBrain.learn(text)
                if random.randint(0, 10000) <= probability:
                    self._reply(irc, msg, channel, text)
        else: # Nope, let's make it!
            subprocess.getoutput('{0} {1}'.format(self._doCommand(channel), 'init'))
            if text:
                self.log.debug("Learning: {0}".format(text))
                cobeBrain = SQLiteBrain(self._getBrainDirectoryForChannel(channel))
                cobeBrain.learn(text)
                if random.randint(0, 10000) <= probability:
                    self._reply(irc, msg, channel, text)

    def _reply(self, irc, msg, channel, text):
        """Send a response to text"""
        cobeBrain = SQLiteBrain(self._getBrainDirectoryForChannel(channel))
        response = cobeBrain.reply(text)
        response = self._strip_nick(irc, msg, response)
        for i in range(response.lower().count(self.magicnick.lower())):
            # If first word is nick, switch with the callers nick.
            if self.magicnick in response:
                response = response.replace(self.magicnick, random.choice(list(irc.state.channels[msg.args[0]].users)))
            if self.magicnick.lower() in response:
                response = response.replace(self.magicnick.lower(), random.choice(list(irc.state.channels[msg.args[0]].users)))
        cobeBrain.learn(response) # Let's have the bot learn the wacky things it says
        self.log.info("Attempting to respond in {0} with message: {1}".format(channel, response))
        # delay the response here so we look real?
        if self.registryValue('responseDelay', channel):
            self.log.info("Delayed the response in %s." % channel)
            delayseconds = time.time() + random.randint(2, 5)
            schedule.addEvent(irc.queueMsg(ircmsgs.privmsg(channel, response)), delayseconds)
        else:
            irc.queueMsg(ircmsgs.privmsg(channel, response))

    def doPrivmsg(self, irc, msg):
        (channel, message) = msg.args
        if callbacks.addressed(irc.nick, msg) or ircmsgs.isCtcp(msg) or not irc.isChannel(channel) or not self.registryValue('enable', channel):
            return
        if msg.nick.lower() in self.registryValue('ignoreNicks', channel):
            log.debug("Cobe: nick %s in ignoreNicks for %s" % (msg.nick, channel))
            return
        if ircmsgs.isAction(msg):
            # If the message was an action...we'll learn it anyways!
            message = ircmsgs.unAction(msg)
        if irc.nick.lower() in message.lower():
            # Were we addressed in the channel?
            probability = self.registryValue('probabilityWhenAddressed', channel)
        else:
            # Okay, we were not addressed, but what's the probability we should reply?
            probability = self.registryValue('probability', channel)
        #if self.registryValue('stripNicks'):
        #    removenicks = '|'.join(item + '\W.*?\s' for item in irc.state.channels[channel].users)
        #    text = re.sub(r'' + removenicks + '', 'MAGIC_NICK', text)
        self._learn(irc, msg, channel, message, probability) # Now we can pass this to our learn function!

    def _makeSizePretty(self, size):
        """Internal command for making the size pretty!"""
        suffixes = [("Bytes",2**10), ("kibibytes",2**20), ("mebibytes",2**30), ("gibibytes",2**40), ("tebibytes",2**50)]
        for suf, lim in suffixes:
            if size > lim:
                continue
            else:
                return round(size/float(lim/2**10),2).__str__()+suf

    def brainsize(self, irc, msg, args, channel):
        """[<channel>]
        Prints the size of the brain on disk. If <channel> is not given, then the current channel is used.
        """
        if not channel: # Did the user enter in a channel? If not, set the currect channel
            channel = msg.args[0]
        if not irc.isChannel(channel): # Are we in a channel?
            if os.path.exists(self._getBrainDirectoryForChannel(channel)):
                # Does this channel have a brain file?
                size = float(os.path.getsize(self._getBrainDirectoryForChannel(channel)))
                irc.reply("The brain file for the channel {0} is {1}.".format(channel, self._makeSizePretty(size)))
            else: # Nope, raise error msg!
                irc.error(_("I am missing a brainfile in {0}!".format(channel)), Raise=True)
        elif os.path.exists(self._getBrainDirectoryForChannel(channel)): # We are in a channel! Does the brain file exist?
            size = float(os.path.getsize(self._getBrainDirectoryForChannel(channel)))
            irc.reply("The brain file for the channel {0} is {1}.".format(channel, self._makeSizePretty(size)))
        else:
            irc.error(_("I am missing a brainfile in {0}!".format(channel)), Raise=True)
    brainsize = wrap(brainsize, [additional('channel')])

    def teach(self, irc, msg, args, channel, text):
        """[<channel>] <text>
        Teaches the bot <text>. If the channel is not given, the current channel is used.
        """
        if not channel: # Did the user enter in a channel? If not, set the current channel
            channel = msg.args[0]
        if not irc.isChannel(msg.args[0]) and irc.isChannel(channel):
            # Are we in a channel and is the channel supplied a channel?
            if os.path.exists(self._getBrainDirectoryForChannel(channel)):
                # Does this channel have a brain file?
                text = self._cleanText(text)
                if text and len(text) > 1 and not text.isspace():
                    irc.reply("Learning text: {0}".format(text))
                    cobeBrain = SQLiteBrain(self._getBrainDirectoryForChannel(channel))
                    cobeBrain.learn(text)
                else:
                    irc.error(_("No text to learn!"), Raise=True)
            else:
                # Nope, create one!
                self.log.info("Non-existent brainfile in {0}!".format(channel))
                self.log.info("Creating a brainfile now in {0}".format(self._getBrainDirectoryForChannel(channel)))
                subprocess.getoutput('{0} {1}'.format(self._doCommand(channel), 'init'))
                text = self._cleanText(text)
                if text and len(text) > 1 and not text.isspace():
                    irc.reply("Learning text: {0}".format(text))
                    cobeBrain = SQLiteBrain(self._getBrainDirectoryForChannel(channel))
                    cobeBrain.learn(text)
        elif os.path.exists(self._getBrainDirectoryForChannel(channel)) and irc.isChannel(channel): 
            # We are in a channel! Does the brain file exist and are we supplied a channel?
            text = self._cleanText(text)
            if text and len(text) > 1 and not text.isspace():
                irc.reply("Learning text: {0}".format(text))
                cobeBrain = SQLiteBrain(self._getBrainDirectoryForChannel(channel))
                cobeBrain.learn(text)
            else:
                irc.error(_("No text to learn!"), Raise=True)
        elif not os.path.exists(self._getBrainDirectoryForChannel(channel)) and irc.isChannel(channel):
            # Nope, create one!
            self.log.info("Non-existent brainfile in {0}!".format(channel))
            self.log.info("Creating a brainfile now in {0}".format(self._getBrainDirectoryForChannel(channel)))
            subprocess.getoutput('{0} {1}'.format(self._doCommand(channel), 'init'))
            text = self._cleanText(text)
            if text and len(text) > 1 and not text.isspace():
                irc.reply("Learning text: {0}".format(text))
                cobeBrain = SQLiteBrain(self._getBrainDirectoryForChannel(channel))
                cobeBrain.learn(text)
        else:
            irc.error(_("Improper channel given!"), Raise=True)
    teach = wrap(teach, [('checkCapability', 'admin'), additional('channel'), 'text'])

    def text(self, irc, msg, args, channel, optlist, url):
        """[<channel>] [--process] <url>
        Imports text from a URL. If the channel is not given, the current channel is used. Use --process
        to process text with ignore/strip options set in plugin configs.
        """
        optlist = dict(optlist)
        lines = 0
        if 'process' in optlist:
            process = True
        else:
            process = False
        if not channel: # Did the user enter in a channel? If not, set the current channel
            channel = msg.args[0]
        if not irc.isChannel(msg.args[0]) and irc.isChannel(channel):
            # Are we in a channel and is the channel supplied a channel?
            if os.path.exists(self._getBrainDirectoryForChannel(channel)):
                # Does this channel have a brain file?
                r = requests.head(url)
                if "text/plain" in r.headers["content-type"]:
                    file = requests.get(url)
                else:
                    irc.reply("Invalid file type.", private=False, notice=False)
                    return
                text = file.content.decode().replace('\r\n','\n')
                for line in text.split('\n'):
                    if process:
                        line = self._processText(channel,line)
                    else:
                        line = self._cleanText(line)
                    if line:
                        cobeBrain = SQLiteBrain(self._getBrainDirectoryForChannel(channel))
                        cobeBrain.learn(line)
                        lines += 1
                    else:
                        continue
                irc.reply("{0} lines added to brain file for channel {1}.".format(lines, channel))
            else:
                # Nope, create one!
                self.log.info("Non-existent brainfile in {0}!".format(channel))
                self.log.info("Creating a brainfile now in {0}".format(self._getBrainDirectoryForChannel(channel)))
                subprocess.getoutput('{0} {1}'.format(self._doCommand(channel), 'init'))
                r = requests.head(url)
                if "text/plain" in r.headers["content-type"]:
                    file = requests.get(url)
                else:
                    irc.reply("Invalid file type.", private=False, notice=False)
                    return
                text = file.content.decode().replace('\r\n','\n')
                for line in text.split('\n'):
                    if process:
                        line = self._processText(channel, line)
                    else:
                        line = self._cleanText(line)
                    if line:
                        cobeBrain = SQLiteBrain(self._getBrainDirectoryForChannel(channel))
                        cobeBrain.learn(line)
                        lines += 1
                    else:
                        continue
                irc.reply("{0} lines added to brain file for channel {1}.".format(lines, channel))
        elif os.path.exists(self._getBrainDirectoryForChannel(channel)) and irc.isChannel(channel): 
            # We are in a channel! Does the brain file exist and are we supplied a channel?
            r = requests.head(url)
            if "text/plain" in r.headers["content-type"]:
                file = requests.get(url)
            else:
                irc.reply("Invalid file type.", private=False, notice=False)
                return
            text = file.content.decode().replace('\r\n','\n')
            for line in text.split('\n'):
                if process:
                    line = self._processText(channel, line)
                else:
                    line = self._cleanText(line)
                if line:
                    cobeBrain = SQLiteBrain(self._getBrainDirectoryForChannel(channel))
                    cobeBrain.learn(line)
                    lines +=1
                else:
                    continue
            irc.reply("{0} lines added to brain file for channel {1}.".format(lines, channel))
        elif not os.path.exists(self._getBrainDirectoryForChannel(channel)) and irc.isChannel(channel):
            # Nope, create one!
            self.log.info("Non-existent brainfile in {0}!".format(channel))
            self.log.info("Creating a brainfile now in {0}".format(self._getBrainDirectoryForChannel(channel)))
            subprocess.getoutput('{0} {1}'.format(self._doCommand(channel), 'init'))
            r = requests.head(url)
            if "text/plain" in r.headers["content-type"]:
                file = requests.get(url)
            else:
                irc.reply("Invalid file type.", private=False, notice=False)
                return
            text = file.content.decode().replace('\r\n','\n')
            for line in text.split('\n'):
                if process:
                    line = self._processText(channel, line)
                else:
                    line = self._cleanText(line)
                if line:
                    cobeBrain = SQLiteBrain(self._getBrainDirectoryForChannel(channel))
                    cobeBrain.learn(line)
                    lines += 1
                else:
                    continue
            irc.reply("{0} lines added to brain file for channel {1}.".format(lines, channel))
        else:
            irc.error(_("Improper channel given!"), Raise=True)
    text = wrap(text, [additional('channel'), getopts({'process':''}), 'text'])

    def respond(self, irc, msg, args, channel, text):
        """[<channel>] <text>
        Replies to <text>. If the channel is not given, the current channel is used.
        """
        if not channel: # Did the user enter in a channel? If not, set the current channel
            channel = msg.args[0]
        if not irc.isChannel(msg.args[0]) and irc.isChannel(channel):
            # Are we in a channel and is the channel supplied a channel?
            if os.path.exists(self._getBrainDirectoryForChannel(channel)):
                # Does this channel have a brain file?
                    text = self._cleanText(text)
                    if text and len(text) > 1 and not text.isspace():
                        cobeBrain = SQLiteBrain(self._getBrainDirectoryForChannel(channel))
                        response = cobeBrain.reply(text)
                        irc.reply(response)
                    else:
                        irc.error(_("No text to reply to!"), Raise=True)
            else:
                # Nope, create one!
                self.log.info("Non-existent brainfile in {0}!".format(channel))
                self.log.info("Creating a brainfile now in {0}".format(self._getBrainDirectoryForChannel(channel)))
                subprocess.getoutput('{0} {1}'.format(self._doCommand(channel), 'init'))
                text = self._cleanText(text)
                if text and len(text) > 1 and not text.isspace():
                    cobeBrain = SQLiteBrain(self._getBrainDirectoryForChannel(channel))
                    response = cobeBrain.reply(text)
                    irc.reply(response)
                else:
                    irc.error(_("No text to reply to!"), Raise=True)
        elif os.path.exists(self._getBrainDirectoryForChannel(channel)) and irc.isChannel(channel):
            # We are in a channel! Does the brain file exist and is this a channel?
            text = self._cleanText(text)
            if text and len(text) > 1 and not text.isspace():

                cobeBrain = SQLiteBrain(self._getBrainDirectoryForChannel(channel))
                response = cobeBrain.reply(text)
                irc.reply(response)

            else:
                irc.error(_("No text to reply to!"), Raise=True)
        elif not os.path.exists(self._getBrainDirectoryForChannel(channel)) and irc.isChannel(channel):
            # Nope, create one!
            self.log.info("Non-existent brainfile in {0}!".format(channel))
            self.log.info("Creating a brainfile now in {0}".format(self._getBrainDirectoryForChannel(channel)))
            subprocess.getoutput('{0} {1}'.format(self._doCommand(channel), 'init'))
            text = self._cleanText(text)
            if text and len(text) > 1 and not text.isspace():
                irc.reply("Learning text: {0}".format(text))
                cobeBrain = SQLiteBrain(self._getBrainDirectoryForChannel(channel))
                cobeBrain.learn(text)
            else:
                irc.error(_("No text to reply to!"), Raise=True)
        else:
            irc.error(_("Improper channel given!"), Raise=True)
    respond = wrap(respond, [additional('channel'), 'text'])

Class = Cobe

# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
