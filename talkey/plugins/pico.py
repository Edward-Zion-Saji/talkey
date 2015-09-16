import os
import re
import tempfile
import pipes
from talkey.base import AbstractTTSEngine, subprocess
from talkey.utils import check_executable, memoize

class PicoTTS(AbstractTTSEngine):
    """
    Uses the svox-pico-tts speech synthesizer
    Requires pico2wave to be available
    """

    SLUG = "pico-tts"

    @classmethod
    def get_init_options(cls):
        return {}

    @memoize
    def is_available(self):
        return check_executable('pico2wave')

    def get_options(self):
        return {}

    @memoize
    def get_languages(self, detectable=True):
        cmd = ['pico2wave', '-l', 'NULL', '-w', os.devnull]
        with tempfile.SpooledTemporaryFile() as f:
            subprocess.call(cmd, stderr=f)
            f.seek(0)
            output = f.read().decode('utf-8')
        pattern = re.compile(r'Unknown language: NULL\nValid languages:\n((?:[a-z]{2}-[A-Z]{2}\n)+)')
        matchobj = pattern.match(output)
        voices = matchobj.group(1).split()
        langs = {}
        for voice in voices:
            lang = voice[:2]
            langs.setdefault(lang, {'default': voice, 'voices': {}})
            langs[lang]['voices'][voice] = {}
        return langs

    def _say(self, phrase, language, voice, voiceinfo, options):
        self._logger.debug("Saying '%s' with '%s'", phrase, self.SLUG)
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
            fname = f.name
        cmd = ['pico2wave', '-l', voice, '-w', fname, phrase]
        self._logger.debug('Executing %s', ' '.join([pipes.quote(arg) for arg in cmd]))
        subprocess.call(cmd)
        self.play(fname)
        os.remove(fname)