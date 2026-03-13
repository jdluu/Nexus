"""Entry point script for the Nexus application.

Initiates the Textual application instance and executes the main event loop.
"""

from nexus.app import NexusApp

if __name__ == "__main__":
    app = NexusApp()
    app.run()
