"""Bridge for connecting a UI instance to nvim."""
from threading import Thread


class UIBridge(object):

    """UIBridge class. Connects a Nvim instance to a UI class."""

    def connect(self, nvim, ui, profile=None):
        """Connect nvim and the ui.

        This will start loops for handling the UI and nvim events while
        also synchronizing both.
        """
        self._nvim = nvim
        self._ui = ui
        self._profile = profile
        t = Thread(target=self._ui_event_loop)
        t.daemon = True
        t.start()
        self._nvim_event_loop()
        t.join()
        if self._profile:
            print(self._profile)

    def disconnect(self):
        """Disconnect by exiting nvim."""
        self._call(self._nvim.quit)

    def send_input(self, input_str):
        """Send input to nvim."""
        self._call(self._nvim.input, input_str)

    def send_resize(self, columns, rows):
        """Send a resize request to nvim."""
        self._call(self._nvim.ui_try_resize, columns, rows)

    def _call(self, fn, *args):
        self._nvim.session.threadsafe_call(fn, *args)

    def _ui_event_loop(self):
        if self._profile:
            import StringIO
            import cProfile
            import pstats
            pr = cProfile.Profile()
            pr.enable()
        self._ui.start(self)
        if self._profile:
            pr.disable()
            s = StringIO.StringIO()
            ps = pstats.Stats(pr, stream=s)
            ps.strip_dirs().sort_stats(self._profile).print_stats(30)
            self._profile = s.getvalue()

    def _nvim_event_loop(self):
        def on_setup():
            self._nvim.ui_attach(153, 39)

        def on_request(method, args):
            raise Exception('Not implemented')

        def on_notification(method, updates):
            def apply_updates(*a):
                for update in updates:
                    handler = getattr(self._ui, '_nvim_' + update[0])
                    for args in update[1:]:
                        handler(*args)
                self._ui._nvim_cursor_on()
            if method == 'redraw':
                self._ui.schedule_screen_update(apply_updates)

        self._nvim.session.run(on_request, on_notification, on_setup)
        self._ui.quit()
