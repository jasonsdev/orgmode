
import re
import sys
import subprocess
import sublime
from .abstract import AbstractRegexLinkResolver

#TODO: I'm unsure of the commands for darwin/linux. Need to test.
DEFAULT_OPEN_LINK_COMMANDS = dict(
    darwin=['open'],
    win32=['start'],
    linux=['xdg-open']
)

PATTERN_SETTING = 'orgmode.open_link.resolver.evernote.pattern'
PATTERN_DEFAULT = r'^(evernote:|en:)(?P<view_path>///view/[^/]+/[^/]+/)?(?P<note_id>[^/]+)(?P<linked_note_id>/[^/]+)?/?$'
URL_SETTING = 'orgmode.open_link.resolver.evernote.url'
URL_DEFAULT = '%s'

class Resolver(AbstractRegexLinkResolver):

    def __init__(self, view):
        super(Resolver, self).__init__(view)
        get = self.settings.get
        self.link_commands = self.settings.get(
            'orgmode.open_link.resolver.abstract.commands', DEFAULT_OPEN_LINK_COMMANDS)
        pattern = get(PATTERN_SETTING, PATTERN_DEFAULT)
        self.regex = re.compile(pattern)
        self.url = get(URL_SETTING, URL_DEFAULT)

    def replace(self, match):
        note_id = match.group('note_id')

        if match.group('view_path'):
            view_path = match.group('view_path')
        else:
            en_user_id = self.settings.get('orgmode.open_link.resolver.evernote.user_id', '')
            en_shard_id = self.settings.get('orgmode.open_link.resolver.evernote.shard_id', '')
            view_path = '///view/{0}/{1}/'.format(en_user_id, en_shard_id)

        if match.group('linked_note_id'):
            linked_note_id = match.group('linked_note_id')
        else:
            linked_note_id = '/' + match.group('note_id')     

        return self.url % 'evernote:{0}{1}{2}/'.format(view_path, note_id, linked_note_id)

    def get_link_command(self):
        platform = sys.platform
        for key, val in self.link_commands.items():
            if key in platform:
                return val
        return None
        
    def execute(self, content):
        command = self.get_link_command()
        if not command:
            sublime.error_message(
                'Could not get link opener command.\nNot yet supported.')
            return None

        if sys.version_info[0] < 3:
            content = content.encode(sys.getfilesystemencoding())

        cmd = command + [content]
        
        sublime.status_message('Executing: %s' % cmd)
        if sys.platform != 'win32':
            process = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        else:
            process = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

        stdout, stderr = process.communicate()
        if stdout:
            stdout = str(stdout, sys.getfilesystemencoding())
            sublime.status_message(stdout)
        if stderr:
            stderr = str(stderr, sys.getfilesystemencoding())
            sublime.error_message(stderr)