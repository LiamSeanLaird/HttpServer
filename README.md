# Python HTTP Server
A simple HTTP server capable of serving static files and directories.

## Managing Concurrency

Options: 
1. **Thread per request**: Create a new thread for each request.
2. **Asynchronous I/O**: Use `asyncio` to handle multiple requests concurrently.
3. **Thread pool**: Create a pool of threads to handle requests.
4. **Process pool**: Create a pool of processes to handle requests
5. **Select**: Use `selectors` module to handle multiple requests concurrently with a basic event loop.


Selectors allow us to monitor multiple I/O streams and determine which ones are ready for reading or writing. 

This project uses selectors because most network applications are I/O-bound, meaning they spend most of their time waiting for data to be sent or received over the network.