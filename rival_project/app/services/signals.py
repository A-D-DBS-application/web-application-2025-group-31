from flask import signals

def setup_signals(app):
    @signals.request_finished.connect_via(app)
    def request_finished(sender, response, **extra):
        # Handle request finished event
        print("Request finished!")

    @signals.before_request.connect_via(app)
    def before_request(sender, **extra):
        # Handle before request event
        print("Before request!")

    @signals.after_request.connect_via(app)
    def after_request(sender, response, **extra):
        # Handle after request event
        print("After request!")
        return response

    @signals.teardown_request.connect_via(app)
    def teardown_request(sender, exception=None, **extra):
        # Handle teardown request event
        print("Teardown request!")