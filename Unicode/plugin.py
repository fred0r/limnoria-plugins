###
# Copyright (c) 2010, Michael B. Klein
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

import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks
import unicodedata
import json
import supybot.utils.web as web
from urllib.parse import urlencode, quote

class Unicode(callbacks.Plugin):

    def unicode(self, irc, msg, args, query):
      """[character]
      Look up unicode character details
      """
      url = "http://unicodelookup.com/lookup?"
      url = url + urlencode({'q' : query, 'o' : 0})
      data = web.getUrl(url)
      try:
        data = json.loads(data)
        responses = []
        for result in data['results']:
          ucode = result[2].replace('0x','U+')
          name = unicodedata.name('{0}'.format(query))
          responses.append('%s (%s): %s [HTML: %s / Decimal: %s / Hex: %s]' % (ucode, name, result[4], result[3], result[1], result[2]))
        response = '; '.join(responses)
        irc.reply(response)
      except ValueError:
        irc.reply('No unicode characters matching /' + query + '/ found.')
    unicode = wrap(unicode, ['text'])

Class = Unicode


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
