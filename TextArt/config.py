###
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

import supybot.conf as conf
import supybot.registry as registry

try:
    from supybot.i18n import PluginInternationalization

    _ = PluginInternationalization("TextArt")
except:
    # Placeholder that allows to run the plugin on a bot
    # without the i18n module
    _ = lambda x: x


def configure(advanced):
    # This will be called by supybot to configure this module.  advanced is
    # a bool that specifies whether the user identified themself as an advanced
    # user or not.  You should effect your configuration by manipulating the
    # registry as appropriate.
    from supybot.questions import expect, anything, something, yn

    conf.registerPlugin("TextArt", True)


TextArt = conf.registerPlugin("TextArt")

conf.registerGlobalValue(
    TextArt, "pasteAPI", registry.String("", _("""Paste.ee API Key"""), private=True)
)

conf.registerGlobalValue(
    TextArt, "imgurAPI", registry.String("", _("""Imgur Client ID"""), private=True)
)

conf.registerChannelValue(
    TextArt,
    "pasteEnable",
    registry.Boolean(False, _("""Turns on and off paste.ee support""")),
)

conf.registerChannelValue(
    TextArt,
    "showStats",
    registry.Boolean(False, _("""Turns on and off showing render stats.""")),
)

conf.registerChannelValue(
    TextArt,
    "delay",
    registry.Float(
        1.0, _("""Set the time delay betwen lines. Not currently implemented.""")
    ),
)

conf.registerChannelValue(
    TextArt,
    "quantize",
    registry.Boolean(
        False,
        _(
            """
            Enable quantizing to 256 colors before rendering. Results in much
            faster rendering at a slight decrease in quality. Default: False
            """
        ),
    ),
)

conf.registerChannelValue(
    TextArt,
    "resize",
    registry.Integer(
        3,
        _(
            """
            Set the resize algorithm. 0 = nearest, 1 = lanczos, 2 = bilinear, 3 =
            bicubic, 4 = box, 5 = hamming"""
        ),
    ),
)

conf.registerChannelValue(
    TextArt,
    "speed",
    registry.String(
        "Slow",
        _(
            """
            Set the speed of the color rendering. 'Slow' (default) to use CIEDE2000
            color difference. 'Fast' to use Euclidean color difference.
            """
        ),
    ),
)

conf.registerChannelValue(
    TextArt,
    "imgDefault",
    registry.String(
        "1/2",
        _(
            """
            Set the default art type for the img command. Options are 'ascii', '1/2'
            (default), '1/4', 'block', and 'no-color'
            """
        ),
    ),
)

conf.registerChannelValue(
    TextArt,
    "asciiWidth",
    registry.Integer(100, _("""Set the default column width for ascii art images""")),
)

conf.registerChannelValue(
    TextArt,
    "blockWidth",
    registry.Integer(
        80, _("""
        Set the default column width for 1/2 and 1/4 block art images
        """)
    ),
)

conf.registerChannelValue(
    TextArt,
    "colors",
    registry.Integer(
        99,
        _(
            """
            Set the default number of colors to use. Options are 16 for colors 0-15
            only, 83 for colors 16-98 only, and 99 (default) to use all available colors
            """
        ),
    ),
)

conf.registerChannelValue(
    TextArt,
    "fg",
    registry.Integer(
        99,
        _(
            """Set the default foreground color for ascii art images. 0-98. 
            99 is disabled (default)"""
        ),
    ),
)

conf.registerChannelValue(
    TextArt,
    "bg",
    registry.Integer(
        99,
        _(
            """
            Set the default background color for ascii art images. 0-98. 99 is disabled
            (default)"""
        ),
    ),
)

conf.registerChannelValue(
    TextArt,
    "maxLength",
    registry.Integer(
        20, _("""Set the maximum character length for text to figlet inputs""")
    ),
)

conf.registerChannelValue(
    TextArt,
    "maxWords",
    registry.Integer(
        4, _("""Set the maximum number of words for text to figlet inputs""")
    ),
)

conf.registerGlobalValue(
    TextArt,
    "userAgents",
    registry.CommaSeparatedListOfStrings(
        [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like"
            " Gecko) Chrome/79.0.3945.130 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:73.0) Gecko/20100101"
            " Firefox/73.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like"
            " Gecko) Chrome/80.0.3987.122 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:74.0) Gecko/20100101"
            " Firefox/74.0",
        ],
        _("""Reported user agent when fetching links"""),
    ),
)
