if __name__ == "__main__":
    try:
        from mvc.ui.widgets import Application
    except ImportError:
        from mvc.ui.console import Application
    app = Application()
    app.startup()
    app.run()
