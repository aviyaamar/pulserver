import logging
from server_config import ServerConfiguration
from server import Server
from reg_server import register_server


def main():
    # Initialize logging
    logging.basicConfig(level=logging.INFO)

    # Load configuration from disk
    configuration = ServerConfiguration()

    if not configuration.get_computer_key():
        # Register with server
        computer_key = register_server(configuration)

        # Set the computer key
        configuration.set_computer_key(computer_key)

    # Initialize server
    server = Server(configuration)
    server.run()


if __name__ == "__main__":
    # Im your daddyf
    main()
